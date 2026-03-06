"""
environment.py
==============
GridWorld: the 2D grid environment in which the agent operates.

AI-agent vocabulary mapped to this module
------------------------------------------
  Environment  →  GridWorld
  State        →  (row, col) tuple
  Actions      →  UP, DOWN, LEFT, RIGHT (4-directional)
  Transition   →  GridWorld.result(state, action) → new state
  Goal test    →  GridWorld.is_goal(state)
  Path cost    →  uniform step cost = MOVE_COST (1 per step)
"""

from __future__ import annotations

from typing import Iterator, List, Optional, Set, Tuple

from constants import GRID_ROWS, GRID_COLS, MOVE_COST

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
State = Tuple[int, int]   # (row, col)

# ---------------------------------------------------------------------------
# Named action vectors: (Δrow, Δcol)
# ---------------------------------------------------------------------------
ACTIONS: List[Tuple[int, int]] = [
    (-1,  0),   # UP
    ( 1,  0),   # DOWN
    ( 0, -1),   # LEFT
    ( 0,  1),   # RIGHT
]


class GridWorld:
    """
    A finite, static 2D grid environment.

    Parameters
    ----------
    rows : int
        Number of rows in the grid.
    cols : int
        Number of columns in the grid.
    start : State
        Starting position (row, col) of the agent.
    goal : State
        Goal position (row, col).
    obstacles : set of State, optional
        Cells that are impassable. Defaults to the empty set.
    """

    def __init__(
        self,
        rows: int = GRID_ROWS,
        cols: int = GRID_COLS,
        start: State = (0, 0),
        goal: State = (GRID_ROWS - 1, GRID_COLS - 1),
        obstacles: Optional[Set[State]] = None,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.start = start
        self.goal = goal
        self.obstacles: Set[State] = obstacles if obstacles is not None else set()

        self._validate()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        """Raise ValueError for obviously invalid configurations."""
        if not self._in_bounds(self.start):
            raise ValueError(f"Start {self.start} is out of grid bounds.")
        if not self._in_bounds(self.goal):
            raise ValueError(f"Goal {self.goal} is out of grid bounds.")
        if self.start in self.obstacles:
            raise ValueError("Start cell cannot be an obstacle.")
        if self.goal in self.obstacles:
            raise ValueError("Goal cell cannot be an obstacle.")

    # ------------------------------------------------------------------
    # Environment interface
    # ------------------------------------------------------------------

    def _in_bounds(self, state: State) -> bool:
        r, c = state
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_passable(self, state: State) -> bool:
        """Return True if *state* is inside the grid and not blocked."""
        return self._in_bounds(state) and state not in self.obstacles

    def is_goal(self, state: State) -> bool:
        """Goal test: returns True when the agent has reached the goal."""
        return state == self.goal

    def step_cost(self, _from: State, _to: State) -> int:
        """Uniform step cost (1 per move); override for weighted grids."""
        return MOVE_COST

    def result(self, state: State, action: Tuple[int, int]) -> Optional[State]:
        """
        Transition model: apply *action* (Δrow, Δcol) to *state*.

        Returns the new state if the move is legal, None otherwise.
        """
        new_state = (state[0] + action[0], state[1] + action[1])
        if self.is_passable(new_state):
            return new_state
        return None

    def neighbors(self, state: State) -> Iterator[Tuple[State, int]]:
        """
        Yield (next_state, cost) for every legal action from *state*.

        Used by AStarSolver to expand a node.
        """
        for action in ACTIONS:
            next_state = self.result(state, action)
            if next_state is not None:
                yield next_state, self.step_cost(state, next_state)

    # ------------------------------------------------------------------
    # Serialisation helpers (for predefined maps / reset)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "start": self.start,
            "goal": self.goal,
            "obstacles": list(self.obstacles),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GridWorld":
        return cls(
            rows=data["rows"],
            cols=data["cols"],
            start=tuple(data["start"]),
            goal=tuple(data["goal"]),
            obstacles=set(map(tuple, data["obstacles"])),
        )

    def __repr__(self) -> str:
        return (
            f"GridWorld(rows={self.rows}, cols={self.cols}, "
            f"start={self.start}, goal={self.goal}, "
            f"obstacles={len(self.obstacles)} cells)"
        )
