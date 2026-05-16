"""
analytics.py — Results logging, statistical analysis and graph generation
CPS7004 Project Hail Mary Simulation
"""

import os
import csv
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


RESULTS_DIR = 'results'


class Analytics:
    """
    Handles all quantitative output for the simulation:
    - Saves per-run results to CSV
    - Generates 5 required matplotlib graphs
    - Prints statistical summary across all 20 runs
    """

    def __init__(self):
        os.makedirs(RESULTS_DIR, exist_ok=True)
        self.all_results = []

    # ── Data collection ──────────────────────────────────────────

    def record(self, result):
        """Store one run's results."""
        self.all_results.append(result)

    def save_csv(self):
        """Save all run results to CSV file."""
        if not self.all_results:
            return

        filepath = os.path.join(RESULTS_DIR, 'simulation_results.csv')
        keys = [k for k in self.all_results[0].keys() if k != 'history']

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for result in self.all_results:
                row = {k: result[k] for k in keys}
                writer.writerow(row)

        print(f"\n  Results saved to {filepath}")

    # ── Statistical summary ──────────────────────────────────────

    def print_summary(self):
        """Print statistical analysis across all simulation runs."""
        if not self.all_results:
            return

        n = len(self.all_results)
        turns        = [r['turns_survived']    for r in self.all_results]
        knowledge    = [r['knowledge_score']   for r in self.all_results]
        breeding     = [r['breeding_progress'] for r in self.all_results]
        beetles      = [r['beetles_deployed']  for r in self.all_results]
        success_rate = [r['success_rate']      for r in self.all_results]
        missions     = sum(1 for r in self.all_results if r['mission_complete'])
        viable       = sum(1 for r in self.all_results if r['viable_strain_found'])

        print(f"\n{'='*60}")
        print(f"  STATISTICAL SUMMARY — {n} Simulation Runs")
        print(f"{'='*60}")
        print(f"  Missions complete:        {missions}/{n} "
              f"({missions/n*100:.1f}%)")
        print(f"  Viable strain found:      {viable}/{n} "
              f"({viable/n*100:.1f}%)")
        print(f"  Avg turns survived:       {sum(turns)/n:.1f} "
              f"(min:{min(turns)} max:{max(turns)})")
        print(f"  Avg knowledge score:      {sum(knowledge)/n:.1f} "
              f"(min:{min(knowledge)} max:{max(knowledge)})")
        print(f"  Avg breeding progress:    {sum(breeding)/n:.3f} "
              f"(min:{min(breeding):.3f} max:{max(breeding):.3f})")
        print(f"  Avg beetles deployed:     {sum(beetles)/n:.1f} "
              f"(min:{min(beetles)} max:{max(beetles)})")
        print(f"  Avg experiment success:   {sum(success_rate)/n:.3f}")
        print(f"{'='*60}\n")

    # ── Graph generation ─────────────────────────────────────────

    def generate_graphs(self):
        """
        Generate all 5 required matplotlib graphs and save to results/.
        Uses data from all simulation runs.
        """
        if not self.all_results:
            return

        self._graph_knowledge_progression()
        self._graph_survival_duration()
        self._graph_experiment_success()
        self._graph_astrophage_spread()
        self._graph_resource_consumption()
        self._graph_summary_dashboard()
        print(f"  Graphs saved to {RESULTS_DIR}/")

    def _graph_knowledge_progression(self):
        """Graph 1 — Knowledge score progression over turns."""
        fig, ax = plt.subplots(figsize=(10, 5))

        for result in self.all_results:
            history = result['history']
            ax.plot(history['turn'], history['grace_knowledge'],
                    alpha=0.3, linewidth=0.8,
                    color='royalblue')

        # Average line
        max_turns = max(len(r['history']['turn']) for r in self.all_results)
        avg_knowledge = []
        for t in range(max_turns):
            vals = [r['history']['grace_knowledge'][t]
                    for r in self.all_results
                    if t < len(r['history']['grace_knowledge'])]
            avg_knowledge.append(sum(vals) / len(vals) if vals else 0)

        ax.plot(range(max_turns), avg_knowledge,
                color='darkblue', linewidth=2.5,
                label='Average knowledge', zorder=5)

        ax.axhline(y=100, color='gold', linestyle='--',
                   linewidth=1.5, label='Win threshold (100)')
        ax.set_title('Graph 1 — Knowledge Score Progression Across 20 Runs',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Turn')
        ax.set_ylabel('Knowledge Score')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'graph1_knowledge_progression.png'),
                    dpi=150)
        plt.close()

    def _graph_survival_duration(self):
        """Graph 2 — Survival duration per run."""
        fig, ax = plt.subplots(figsize=(10, 5))

        run_ids = [r['run_id']        for r in self.all_results]
        turns   = [r['turns_survived'] for r in self.all_results]
        colors  = ['green' if r['mission_complete'] else 'crimson'
                   for r in self.all_results]

        bars = ax.bar(run_ids, turns, color=colors, edgecolor='black',
                      linewidth=0.5)
        ax.axhline(y=sum(turns)/len(turns), color='navy',
                   linestyle='--', linewidth=1.5,
                   label=f'Average: {sum(turns)/len(turns):.1f} turns')

        ax.set_title('Graph 2 — Survival Duration Per Run '
                     '(Green = Mission Complete)',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Run ID')
        ax.set_ylabel('Turns Survived')
        ax.set_xticks(run_ids)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'graph2_survival_duration.png'),
                    dpi=150)
        plt.close()

    def _graph_experiment_success(self):
        """Graph 3 — Experiment success rates and breeding progress."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Success rate per run
        run_ids      = [r['run_id']      for r in self.all_results]
        success_rate = [r['success_rate'] for r in self.all_results]
        breeding     = [r['breeding_progress'] for r in self.all_results]

        ax1.bar(run_ids, success_rate, color='mediumseagreen',
                edgecolor='black', linewidth=0.5)
        ax1.axhline(y=sum(success_rate)/len(success_rate),
                    color='darkgreen', linestyle='--', linewidth=1.5,
                    label=f'Avg: {sum(success_rate)/len(success_rate):.3f}')
        ax1.set_title('Experiment Success Rate Per Run',
                      fontsize=11, fontweight='bold')
        ax1.set_xlabel('Run ID')
        ax1.set_ylabel('Success Rate')
        ax1.set_ylim(0, 1)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        ax2.bar(run_ids, breeding, color='darkorange',
                edgecolor='black', linewidth=0.5)
        ax2.axhline(y=1.0, color='red', linestyle='--',
                    linewidth=1.5, label='Viable strain threshold')
        ax2.set_title('Taumoeba Breeding Progress Per Run',
                      fontsize=11, fontweight='bold')
        ax2.set_xlabel('Run ID')
        ax2.set_ylabel('Breeding Progress (0→1)')
        ax2.set_ylim(0, 1.1)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        fig.suptitle('Graph 3 — Taumoeba Experimentation Results',
                     fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'graph3_experiment_success.png'),
                    dpi=150)
        plt.close()

    def _graph_astrophage_spread(self):
        """Graph 4 — Astrophage spread over turns."""
        fig, ax = plt.subplots(figsize=(10, 5))

        for result in self.all_results:
            history = result['history']
            ax.plot(history['turn'], history['astrophage_cells'],
                    alpha=0.3, linewidth=0.8, color='crimson')

        max_turns = max(len(r['history']['turn']) for r in self.all_results)
        avg_astrophage = []
        for t in range(max_turns):
            vals = [r['history']['astrophage_cells'][t]
                    for r in self.all_results
                    if t < len(r['history']['astrophage_cells'])]
            avg_astrophage.append(sum(vals)/len(vals) if vals else 0)

        ax.plot(range(max_turns), avg_astrophage,
                color='darkred', linewidth=2.5,
                label='Average Astrophage cells', zorder=5)

        ax.set_title('Graph 4 — Astrophage Spread Over Simulation Turns',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Turn')
        ax.set_ylabel('Number of Astrophage Cells')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'graph4_astrophage_spread.png'),
                    dpi=150)
        plt.close()

    def _graph_resource_consumption(self):
        """Graph 5 — Grace energy and health over turns (best run)."""
        best = max(self.all_results, key=lambda r: r['knowledge_score'])
        history = best['history']

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(history['turn'], history['grace_energy'],
                color='royalblue', linewidth=2, label='Grace Energy')
        ax.plot(history['turn'], history['grace_health'],
                color='mediumseagreen', linewidth=2, label='Grace Health')
        ax.plot(history['turn'], history['rocky_energy'],
                color='darkorange', linewidth=2,
                linestyle='--', label='Rocky Energy')

        ax.set_title(f'Graph 5 — Resource Consumption Over Time '
                     f'(Best Run: #{best["run_id"]})',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Turn')
        ax.set_ylabel('Resource Level (0–100)')
        ax.set_ylim(0, 110)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'graph5_resource_consumption.png'),
                    dpi=150)
        plt.close()

    def _graph_summary_dashboard(self):
        """Summary dashboard — beetles deployed and mission outcomes."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Beetles deployed per run
        run_ids = [r['run_id']         for r in self.all_results]
        beetles = [r['beetles_deployed'] for r in self.all_results]
        ax1.bar(run_ids, beetles, color='steelblue',
                edgecolor='black', linewidth=0.5)
        ax1.set_title('Beetle Probes Deployed Per Run',
                      fontsize=11, fontweight='bold')
        ax1.set_xlabel('Run ID')
        ax1.set_ylabel('Beetles Deployed')
        ax1.set_ylim(0, 5)
        ax1.grid(True, alpha=0.3, axis='y')

        # Mission outcomes pie chart
        complete   = sum(1 for r in self.all_results if r['mission_complete'])
        incomplete = len(self.all_results) - complete
        ax2.pie([complete, incomplete],
                labels=[f'Complete ({complete})', f'Incomplete ({incomplete})'],
                colors=['mediumseagreen', 'crimson'],
                autopct='%1.1f%%', startangle=90)
        ax2.set_title('Mission Outcomes Across 20 Runs',
                      fontsize=11, fontweight='bold')

        fig.suptitle('Summary Dashboard — Beetle Probes & Mission Outcomes',
                     fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'graph_summary_dashboard.png'),
                    dpi=150)
        plt.close()
