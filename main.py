"""
main.py — Entry point for Project Hail Mary Simulation
CPS7004 Project Hail Mary Simulation
Dr. Ryland Grace | Rocky | Astrophage | Taumoeba | Beetle Probes

Run: python3.12 main.py
"""

from simulation import Simulation
from analytics import Analytics


def main():
    print("\n" + "="*60)
    print("  PROJECT HAIL MARY — MULTI-AGENT AI SIMULATION")
    print("  CPS7004 Artificial Intelligence | St Mary's University")
    print("="*60)

    NUM_RUNS = 20
    analytics = Analytics()

    for run_id in range(1, NUM_RUNS + 1):
        print(f"\n  Starting Run {run_id}/{NUM_RUNS}...", end=' ')
        sim = Simulation(run_id=run_id, verbose=(run_id == 1))
        result = sim.run()
        analytics.record(result)
        print(f"Done. Turns: {result['turns_survived']:3d} | "
              f"Knowledge: {result['knowledge_score']:3d} | "
              f"Breeding: {result['breeding_progress']:.2f} | "
              f"Beetles: {result['beetles_deployed']} | "
              f"Complete: {result['mission_complete']}")

    # Statistical summary
    analytics.print_summary()

    # Save CSV results
    analytics.save_csv()

    # Generate all graphs
    print("\n  Generating graphs...")
    analytics.generate_graphs()

    print("\n  Simulation complete.")
    print("  Results saved to results/ folder.")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
