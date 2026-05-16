# Project Hail Mary Simulation
## CPS7004 – Artificial Intelligence | St Mary's University, Twickenham

A multi-agent AI simulation based on Andy Weir's *Project Hail Mary*.

## Requirements
- Python 3.12+
- matplotlib

## Installation
```bash
pip3.12 install matplotlib
```

## Running the Simulation
```bash
python3.12 main.py
```

## Project Structure
- `environment.py` — 50x50 grid world
- `agent.py` — Base agent class
- `grace.py` — Dr. Ryland Grace agent
- `rocky.py` — Rocky (Eridian alien) agent
- `astrophage.py` — Astrophage threat system
- `taumoeba.py` — Taumoeba experimentation lab
- `beetle.py` — Autonomous beetle probes
- `simulation.py` — Simulation controller
- `analytics.py` — Results logging and graphing
- `utils.py` — Shared utilities
- `main.py` — Entry point

## Results
Simulation results and graphs are saved to the `results/` folder.
