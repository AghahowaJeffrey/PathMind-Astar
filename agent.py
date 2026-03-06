"""
agent.py
=========
GoalBasedAgent: the rational actor that uses A* to reach its goal.

What makes this agent *goal-based*?
-------------------------------------
A goal-based agent (Russell & Norvig, 2021) differs from a purely
reactive agent in that it:

  1. Maintains an explicit *goal* — a desired state of the world.
  2. Chooses actions based on a *plan* that achieves the goal, not
     merely on the current percept.
  3. Uses a *search algorithm* (here, A*) to find that plan.

Architecture
------------
  Percept   → current grid position (assumed fully observable)
  Goal      → GridWorld.goal
  Plan      → ordered list of states returned by AStarSolver
  Action    → move to the next state in the plan
  Execution → follow_plan() advances one step at a time
"""

from __future__ import annotations

from typing import Callable, List, Optional

from environment import GridWorld, State
from astar import AStarSolver, SearchStep
from utils import manhattan_distance, Stopwatch


class GoalBasedAgent:
    """
    A goal-based planning agent that uses A* search.

    Parameters
    ----------
    grid      : GridWorld — the environment the agent lives in.
    heuristic : Callable[[State, State], float]
                Heuristic function for A*. Defaults to Manhattan distance.

    Lifecycle
    ---------
      1. plan()       — run A* and store the result
      2. follow_plan() — yield successive positions along the found path
    """

    def __init__(
        self,
        grid: GridWorld,
        heuristic: Callable[[State, State], float] = manhattan_distance,
    ) -> None:
        self.grid = grid
        self.heuristic = heuristic

        # Internal planner
        self._solver: AStarSolver = AStarSolver(grid, heuristic)
        self._stopwatch: Stopwatch = Stopwatch()

        # Planning results
        self.path: List[State] = []
        self.plan_found: bool = False
        self.nodes_explored: int = 0
        self.path_cost: int = 0
        self.elapsed_ms: float = 0.0

        # Animation state
        self._step_index: int = 0
        self.current_position: State = grid.start

    # ------------------------------------------------------------------
    # Planning (A* search)
    # ------------------------------------------------------------------

    def plan_generator(self):
        """
        Return the raw A* generator for step-by-step GUI animation.

        The GUI drives the generator; the agent updates its internal
        state when a final SearchStep (found or exhausted) is received.
        """
        self._stopwatch.reset()
        self._stopwatch.start()
        return self._solver.run()

    def record_result(self, final_step: SearchStep) -> None:
        """
        Called by the GUI after the A* generator finishes to persist
        planning metadata into the agent.
        """
        self._stopwatch.stop()
        self.elapsed_ms = self._stopwatch.elapsed_ms
        self.plan_found = final_step.found
        self.nodes_explored = final_step.nodes_explored
        self.path = final_step.path
        self.path_cost = len(final_step.path) - 1 if final_step.path else 0
        self._step_index = 0
        self.current_position = self.grid.start

    # ------------------------------------------------------------------
    # Execution (following the plan)
    # ------------------------------------------------------------------

    def has_next_step(self) -> bool:
        """True while there are remaining steps in the plan."""
        return self._step_index < len(self.path) - 1

    def advance(self) -> Optional[State]:
        """
        Move to the next state in the plan.

        Returns the new position, or None if the plan is finished.
        """
        if not self.has_next_step():
            return None
        self._step_index += 1
        self.current_position = self.path[self._step_index]
        return self.current_position

    def reset(self) -> None:
        """Reset agent state (but keep the grid reference)."""
        self._solver = AStarSolver(self.grid, self.heuristic)
        self._stopwatch.reset()
        self.path = []
        self.plan_found = False
        self.nodes_explored = 0
        self.path_cost = 0
        self.elapsed_ms = 0.0
        self._step_index = 0
        self.current_position = self.grid.start

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def goal(self) -> State:
        return self.grid.goal

    @property
    def start(self) -> State:
        return self.grid.start

    def __repr__(self) -> str:
        status = "has plan" if self.plan_found else "no plan"
        return (
            f"GoalBasedAgent(start={self.start}, goal={self.goal}, "
            f"status={status}, path_cost={self.path_cost})"
        )
