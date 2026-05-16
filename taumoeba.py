"""
taumoeba.py — Taumoeba collection, analysis and breeding lab
CPS7004 Project Hail Mary Simulation
"""

import random
from utils import (REWARD_EXPERIMENT_SUCCESS, REWARD_EXPERIMENT_PARTIAL,
                   REWARD_EXPERIMENT_FAIL, log)


class TaumoebaLab:
    """
    Manages Taumoeba sample collection, analysis, and selective breeding.
    Taumoeba is the key to saving Earth and Erid — it consumes Astrophage.
    Grace and Rocky must breed a strain that survives Earth's nitrogen atmosphere.
    Scientific integrity is maintained: all results recorded, none discarded.
    """

    def __init__(self):
        self.samples_collected      = 0
        self.experiments_run        = 0
        self.experiments_success    = 0
        self.experiments_partial    = 0
        self.experiments_failed     = 0
        self.breeding_progress      = 0.0   # 0.0 → 1.0 (viable strain)
        self.viable_strain_found    = False
        self.experiment_log         = []    # all results recorded

        # Procedural generation — mutation rate varies each run
        self.mutation_rate          = round(random.uniform(0.1, 0.9), 2)
        self.earth_compatibility    = 0.0   # increases with successful breeding

    # ── Sample collection ────────────────────────────────────────

    def collect_sample(self, agent):
        """Grace collects a Taumoeba sample from Adrian's atmosphere."""
        self.samples_collected += 1
        agent.record_reward('sample', 5)
        log(f"{agent.name} collected Taumoeba sample #{self.samples_collected}")
        return True

    # ── Experimentation ──────────────────────────────────────────

    def run_experiment(self, agent, rocky_assisting=False):
        """
        Run a breeding experiment. Rocky's assistance improves success probability.
        Outcomes: success / partial success / failure — all recorded.
        Returns the reward value for reinforcement learning.
        """
        if self.samples_collected == 0:
            log("No samples available — experiment cannot proceed.")
            return REWARD_EXPERIMENT_FAIL

        self.experiments_run += 1

        # Base success probability — improved by Rocky's knowledge sharing
        base_prob      = 0.35 + (0.15 if rocky_assisting else 0.0)
        partial_prob   = 0.30
        mutation_bonus = self.mutation_rate * 0.1

        roll = random.random()

        if roll < base_prob + mutation_bonus:
            # Success
            outcome = 'success'
            self.experiments_success += 1
            self.breeding_progress = min(1.0, self.breeding_progress + random.uniform(0.08, 0.15))
            self.earth_compatibility = min(1.0, self.earth_compatibility + 0.05)
            reward = REWARD_EXPERIMENT_SUCCESS
            log(f"Experiment #{self.experiments_run} — SUCCESS | "
                f"Breeding progress: {self.breeding_progress:.2f}")

        elif roll < base_prob + mutation_bonus + partial_prob:
            # Partial success
            outcome = 'partial'
            self.experiments_partial += 1
            self.breeding_progress = min(1.0, self.breeding_progress + random.uniform(0.02, 0.06))
            reward = REWARD_EXPERIMENT_PARTIAL
            log(f"Experiment #{self.experiments_run} — PARTIAL | "
                f"Breeding progress: {self.breeding_progress:.2f}")

        else:
            # Failure — recorded and learned from, not discarded
            outcome = 'failure'
            self.experiments_failed += 1
            reward = REWARD_EXPERIMENT_FAIL
            log(f"Experiment #{self.experiments_run} — FAILED | "
                f"Result recorded for learning.")

        # Record result — scientific integrity maintained
        self.experiment_log.append({
            'experiment_number': self.experiments_run,
            'outcome':           outcome,
            'breeding_progress': round(self.breeding_progress, 3),
            'rocky_assisted':    rocky_assisting,
            'mutation_rate':     self.mutation_rate,
        })

        # Update agent reward memory
        agent.record_reward('experiment', reward)

        # Adjust mutation rate dynamically (procedural generation)
        self.mutation_rate = round(
            min(0.95, max(0.05, self.mutation_rate + random.uniform(-0.05, 0.05))), 2
        )

        # Check if viable strain achieved
        if self.breeding_progress >= 1.0 and not self.viable_strain_found:
            self.viable_strain_found = True
            log("*** VIABLE TAUMOEBA STRAIN ACHIEVED — Earth can be saved! ***")

        return reward

    # ── Stats ────────────────────────────────────────────────────

    def success_rate(self):
        if self.experiments_run == 0:
            return 0.0
        return round(self.experiments_success / self.experiments_run, 3)

    def stats(self):
        return {
            'samples_collected':   self.samples_collected,
            'experiments_run':     self.experiments_run,
            'experiments_success': self.experiments_success,
            'experiments_partial': self.experiments_partial,
            'experiments_failed':  self.experiments_failed,
            'success_rate':        self.success_rate(),
            'breeding_progress':   round(self.breeding_progress, 3),
            'viable_strain_found': self.viable_strain_found,
            'mutation_rate':       self.mutation_rate,
        }
