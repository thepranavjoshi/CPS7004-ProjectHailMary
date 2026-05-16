"""
astrophage.py — Astrophage threat system
CPS7004 Project Hail Mary Simulation
"""

import random
from utils import (ASTROPHAGE_DRAIN, RADIATION_DRAIN, DEBRIS_DRAIN,
                   ASTROPHAGE, RADIATION, DEBRIS, TIME_DILATION, log)


class AstrophageSystem:
    """
    Manages the Astrophage threat across the simulation.
    Tracks spread, intensity, resistance, and energy drain on agents.
    Astrophage adapts — gaining resistance when Taumoeba is deployed.
    """

    def __init__(self):
        self.total_spread_events  = 0
        self.taumoeba_deployed    = False
        self.resistance_level     = 0.0   # increases as Taumoeba is used
        self.turn                 = 0

        # Procedural generation parameters (vary each simulation run)
        self.base_spread_rate     = round(random.uniform(0.05, 0.12), 3)
        self.base_drain_variance  = random.randint(1, 4)

    # ── Per-turn update ──────────────────────────────────────────

    def update(self, environment):
        """
        Called every simulation turn.
        Spreads Astrophage and evolves hazard intensity procedurally.
        """
        self.turn += 1
        environment.spread_astrophage(taumoeba_deployed=self.taumoeba_deployed)
        self.total_spread_events += 1

        # Every 10 turns, randomly intensify some existing Astrophage cells
        if self.turn % 10 == 0:
            self._intensify(environment)

    def _intensify(self, environment):
        """Randomly boost intensity of existing Astrophage cells."""
        boosted = 0
        for r in range(environment.size):
            for c in range(environment.size):
                if environment.grid[r][c] == ASTROPHAGE:
                    if random.random() < 0.15:
                        environment.astrophage_intensity[r][c] = min(
                            1.0,
                            environment.astrophage_intensity[r][c] + random.uniform(0.05, 0.15)
                        )
                        boosted += 1

    # ── Taumoeba response ────────────────────────────────────────

    def notify_taumoeba_deployed(self):
        """
        When Taumoeba is deployed, Astrophage adapts:
        - resistance increases
        - spread rate increases
        This models the adaptive resistance described in the brief.
        """
        self.taumoeba_deployed  = True
        self.resistance_level   = min(1.0, self.resistance_level + 0.1)
        self.base_spread_rate   = min(0.25, self.base_spread_rate + 0.02)
        log(f"Astrophage adapts! Resistance: {self.resistance_level:.2f} | "
            f"Spread rate: {self.base_spread_rate:.3f}")

    # ── Agent drain ──────────────────────────────────────────────

    def apply_cell_effects(self, agent, cell_type, intensity=0.0):
        """
        Apply energy/health drain to an agent based on the cell they occupy.
        Intensity scales the Astrophage drain.
        """
        if cell_type == ASTROPHAGE:
            drain = int(ASTROPHAGE_DRAIN * (1 + intensity) + self.base_drain_variance)
            agent.deplete_energy(drain)
            agent.deplete_health(int(drain * 0.5))
            log(f"{agent.name} in Astrophage cloud — energy -{drain}")

        elif cell_type == RADIATION:
            agent.deplete_energy(RADIATION_DRAIN)
            agent.deplete_health(int(RADIATION_DRAIN * 0.7))
            log(f"{agent.name} in radiation zone — energy -{RADIATION_DRAIN}")

        elif cell_type == DEBRIS:
            agent.deplete_energy(DEBRIS_DRAIN)
            agent.deplete_health(int(DEBRIS_DRAIN * 0.3))
            log(f"{agent.name} in debris field — energy -{DEBRIS_DRAIN}")

        elif cell_type == TIME_DILATION:
            # Time dilation slows the agent — costs extra energy
            agent.deplete_energy(6)
            log(f"{agent.name} in time-dilation zone — energy -6")

    # ── Stats ────────────────────────────────────────────────────

    def stats(self):
        return {
            'total_spread_events': self.total_spread_events,
            'resistance_level':    round(self.resistance_level, 3),
            'spread_rate':         round(self.base_spread_rate, 3),
            'taumoeba_deployed':   self.taumoeba_deployed,
        }
