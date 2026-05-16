"""
beetle.py — Autonomous Beetle probe agents
CPS7004 Project Hail Mary Simulation
"""

import random
from agent import Agent
from utils import (ENERGY_MOVE, REWARD_BEETLE_DEPLOYED, wrap, log)


class BeetleProbe(Agent):
    """
    Autonomous data-relay drone deployed by Grace to transmit
    findings back to Earth. Four probes: John, Paul, George, Ringo.
    Each beetle navigates using stellar positioning and carries
    a data payload configured by Grace before deployment.
    """

    def __init__(self, name, row, col, knowledge_payload=0):
        super().__init__(name, row, col, health=100, energy=100)
        self.knowledge_payload  = knowledge_payload
        self.deployed           = False
        self.reached_earth      = False
        self.steps_travelled    = 0
        self.target_row         = 0   # Earth direction: top-left corner
        self.target_col         = 0

    # ── Deployment ───────────────────────────────────────────────

    def deploy(self, from_agent):
        """
        Deploy this beetle from Grace's position.
        Costs Grace energy. Records reward for reinforcement learning.
        """
        self.deployed  = True
        self.row       = from_agent.row
        self.col       = from_agent.col
        from_agent.record_reward('experiment', REWARD_BEETLE_DEPLOYED)
        log(f"Beetle '{self.name}' deployed from ({self.row},{self.col}) "
            f"with payload: {self.knowledge_payload} knowledge points")

    # ── Autonomous navigation ────────────────────────────────────

    def step(self, environment):
        """
        Each turn, beetle moves autonomously toward Earth (0,0).
        Uses stellar positioning — moves toward target coordinates.
        Drains energy with each step.
        """
        if not self.deployed or self.reached_earth or not self.alive:
            return

        self.steps_travelled += 1

        # Move toward target (stellar positioning)
        dr = 0 if self.row == self.target_row else (-1 if self.row > self.target_row else 1)
        dc = 0 if self.col == self.target_col else (-1 if self.col > self.target_col else 1)

        # Occasionally deviate slightly (simulate space navigation uncertainty)
        if random.random() < 0.1:
            dr, dc = random.choice([(-1,0),(1,0),(0,-1),(0,1)])

        self.row = wrap(self.row + dr)
        self.col = wrap(self.col + dc)
        self.deplete_energy(ENERGY_MOVE)

        # Check if reached Earth coordinates
        if self.row == self.target_row and self.col == self.target_col:
            self.reached_earth = True
            log(f"Beetle '{self.name}' reached Earth! "
                f"Payload of {self.knowledge_payload} knowledge points delivered.")

    # ── Stats ────────────────────────────────────────────────────

    def stats(self):
        return {
            'name':              self.name,
            'deployed':          self.deployed,
            'reached_earth':     self.reached_earth,
            'steps_travelled':   self.steps_travelled,
            'knowledge_payload': self.knowledge_payload,
            'energy_remaining':  self.energy,
        }


class BeetleFleet:
    """
    Manages all four beetle probes: John, Paul, George, Ringo.
    Tracks deployment status and mission contribution score.
    """

    NAMES = ['John', 'Paul', 'George', 'Ringo']

    def __init__(self, hail_mary_pos):
        r, c = hail_mary_pos
        self.probes = [
            BeetleProbe(name, r, c) for name in self.NAMES
        ]
        self.deployed_count = 0

    def get_available(self):
        """Return first undeployed beetle."""
        for probe in self.probes:
            if not probe.deployed:
                return probe
        return None

    def deploy_next(self, grace, knowledge_score):
        """Deploy the next available beetle with Grace's current knowledge payload."""
        probe = self.get_available()
        if probe is None:
            log("All beetle probes already deployed.")
            return False
        probe.knowledge_payload = knowledge_score
        probe.deploy(grace)
        self.deployed_count += 1
        return True

    def step_all(self, environment):
        """Move all deployed beetles one step."""
        for probe in self.probes:
            if probe.deployed:
                probe.step(environment)

    def probes_reached_earth(self):
        return sum(1 for p in self.probes if p.reached_earth)

    def mission_score_contribution(self):
        return sum(p.knowledge_payload for p in self.probes if p.reached_earth)

    def stats(self):
        return [p.stats() for p in self.probes]
