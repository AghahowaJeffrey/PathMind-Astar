"""
utils.py
========
Utility functions shared across modules.

Heuristics, path reconstruction, predefined maps, and timing helpers.
"""

from __future__ import annotations

import random
import time
from typing import Dict, List, Optional, Set, Tuple

from constants import (
    GRID_ROWS,
    GRID_COLS,
    MAP_OPEN_FIELD,
    MAP_MAZE,
    MAP_CORRIDORS,
    MAP_RANDOM,
)

State = Tuple[int, int]


# ---------------------------------------------------------------------------
# Heuristics
# ---------------------------------------------------------------------------

def manhattan_distance(a: State, b: State) -> int:
    """
    Manhattan (L1) distance between two grid cells.

    This is an *admissible* heuristic for 4-directional movement on a
    uniform-cost grid: it never overestimates the true cost because you
    need at least |Δrow| + |Δcol| moves to reach the goal.

        h(n) = |row_n - row_goal| + |col_n - col_goal|
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ---------------------------------------------------------------------------
# Path reconstruction
# ---------------------------------------------------------------------------

def reconstruct_path(
    came_from: Dict[State, Optional[State]],
    goal: State,
) -> List[State]:
    """
    Walk the *came_from* parent-pointer map from *goal* back to
    the start and return the path in start-to-goal order.

    Parameters
    ----------
    came_from : dict mapping state → parent state (or None for start)
    goal      : the goal state from which to trace back

    Returns
    -------
    List of states forming the optimal path, inclusive of start and goal.
    """
    path: List[State] = []
    current: Optional[State] = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# Predefined maps
# ---------------------------------------------------------------------------

def _border_obstacles(rows: int, cols: int) -> Set[State]:
    """Return a set containing the four border cells of the grid."""
    obs: Set[State] = set()
    for c in range(cols):
        obs.add((0, c))
        obs.add((rows - 1, c))
    for r in range(rows):
        obs.add((r, 0))
        obs.add((r, cols - 1))
    return obs


def get_predefined_map(
    name: str,
    rows: int = GRID_ROWS,
    cols: int = GRID_COLS,
) -> dict:
    """
    Return a map-config dict compatible with GridWorld.from_dict().

    All maps guarantee that start and goal are reachable.
    """
    if name == MAP_OPEN_FIELD:
        return _map_open_field(rows, cols)
    if name == MAP_MAZE:
        return _map_maze(rows, cols)
    if name == MAP_CORRIDORS:
        return _map_corridors(rows, cols)
    if name == MAP_RANDOM:
        return _map_random(rows, cols)
    raise ValueError(f"Unknown map name: '{name}'")


def _map_open_field(rows: int, cols: int) -> dict:
    """Sparse obstacles — mostly clear, a few scattered rocks."""
    obstacles = set()
    # A cluster of rocks in the middle
    mid_r, mid_c = rows // 2, cols // 2
    for dr in range(-1, 4):
        for dc in range(-1, 6):
            obstacles.add((mid_r + dr, mid_c + dc))
    start = (1, 1)
    goal  = (rows - 2, cols - 2)
    obstacles.discard(start)
    obstacles.discard(goal)
    return {"rows": rows, "cols": cols, "start": start, "goal": goal,
            "obstacles": list(obstacles)}


def _map_maze(rows: int, cols: int) -> dict:
    """
    Classic horizontal-wall maze pattern:
    alternating solid walls with a single gap.
    """
    obstacles = set()
    gap_col = 1
    for wall_row in range(2, rows - 1, 3):
        for c in range(cols):
            if c != gap_col:
                obstacles.add((wall_row, c))
        # Alternate gap side
        gap_col = (cols - 2) if gap_col == 1 else 1

    start = (0, 1)
    goal  = (rows - 1, cols - 2)
    obstacles.discard(start)
    obstacles.discard(goal)
    return {"rows": rows, "cols": cols, "start": start, "goal": goal,
            "obstacles": list(obstacles)}


def _map_corridors(rows: int, cols: int) -> dict:
    """Grid of vertical dividers forming corridor pockets."""
    obstacles = set()
    # Vertical walls every 5 columns, with gaps every 3 rows
    for c in range(4, cols - 1, 5):
        for r in range(rows):
            if r % 3 != 0:
                obstacles.add((r, c))

    start = (1, 1)
    goal  = (rows - 2, cols - 2)
    obstacles.discard(start)
    obstacles.discard(goal)
    return {"rows": rows, "cols": cols, "start": start, "goal": goal,
            "obstacles": list(obstacles)}


def _map_random(rows: int, cols: int, density: float = 0.25) -> dict:
    """Randomly placed obstacles at ~density fraction of cells."""
    random.seed(42)          # deterministic seed for reproducibility
    start = (1, 1)
    goal  = (rows - 2, cols - 2)
    obstacles = set()
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in (start, goal):
                if random.random() < density:
                    obstacles.add((r, c))
    return {"rows": rows, "cols": cols, "start": start, "goal": goal,
            "obstacles": list(obstacles)}


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

class Stopwatch:
    """Simple wall-clock stopwatch."""

    def __init__(self) -> None:
        self._start: Optional[float] = None
        self._elapsed: float = 0.0

    def start(self) -> None:
        self._start = time.perf_counter()

    def stop(self) -> None:
        if self._start is not None:
            self._elapsed += time.perf_counter() - self._start
            self._start = None

    def reset(self) -> None:
        self._start = None
        self._elapsed = 0.0

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds (includes running time if active)."""
        running = (
            (time.perf_counter() - self._start) if self._start is not None else 0.0
        )
        return (self._elapsed + running) * 1000.0
