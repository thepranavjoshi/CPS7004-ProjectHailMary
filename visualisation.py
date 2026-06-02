"""
visualisation.py — 20-Run Batch Visualizer with Labels
CPS7004 Project Hail Mary Simulation
"""

import tkinter as tk
from simulation import Simulation
from analytics import Analytics
from utils import (ASTROPHAGE, RADIATION, DEBRIS, TIME_DILATION,
                   TUNNEL, HAIL_MARY, BLIP_A, ADRIAN)

class SimulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Hail Mary - 20-Run Batch Simulation")
        self.configure(bg="#1e1e1e")

        # 1. Batch Tracking Setup
        self.total_runs = 20
        self.current_run = 1
        self.analytics = Analytics()

        # 2. Initialize First Simulation
        self.sim = Simulation(run_id=self.current_run, verbose=False)
        self.grid_size = self.sim.environment.size
        self.cell_size = 14  # Pixels per grid cell
        self.canvas_size = self.grid_size * self.cell_size

        # 3. Setup UI Layout
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size,
                                bg='#000000', highlightthickness=1, highlightbackground="#444444")
        self.canvas.pack(side=tk.LEFT, padx=15, pady=15)

        self.panel = tk.Frame(self, bg="#1e1e1e", width=350)
        self.panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.stats_lbl = tk.Label(self.panel, text="Initializing...", font=("Courier", 11),
                                  bg="#1e1e1e", fg="#00FF00", justify=tk.LEFT)
        self.stats_lbl.pack(anchor="nw")

        # 4. Start the loop after a tiny delay
        self.after(500, self.step_sim)

    def step_sim(self):
        """Advances the simulation by one tick. Handles run transitions."""
        if not self.sim.ended and self.sim.turn < self.sim.MAX_TURNS:
            # Advance simulation logic
            self.sim.turn += 1
            self.sim._execute_turn()
            self.sim._record_history()
            self.sim._check_end_conditions()

            # Update visuals and loop quickly (20ms for fast batch processing)
            self.draw_frame()
            self.after(20, self.step_sim)

        else:
            # RUN FINISHED -> Record Data
            self.draw_frame()
            result = self.sim._compile_results()
            self.analytics.record(result)

            # Check if we need to start the next run or finish the batch
            if self.current_run < self.total_runs:
                self.current_run += 1
                self.sim = Simulation(run_id=self.current_run, verbose=False)

                # Brief 1-second pause between runs so you can see the reset
                self.after(1000, self.step_sim)
            else:
                self.show_final_summary()

    def draw_frame(self):
        """Clears and redraws the entire grid based on current simulation state."""
        self.canvas.delete("all")

        # -- 1. Draw Hazards & Astrophage (No labels to avoid clutter) --
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                val = self.sim.environment.grid[r][c]
                if val == ASTROPHAGE:
                    self.draw_entity(r, c, "crimson", shape="rect")
                elif val in [RADIATION, DEBRIS, TIME_DILATION]:
                    self.draw_entity(r, c, "darkorange", shape="rect")

        # -- 2. Draw Fixed Landmarks (With Labels) --
        hm_r, hm_c = self.sim.environment.hail_mary_pos
        self.draw_entity(hm_r, hm_c, "royalblue", shape="oval", scale=1.5, label="Hail Mary")

        blip_r, blip_c = self.sim.environment.blip_a_pos
        self.draw_entity(blip_r, blip_c, "gray", shape="oval", scale=1.5, label="Blip-A")

        adrian_r, adrian_c = self.sim.environment.adrian_pos
        self.draw_entity(adrian_r, adrian_c, "saddlebrown", shape="oval", scale=3.0, label="Adrian")

        tunnel_r, tunnel_c = self.sim.environment.tunnel_pos
        self.draw_entity(tunnel_r, tunnel_c, "purple", shape="rect", scale=1.0)

        # -- 3. Draw Beetles (With Labels) --
        for b in self.sim.beetle_fleet.probes:
            if b.deployed and not b.reached_earth and b.alive:
                self.draw_entity(b.row, b.col, "cyan", shape="oval", scale=0.6, label=b.name)

        # -- 4. Draw Agents (With Labels) --
        if self.sim.rocky.alive:
            self.draw_entity(self.sim.rocky.row, self.sim.rocky.col, "magenta", shape="oval", scale=1.2, label="Rocky")

        if self.sim.grace.alive:
            self.draw_entity(self.sim.grace.row, self.sim.grace.col, "lime", shape="oval", scale=1.2, label="Grace")

        # -- 5. Update HUD Text (Current Run Status) --
        stats = (
            f"BATCH RUN:  {self.current_run} / {self.total_runs}\n"
            f"TURN:       {self.sim.turn:03d} / {self.sim.MAX_TURNS}\n"
            f"{'='*30}\n"
            f"GRACE\n"
            f"  HP:     {self.sim.grace.health}\n"
            f"  Energy: {self.sim.grace.energy}\n"
            f"  Knowlg: {self.sim.grace.knowledge_score}/100\n"
            f"  Sample: {self.sim.grace.sample_inventory}\n\n"
            f"SYSTEMS\n"
            f"  Astrophage: {self.sim.environment.count_astrophage_cells():03d}\n"
            f"  Beetles:    {self.sim.beetle_fleet.deployed_count}/4\n"
        )
        if self.sim.ended and self.current_run < self.total_runs:
            stats += f"\n\n[ RUN {self.current_run} ENDED ]\n{self.sim.end_reason}\n\nStarting next run..."

        self.stats_lbl.config(text=stats)

    def draw_entity(self, r, c, color, shape="rect", scale=1.0, label=None):
        """Helper to draw geometric shapes and optional text labels accurately."""
        cx = (c + 0.5) * self.cell_size
        cy = (r + 0.5) * self.cell_size
        hw = (self.cell_size / 2) * scale * 0.90

        x0, y0 = cx - hw, cy - hw
        x1, y1 = cx + hw, cy + hw

        if shape == "rect":
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
        elif shape == "oval":
            self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="white")

        # Render the text label slightly above the entity
        if label:
            self.canvas.create_text(cx, y0 - 8, text=label, fill="#FFFFFF", font=("Arial", 8, "bold"))

    def show_final_summary(self):
        """Calculates and displays the final 20-run statistics on the HUD."""
        # Calculate summary statistics exactly like your analytics.py does
        results = self.analytics.all_results
        n = len(results)

        missions = sum(1 for r in results if r['mission_complete'])
        viable = sum(1 for r in results if r['viable_strain_found'])
        avg_turns = sum(r['turns_survived'] for r in results) / n
        avg_know = sum(r['knowledge_score'] for r in results) / n
        avg_breed = sum(r['breeding_progress'] for r in results) / n
        avg_beetles = sum(r['beetles_deployed'] for r in results) / n

        # Dim the canvas slightly and add a "Complete" overlay
        self.canvas.create_rectangle(0, 0, self.canvas_size, self.canvas_size, fill="black", stipple="gray50")
        self.canvas.create_text(self.canvas_size/2, self.canvas_size/2,
                                text="20-RUN BATCH COMPLETE", fill="#00FF00", font=("Arial", 18, "bold"))

        # Output the final stats to the HUD
        final_text = (
            f"*** SIMULATION BATCH COMPLETE ***\n"
            f"{'='*30}\n"
            f"Total Runs:       {n}\n"
            f"Missions Won:     {missions}/{n} ({missions/n*100:.1f}%)\n"
            f"Viable Taumoeba:  {viable}/{n}\n\n"
            f"AVERAGES ACROSS 20 RUNS:\n"
            f"  Turns Survived: {avg_turns:.1f}\n"
            f"  Knowledge:      {avg_know:.1f} / 100\n"
            f"  Breeding Prog:  {avg_breed:.3f}\n"
            f"  Beetles Deploy: {avg_beetles:.1f} / 4\n\n"
            f"Check 'results/' folder for\ngenerated CSV and Graphs."
        )
        self.stats_lbl.config(text=final_text, fg="#00FFFF")

        # Ensure the graphs and CSV are saved to the disk exactly like main.py
        self.analytics.save_csv()
        self.analytics.generate_graphs()
        print("\nBatch complete! Results and graphs saved to your results/ folder.")

if __name__ == "__main__":
    app = SimulationApp()
    app.mainloop()