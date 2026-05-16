"""
simulation.py — Main simulation controller
CPS7004 Project Hail Mary Simulation
"""

import random
from environment import EnvironmentGrid
from grace import GraceAgent
from rocky import RockyAgent
from astrophage import AstrophageSystem
from taumoeba import TaumoebaLab
from beetle import BeetleFleet
from utils import (ASTROPHAGE, RADIATION, DEBRIS, TIME_DILATION,
                   TUNNEL, HAIL_MARY, BLIP_A, log)


class Simulation:
    """
    Master controller for one complete simulation run.
    Manages turn-by-turn execution of all agents and systems.
    Tracks all metrics for analytics and graphing.
    """

    MAX_TURNS = 200

    def __init__(self, run_id=1, verbose=False):
        self.run_id      = run_id
        self.verbose     = verbose
        self.turn        = 0
        self.ended       = False
        self.end_reason  = ''

        # Initialise all systems
        self.environment     = EnvironmentGrid()
        self.grace           = GraceAgent(*self.environment.hail_mary_pos)
        self.rocky           = RockyAgent(*self.environment.blip_a_pos)
        self.astrophage_sys  = AstrophageSystem()
        self.taumoeba_lab    = TaumoebaLab()
        self.beetle_fleet    = BeetleFleet(self.environment.hail_mary_pos)

        # Metrics tracked per turn for graphing
        self.history = {
            'turn':                [],
            'grace_energy':        [],
            'grace_health':        [],
            'grace_knowledge':     [],
            'rocky_energy':        [],
            'astrophage_cells':    [],
            'breeding_progress':   [],
            'beetles_deployed':    [],
            'experiment_success':  [],
        }

    # ── Main run loop ────────────────────────────────────────────

    def run(self):
        """Execute the full simulation until end condition is met."""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"  RUN {self.run_id} STARTING")
            print(f"{'='*60}")

        while not self.ended and self.turn < self.MAX_TURNS:
            self.turn += 1
            self._execute_turn()
            self._record_history()
            self._check_end_conditions()

            if self.verbose and self.turn % 20 == 0:
                self._print_status()

        if self.verbose:
            print(f"\n  Run {self.run_id} ended after {self.turn} turns.")
            print(f"  Reason: {self.end_reason}")
            print(f"  Knowledge: {self.grace.knowledge_score} | "
                  f"Beetles: {self.beetle_fleet.deployed_count} | "
                  f"Viable strain: {self.taumoeba_lab.viable_strain_found}")

        return self._compile_results()

    # ── Turn execution ───────────────────────────────────────────

    def _execute_turn(self):
        """Execute one full simulation turn."""

        # 1. Grace chooses and executes action
        if self.grace.alive:
            self.grace.choose_action(
                self.environment,
                self.taumoeba_lab,
                self.beetle_fleet,
                self.astrophage_sys,
                self.rocky
            )
            self._apply_cell_effects(self.grace)

        # 2. Rocky chooses and executes action
        if self.rocky.alive:
            self.rocky.choose_action(self.environment, self.grace)
            self._apply_cell_effects(self.rocky)

        # 3. Beetle probes move autonomously
        self.beetle_fleet.step_all(self.environment)

        # 4. Astrophage spreads and evolves
        taumoeba_active = self.taumoeba_lab.viable_strain_found
        if taumoeba_active:
            self.astrophage_sys.notify_taumoeba_deployed()
        self.astrophage_sys.update(self.environment)

    def _apply_cell_effects(self, agent):
        """Apply hazard effects based on agent's current cell."""
        cell = self.environment.get_cell(agent.row, agent.col)
        intensity = self.environment.get_intensity(agent.row, agent.col)
        self.astrophage_sys.apply_cell_effects(agent, cell, intensity)

    # ── History recording ────────────────────────────────────────

    def _record_history(self):
        self.history['turn'].append(self.turn)
        self.history['grace_energy'].append(self.grace.energy)
        self.history['grace_health'].append(self.grace.health)
        self.history['grace_knowledge'].append(self.grace.knowledge_score)
        self.history['rocky_energy'].append(self.rocky.energy)
        self.history['astrophage_cells'].append(
            self.environment.count_astrophage_cells())
        self.history['breeding_progress'].append(
            self.taumoeba_lab.breeding_progress)
        self.history['beetles_deployed'].append(
            self.beetle_fleet.deployed_count)
        self.history['experiment_success'].append(
            self.taumoeba_lab.experiments_success)

    # ── End conditions ───────────────────────────────────────────

    def _check_end_conditions(self):
        if self.grace.mission_complete:
            self.ended     = True
            self.end_reason = 'Mission Complete — Earth saved!'

        elif not self.grace.alive:
            self.ended     = True
            self.end_reason = 'Mission Abort — Grace ran out of energy/health.'

        elif self.turn >= self.MAX_TURNS:
            self.ended     = True
            self.end_reason = 'Time limit reached.'

    # ── Status display ───────────────────────────────────────────

    def _print_status(self):
        print(f"\n  Turn {self.turn:3d} | {self.grace.status()}")
        print(f"         | {self.rocky.status()}")
        print(f"         | Knowledge: {self.grace.knowledge_score:3d} | "
              f"Breeding: {self.taumoeba_lab.breeding_progress:.2f} | "
              f"Beetles: {self.beetle_fleet.deployed_count} | "
              f"Astrophage cells: {self.environment.count_astrophage_cells()}")
        self.environment.display(self.grace.pos, self.rocky.pos)

    # ── Results compilation ──────────────────────────────────────

    def _compile_results(self):
        return {
            'run_id':               self.run_id,
            'turns_survived':       self.turn,
            'end_reason':           self.end_reason,
            'mission_complete':     self.grace.mission_complete,
            'knowledge_score':      self.grace.knowledge_score,
            'breeding_progress':    round(self.taumoeba_lab.breeding_progress, 3),
            'viable_strain_found':  self.taumoeba_lab.viable_strain_found,
            'experiments_run':      self.taumoeba_lab.experiments_run,
            'experiment_success':   self.taumoeba_lab.experiments_success,
            'success_rate':         self.taumoeba_lab.success_rate(),
            'beetles_deployed':     self.beetle_fleet.deployed_count,
            'beetles_reached_earth':self.beetle_fleet.probes_reached_earth(),
            'astrophage_cells':     self.environment.count_astrophage_cells(),
            'rocky_repairs':        self.rocky.repairs_completed,
            'rocky_knowledge_shared':self.rocky.knowledge_shared,
            'grace_alive':          self.grace.alive,
            'history':              self.history,
        }
