"""
rocky.py — Rocky (Eridian alien) agent
CPS7004 Project Hail Mary Simulation
"""

import random
from agent import Agent
from utils import (ENERGY_REPAIR, ENERGY_COMMUNICATE, REWARD_REPAIR,
                   ASTROPHAGE, RADIATION, DEBRIS, clamp, log)


class RockyAgent(Agent):
    """
    Rocky is an Eridian — a five-limbed alien that breathes ammonia
    at high pressure. Cannot enter Grace's oxygen environment without
    the pressurised xenonite tunnel. Communicates via sonar chord patterns.
    Rocky's home star (40 Eridani) is also threatened by Astrophage,
    giving him aligned but not identical goals to Grace.
    """

    def __init__(self, row, col):
        super().__init__('Rocky', row, col, health=100, energy=100)

        # Rocky-specific attributes
        self.engineering_skill   = round(random.uniform(0.6, 1.0), 2)
        self.translation_level   = 0.0    # grows as Grace and Rocky communicate
        self.fuel_reserves       = 100    # Astrophage fuel Rocky can share
        self.cooperation_trust   = 0.5    # affects knowledge sharing quality
        self.repairs_completed   = 0
        self.knowledge_shared    = 0
        self.fuel_transferred    = 0
        self.xenonite_materials  = 100   # xenonite for repairs and tunnel maintenance

        # Sonar chord communication system
        self.chord_vocabulary    = {}     # maps concepts to chord patterns
        self.known_concepts      = 0

        # Strategy state for emergent behaviour
        self.strategy            = 'exploration'  # exploration/research/survival/emergency

    # ── Strategy selection ───────────────────────────────────────

    def update_strategy(self, environment, grace):
        """
        Rocky adapts strategy based on current conditions.
        Implements multi-agent coordination mechanism.
        """
        astrophage_cells = environment.count_astrophage_cells()
        total_cells      = environment.size ** 2

        if self.energy < 20 or self.health < 20:
            self.strategy = 'emergency'
        elif grace.energy < 25:
            self.strategy = 'survival'
        elif astrophage_cells / total_cells > 0.3:
            self.strategy = 'research'
        else:
            self.strategy = 'exploration'

    # ── Actions ──────────────────────────────────────────────────

    def choose_action(self, environment, grace):
        """
        Rocky chooses action based on current strategy and
        reinforcement learning reward history.
        """
        self.update_strategy(environment, grace)

        if self.strategy == 'emergency':
            return self.rest()

        if self.strategy == 'survival':
            return self.transfer_fuel(grace)

        if self.strategy == 'research':
            candidates = ['experiment', 'communicate', 'repair']
            best = self.best_action(candidates)
            if best == 'repair':
                return self.repair(grace)
            elif best == 'communicate':
                return self.share_knowledge(grace)
            else:
                return self.assist_experiment(grace)

        # Exploration
        candidates = ['communicate', 'repair', 'experiment']
        best = self.best_action(candidates)
        if best == 'repair':
            return self.repair(grace)
        elif best == 'communicate':
            return self.share_knowledge(grace)
        else:
            return self.assist_experiment(grace)

    def repair(self, grace):
        """
        Rocky performs engineering repairs that Grace cannot do alone.
        Restores Grace's energy systems.
        """
        if self.energy < ENERGY_REPAIR:
            log("Rocky: insufficient energy to repair.")
            return False

        self.deplete_energy(ENERGY_REPAIR)
        repair_amount = int(15 * self.engineering_skill)
        grace.restore_energy(repair_amount)
        grace.restore_health(int(repair_amount * 0.5))
        self.repairs_completed += 1
        self.xenonite_materials  = max(0, self.xenonite_materials - 5)
        if self.xenonite_materials == 0:
            log("Rocky: xenonite materials exhausted — repairs compromised.")
        self.record_reward('repair', REWARD_REPAIR)
        log(f"Rocky repairs systems — Grace energy +{repair_amount} | "
            f"Engineering skill: {self.engineering_skill:.2f}")
        return True

    def share_knowledge(self, grace):
        """
        Rocky shares scientific knowledge via sonar chord patterns.
        Progressive translation system — improves over time.
        Boosts Grace's knowledge score proportionally to translation level.
        """
        if self.energy < ENERGY_COMMUNICATE:
            return False

        self.deplete_energy(ENERGY_COMMUNICATE)

        # Translation improves with each communication exchange
        self.translation_level = min(1.0, self.translation_level + random.uniform(0.02, 0.06))
        self.cooperation_trust = min(1.0, self.cooperation_trust + 0.02)

        # Knowledge transferred scales with translation level
        knowledge_gain = int(5 * self.translation_level * self.cooperation_trust)
        grace.knowledge_score = clamp(grace.knowledge_score + knowledge_gain, 0, 200)
        self.knowledge_shared += knowledge_gain
        self.known_concepts   += 1

        # Build chord vocabulary entry
        chord = f"chord_{self.known_concepts}"
        self.chord_vocabulary[chord] = f"concept_{self.known_concepts}"

        self.record_reward('communicate', knowledge_gain * 0.5)
        log(f"Rocky shares knowledge via chord '{chord}' — "
            f"Grace knowledge +{knowledge_gain} | "
            f"Translation level: {self.translation_level:.2f}")
        return True

    def assist_experiment(self, grace):
        """
        Rocky assists Grace's Taumoeba experiments with Eridian science data.
        Sets a flag that TaumoebaLab uses to boost success probability.
        """
        self.deplete_energy(ENERGY_COMMUNICATE)
        grace.rocky_assisting = True
        log(f"Rocky assists experiment — success probability boosted.")
        self.record_reward('experiment', 4)
        return True

    def transfer_fuel(self, grace):
        """
        Rocky shares Astrophage fuel reserves with Grace's ship.
        """
        if self.fuel_reserves <= 0:
            log("Rocky: no fuel reserves remaining.")
            return False

        transfer = min(20, self.fuel_reserves)
        self.fuel_reserves -= transfer
        grace.restore_energy(transfer)
        self.fuel_transferred += transfer
        log(f"Rocky transfers {transfer} fuel units to Grace — "
            f"Rocky fuel remaining: {self.fuel_reserves}")
        return True

    def rest(self):
        """Rocky rests to recover energy."""
        from utils import ENERGY_REST_GAIN
        self.restore_energy(ENERGY_REST_GAIN)
        self.record_reward('rest', 1)
        log(f"Rocky rests — energy restored to {self.energy}")
        return True

    def scan_hazards(self, environment):
        """
        Rocky scans surrounding cells and reports hazard locations.
        Returns list of hazardous adjacent cells.
        """
        hazards = []
        for dr in range(-3, 4):
            for dc in range(-3, 4):
                from utils import wrap
                r = wrap(self.row + dr)
                c = wrap(self.col + dc)
                if environment.grid[r][c] in [ASTROPHAGE, RADIATION, DEBRIS]:
                    hazards.append((r, c, environment.grid[r][c]))
        return hazards

    # ── Stats ────────────────────────────────────────────────────

    def stats(self):
        return {
            'health':            self.health,
            'energy':            self.energy,
            'engineering_skill': self.engineering_skill,
            'translation_level': round(self.translation_level, 3),
            'cooperation_trust': round(self.cooperation_trust, 3),
            'fuel_reserves':     self.fuel_reserves,
            'repairs_completed': self.repairs_completed,
            'xenonite_materials': self.xenonite_materials,
            'knowledge_shared':  self.knowledge_shared,
            'fuel_transferred':  self.fuel_transferred,
            'strategy':          self.strategy,
        }
