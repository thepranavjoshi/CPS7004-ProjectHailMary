"""
agent.py — Base Agent class for all simulation agents
CPS7004 Project Hail Mary Simulation
"""

from utils import clamp, wrap, GRID_SIZE


class Agent:
    """
    Abstract base class for all agents in the simulation.
    Provides shared attributes: health, energy, position, knowledge score.
    All specific agents (Grace, Rocky, Beetle) inherit from this class.
    """

    def __init__(self, name, row, col, health=100, energy=100):
        self.name     = name
        self.row      = row
        self.col      = col
        self.health   = health
        self.energy   = energy
        self.alive    = True
        self.turn     = 0

        # Reinforcement learning — action reward tracking
        self.action_rewards = {
            'experiment': [],
            'repair':     [],
            'sample':     [],
            'move':       [],
            'communicate':[],
            'rest':       [],
        }

    # ── Position ─────────────────────────────────────────────────

    @property
    def pos(self):
        return (self.row, self.col)

    def move_to(self, row, col):
        self.row = wrap(row, GRID_SIZE)
        self.col = wrap(col, GRID_SIZE)

    # ── Resource management ──────────────────────────────────────

    def deplete_energy(self, amount):
        self.energy = clamp(self.energy - amount, 0, 100)
        if self.energy <= 0:
            self.alive = False

    def restore_energy(self, amount):
        self.energy = clamp(self.energy + amount, 0, 100)

    def deplete_health(self, amount):
        self.health = clamp(self.health - amount, 0, 100)
        if self.health <= 0:
            self.alive = False

    def restore_health(self, amount):
        self.health = clamp(self.health + amount, 0, 100)

    # ── Reinforcement learning ───────────────────────────────────

    def record_reward(self, action, reward):
        if action in self.action_rewards:
            self.action_rewards[action].append(reward)

    def average_reward(self, action):
        rewards = self.action_rewards.get(action, [])
        if not rewards:
            return 0.0
        return sum(rewards) / len(rewards)

    def best_action(self, candidates):
        """
        Given a list of candidate action names, return the one
        with the highest average historical reward.
        Used for reinforcement-based decision making.
        """
        return max(candidates, key=lambda a: self.average_reward(a))

    # ── Status ───────────────────────────────────────────────────

    def is_critical(self):
        return self.energy < 20 or self.health < 20

    def status(self):
        return (f"{self.name} | HP:{self.health:3d} | "
                f"EN:{self.energy:3d} | "
                f"Pos:({self.row:2d},{self.col:2d}) | "
                f"Alive:{self.alive}")

    def __repr__(self):
        return self.status()
