"""
environment.py — 50x50 grid world for the Tau Ceti system
CPS7004 Project Hail Mary Simulation
"""

import random
from utils import (GRID_SIZE, EMPTY, HAIL_MARY, BLIP_A, ADRIAN,
                   ASTROPHAGE, RADIATION, DEBRIS, TUNNEL, TIME_DILATION,
                   CELL_SYMBOLS, wrap)


class EnvironmentGrid:
    """
    Represents the 2-D grid of space near the Tau Ceti system.
    Grid wraps around at edges to simulate open space.
    Cells contain: empty space, ships, planet, hazards, probes, tunnel.
    """

    def __init__(self):
        self.size = GRID_SIZE
        self.grid = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.astrophage_intensity = [[0.0 for _ in range(self.size)] for _ in range(self.size)]
        self.taumoeba_resistance  = [[0.0 for _ in range(self.size)] for _ in range(self.size)]

        # Fixed positions
        self.hail_mary_pos   = (5,  5)
        self.blip_a_pos      = (5, 10)
        self.adrian_pos      = (25, 25)
        self.tunnel_pos      = (5,  7)

        self._place_fixed_objects()
        self._generate_hazards()
        self._generate_petrova_line()
        self._generate_time_dilation_zones()

    # ── Setup ────────────────────────────────────────────────────

    def _place_fixed_objects(self):
        self.grid[self.hail_mary_pos[0]][self.hail_mary_pos[1]] = HAIL_MARY
        self.grid[self.blip_a_pos[0]][self.blip_a_pos[1]]       = BLIP_A
        self.grid[self.adrian_pos[0]][self.adrian_pos[1]]        = ADRIAN
        self.grid[self.tunnel_pos[0]][self.tunnel_pos[1]]        = TUNNEL

        # Adrian atmosphere — 3x3 zone around the planet
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r = wrap(self.adrian_pos[0] + dr)
                c = wrap(self.adrian_pos[1] + dc)
                if self.grid[r][c] == EMPTY:
                    self.grid[r][c] = ASTROPHAGE
                    self.astrophage_intensity[r][c] = round(random.uniform(0.4, 0.9), 2)

    def _generate_petrova_line(self):
        """Dense Astrophage band across the middle of the grid."""
        for r in range(self.size):
            for dc in range(-1, 2):
                c = wrap(r + dc + 15)
                if self.grid[r][c] == EMPTY:
                    self.grid[r][c] = ASTROPHAGE
                    self.astrophage_intensity[r][c] = round(random.uniform(0.6, 1.0), 2)

    def _generate_hazards(self):
        """Randomly scatter radiation zones, debris fields, and Astrophage clusters."""
        for _ in range(30):
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = RADIATION

        for _ in range(25):
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = DEBRIS

        for _ in range(20):
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = ASTROPHAGE
                self.astrophage_intensity[r][c] = round(random.uniform(0.1, 0.5), 2)

    def _generate_time_dilation_zones(self):
        """Optional extension: relativistic time-dilation zones."""
        for _ in range(5):
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.grid[r][c] == EMPTY:
                self.grid[r][c] = TIME_DILATION

    # ── Cell access ──────────────────────────────────────────────

    def get_cell(self, row, col):
        return self.grid[wrap(row)][wrap(col)]

    def set_cell(self, row, col, value):
        self.grid[wrap(row)][wrap(col)] = value

    def get_intensity(self, row, col):
        return self.astrophage_intensity[wrap(row)][wrap(col)]

    def is_navigable(self, row, col):
        cell = self.get_cell(row, col)
        return cell not in []  # all cells navigable but hazardous ones cost energy

    # ── Astrophage spread ────────────────────────────────────────

    def spread_astrophage(self, taumoeba_deployed=False):
        """
        Each step, Astrophage may spread to adjacent empty cells.
        If Taumoeba has been deployed, Astrophage gains resistance and spreads faster.
        """
        spread_rate   = 0.08 if not taumoeba_deployed else 0.14
        resist_bonus  = 0.05 if taumoeba_deployed else 0.0
        new_cells = []

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == ASTROPHAGE:
                    self.astrophage_intensity[r][c] = min(
                        1.0, self.astrophage_intensity[r][c] + resist_bonus
                    )
                    if random.random() < spread_rate:
                        directions = [(-1,0),(1,0),(0,-1),(0,1)]
                        dr, dc = random.choice(directions)
                        nr, nc = wrap(r + dr), wrap(c + dc)
                        if self.grid[nr][nc] == EMPTY:
                            new_cells.append((nr, nc))

        for r, c in new_cells:
            self.grid[r][c] = ASTROPHAGE
            self.astrophage_intensity[r][c] = round(random.uniform(0.1, 0.3), 2)

    # ── Console display ──────────────────────────────────────────

    def display(self, grace_pos=None, rocky_pos=None):
        """Print a compact console view of the grid (every 5th row/col)."""
        print("\n  Grid snapshot (every 5th cell):")
        for r in range(0, self.size, 5):
            row_str = ""
            for c in range(0, self.size, 5):
                if grace_pos and (r, c) == grace_pos:
                    row_str += 'G '
                elif rocky_pos and (r, c) == rocky_pos:
                    row_str += 'K '
                else:
                    row_str += CELL_SYMBOLS.get(self.grid[r][c], '?') + ' '
            print("  " + row_str)
        print()

    def count_astrophage_cells(self):
        return sum(1 for r in range(self.size)
                   for c in range(self.size)
                   if self.grid[r][c] == ASTROPHAGE)
