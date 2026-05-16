"""
grace.py — Dr. Ryland Grace agent (central human agent)
CPS7004 Project Hail Mary Simulation
"""

import random
from agent import Agent
from utils import (ENERGY_MOVE, ENERGY_EXPERIMENT, ENERGY_EVA,
                   ENERGY_TUNNEL, ENERGY_DEPLOY_BEETLE, ENERGY_REST_GAIN,
                   KNOWLEDGE_FLASHBACK_1, KNOWLEDGE_FLASHBACK_2,
                   KNOWLEDGE_FLASHBACK_3, KNOWLEDGE_WIN,
                   ASTROPHAGE, RADIATION, DEBRIS, TUNNEL,
                   REWARD_SAMPLE_COLLECTED, clamp, wrap, log)


class GraceAgent(Agent):
    """
    Dr. Ryland Grace — central agent of the simulation.
    Wakes from a coma with no memory. Progressively regains knowledge
    through flashback events triggered by discoveries.
    Can move, experiment, collect samples, deploy beetles, repair,
    rest, communicate with Rocky, and travel via the xenonite tunnel.
    """

    def __init__(self, row, col):
        super().__init__('Grace', row, col, health=100, energy=100)

        # Grace-specific attributes
        self.knowledge_score     = 0
        self.sample_inventory    = 0
        self.mission_complete    = False
        self.rocky_assisting     = False

        # Flashback tracking
        self.flashbacks_triggered = []
        self.flashback_events = {
            KNOWLEDGE_FLASHBACK_1: "Flashback: Eva Stratt recruits Grace for the mission.",
            KNOWLEDGE_FLASHBACK_2: "Flashback: The Hail Mary launches — Earth's last hope.",
            KNOWLEDGE_FLASHBACK_3: "Flashback: Grace understands the Astrophage threat fully.",
        }

        # Mission protocol flags
        self.protocol_violations = 0
        self.beetles_deployed    = 0

        # Strategy state for emergent behaviour
        self.strategy = 'exploration'

    # ── Strategy selection ───────────────────────────────────────

    def update_strategy(self, environment, astrophage_system):
        """
        Grace adapts strategy in real time based on conditions.
        Implements multi-agent coordination and emergent behaviour.
        """
        astrophage_cells = environment.count_astrophage_cells()
        total_cells      = environment.size ** 2
        spread_ratio     = astrophage_cells / total_cells

        if self.energy < 20 or self.health < 20:
            self.strategy = 'emergency'
        elif spread_ratio > 0.35:
            self.strategy = 'research'
        elif self.knowledge_score > 60:
            self.strategy = 'research'
        else:
            self.strategy = 'exploration'

    # ── Actions ──────────────────────────────────────────────────

    def choose_action(self, environment, taumoeba_lab,
                      beetle_fleet, astrophage_system, rocky):
        """
        Grace selects action based on strategy and reinforcement learning.
        Coordinates with Rocky for joint decision making.
        """
        self.update_strategy(environment, astrophage_system)

        if self.strategy == 'emergency':
            return self.rest()

        if self.strategy == 'survival':
            return self.rest()

        if self.strategy == 'research':
            candidates = ['experiment', 'sample', 'communicate']
            best = self.best_action(candidates)
            if best == 'sample' and self._near_adrian(environment):
                return self.collect_sample(taumoeba_lab)
            elif best == 'experiment' and taumoeba_lab.samples_collected > 0:
                return self.run_experiment(taumoeba_lab)
            else:
                return self.communicate(rocky)

        # Exploration strategy
        if self._near_adrian(environment) and self.sample_inventory < 5:
            return self.collect_sample(taumoeba_lab)

        if taumoeba_lab.samples_collected > 0 and random.random() < 0.4:
            return self.run_experiment(taumoeba_lab)

        if (self.knowledge_score >= 40 and
                beetle_fleet.deployed_count < 4 and
                random.random() < 0.15):
            return self.deploy_beetle(beetle_fleet)

        candidates = ['move', 'experiment', 'sample', 'rest']
        best = self.best_action(candidates)

        if best == 'rest' or self.energy < 30:
            return self.rest()
        elif best == 'experiment' and taumoeba_lab.samples_collected > 0:
            return self.run_experiment(taumoeba_lab)
        else:
            return self.move(environment)

    def move(self, environment):
        """Move Grace to an adjacent cell. Costs energy."""
        if self.energy < ENERGY_MOVE:
            return self.rest()

        # Move toward Adrian if no samples, else explore
        if self.sample_inventory < 3:
            target = environment.adrian_pos
            dr = 0 if self.row == target[0] else (1 if target[0] > self.row else -1)
            dc = 0 if self.col == target[1] else (1 if target[1] > self.col else -1)
        else:
            dr, dc = random.choice([(-1,0),(1,0),(0,-1),(0,1)])

        new_row = wrap(self.row + dr)
        new_col = wrap(self.col + dc)
        self.move_to(new_row, new_col)
        self.deplete_energy(ENERGY_MOVE)
        self.record_reward('move', -1)
        return True

    def collect_sample(self, taumoeba_lab):
        """Collect Taumoeba sample from Adrian's atmosphere."""
        if self.energy < ENERGY_EVA:
            log("Grace: insufficient energy for EVA sample collection.")
            return self.rest()

        self.deplete_energy(ENERGY_EVA)
        self.sample_inventory += 1
        taumoeba_lab.collect_sample(self)
        self.record_reward('sample', REWARD_SAMPLE_COLLECTED)
        self.knowledge_score = clamp(self.knowledge_score + 3, 0, 200)
        self._check_flashbacks()
        return True

    def run_experiment(self, taumoeba_lab):
        """Run a Taumoeba breeding experiment."""
        if self.energy < ENERGY_EXPERIMENT:
            return self.rest()

        self.deplete_energy(ENERGY_EXPERIMENT)
        reward = taumoeba_lab.run_experiment(self, rocky_assisting=self.rocky_assisting)
        self.rocky_assisting = False

        # Knowledge gained from experiment
        if reward > 0:
            self.knowledge_score = clamp(self.knowledge_score + reward, 0, 200)
        self._check_flashbacks()
        self._check_mission_complete(taumoeba_lab)
        return True

    def deploy_beetle(self, beetle_fleet):
        """Deploy a beetle probe with current knowledge payload."""
        if self.energy < ENERGY_DEPLOY_BEETLE:
            return self.rest()

        self.deplete_energy(ENERGY_DEPLOY_BEETLE)
        success = beetle_fleet.deploy_next(self, self.knowledge_score)
        if success:
            self.beetles_deployed += 1
            self.record_reward('experiment', 15)
            log(f"Grace deploys beetle #{self.beetles_deployed}")
        return success

    def travel_tunnel(self, rocky):
        """Travel via xenonite tunnel to Rocky's ship."""
        if self.energy < ENERGY_TUNNEL:
            return False
        self.deplete_energy(ENERGY_TUNNEL)
        log(f"Grace travels through xenonite tunnel to Rocky's ship.")
        return True

    def communicate(self, rocky):
        """Grace initiates communication with Rocky."""
        if self.energy < 3:
            return False
        self.deplete_energy(3)
        rocky.share_knowledge(self)
        self.record_reward('communicate', 2)
        return True

    def rest(self):
        """Grace rests to recover energy."""
        self.restore_energy(ENERGY_REST_GAIN)
        self.restore_health(5)
        self.record_reward('rest', 1)
        log(f"Grace rests — energy: {self.energy} | health: {self.health}")
        return True

    # ── Flashback system ─────────────────────────────────────────

    def _check_flashbacks(self):
        """Trigger flashback events at knowledge milestones."""
        for threshold, message in self.flashback_events.items():
            if (self.knowledge_score >= threshold and
                    threshold not in self.flashbacks_triggered):
                self.flashbacks_triggered.append(threshold)
                log(f"*** FLASHBACK TRIGGERED *** {message}")

    # ── Mission checks ───────────────────────────────────────────

    def _near_adrian(self, environment):
        """Check if Grace is within range of Adrian's atmosphere."""
        adrian = environment.adrian_pos
        return (abs(self.row - adrian[0]) <= 3 and
                abs(self.col - adrian[1]) <= 3)

    def _check_mission_complete(self, taumoeba_lab):
        if (taumoeba_lab.viable_strain_found and
                self.knowledge_score >= KNOWLEDGE_WIN):
            self.mission_complete = True
            log("*** MISSION COMPLETE — Grace has saved Earth! ***")

    # ── Stats ────────────────────────────────────────────────────

    def stats(self):
        return {
            'health':             self.health,
            'energy':             self.energy,
            'knowledge_score':    self.knowledge_score,
            'sample_inventory':   self.sample_inventory,
            'beetles_deployed':   self.beetles_deployed,
            'flashbacks':         len(self.flashbacks_triggered),
            'mission_complete':   self.mission_complete,
            'strategy':           self.strategy,
            'alive':              self.alive,
        }
