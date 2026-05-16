"""
utils.py — Shared constants and utility functions
CPS7004 Project Hail Mary Simulation
"""

import random

# ── Grid constants ──────────────────────────────────────────────
GRID_SIZE = 50

# ── Cell type identifiers ────────────────────────────────────────
EMPTY          = 0
HAIL_MARY      = 1
BLIP_A         = 2
ADRIAN         = 3
ASTROPHAGE     = 4
RADIATION      = 5
DEBRIS         = 6
BEETLE         = 7
TUNNEL         = 8
TIME_DILATION  = 9

# ── Cell display symbols (for console output) ────────────────────
CELL_SYMBOLS = {
    EMPTY:         '·',
    HAIL_MARY:     'H',
    BLIP_A:        'B',
    ADRIAN:        'A',
    ASTROPHAGE:    '☠',
    RADIATION:     'R',
    DEBRIS:        'D',
    BEETLE:        'b',
    TUNNEL:        'T',
    TIME_DILATION: 'Z',
}

# ── Energy costs ─────────────────────────────────────────────────
ENERGY_MOVE          = 2
ENERGY_EXPERIMENT    = 10
ENERGY_EVA           = 15
ENERGY_TUNNEL        = 8
ENERGY_DEPLOY_BEETLE = 20
ENERGY_REPAIR        = 12
ENERGY_REST_GAIN     = 15
ENERGY_COMMUNICATE   = 3

# ── Astrophage settings ──────────────────────────────────────────
ASTROPHAGE_DRAIN     = 5
RADIATION_DRAIN      = 8
DEBRIS_DRAIN         = 3

# ── Mission thresholds ───────────────────────────────────────────
KNOWLEDGE_FLASHBACK_1  = 20
KNOWLEDGE_FLASHBACK_2  = 50
KNOWLEDGE_FLASHBACK_3  = 80
KNOWLEDGE_WIN          = 100

# ── Reinforcement learning settings ─────────────────────────────
REWARD_EXPERIMENT_SUCCESS  =  10
REWARD_EXPERIMENT_PARTIAL  =   4
REWARD_EXPERIMENT_FAIL     =  -5
REWARD_BEETLE_DEPLOYED     =  15
REWARD_SAMPLE_COLLECTED    =   5
REWARD_REPAIR              =   6
REWARD_ENERGY_WASTED       =  -3

# ── Utility functions ────────────────────────────────────────────
def wrap(value, size=GRID_SIZE):
    """Wrap a coordinate around the grid edges."""
    return value % size

def manhattan_distance(pos1, pos2):
    """Manhattan distance between two (row, col) positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def clamp(value, min_val=0, max_val=100):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))

def random_adjacent(pos):
    """Return a random adjacent cell (wrapping at edges)."""
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dr, dc = random.choice(directions)
    return (wrap(pos[0] + dr), wrap(pos[1] + dc))

def log(message):
    """Simple timestamped console logger."""
    print(f"  [SIM] {message}")
