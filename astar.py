"""
astar.py
========
AStarSolver: a step-by-step, generator-based A* search engine.

Key A* identity
---------------
    f(n) = g(n) + h(n)

    g(n) — exact cost from START to node n (known)
    h(n) — heuristic estimated cost from n to GOAL (admissible ⟹ optimal)
    f(n) — total estimated cost of a path through n

The solver is implemented as a *generator* that yields a SearchStep
snapshot after every node expansion.  This lets the GUI animate the
search without running it in a separate thread.

Data structures
---------------
  open_set  : min-heap ordered by f(n)  → O(log n) pop
  closed_set: plain set for O(1) membership test
  g_cost    : dict mapping state → best known g value
  came_from : dict mapping state → parent state (for path reconstruction)
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Callable, Dict, Generator, List, Optional, Set, Tuple

from environment import GridWorld, State
from utils import manhattan_distance, reconstruct_path


# ---------------------------------------------------------------------------
# Internal heap entry
# ---------------------------------------------------------------------------

@dataclass(order=True)
class _HeapItem:
    """Heap entry: (f, tie-breaker, state)."""
    f: float
    counter: int                    # tie-break by insertion order
    state: State = field(compare=False)


# ---------------------------------------------------------------------------
# SearchStep — snapshot of algorithm state at each expansion
# ---------------------------------------------------------------------------

@dataclass
class SearchStep:
    """
    Immutable snapshot of the A* state at one expansion.

    Attributes
    ----------
    current     : State being expanded this step.
    open_set    : frozenset of states currently in the open set.
    closed_set  : frozenset of states already fully explored.
    g_cost      : dict of best-known g values seen so far.
    path        : reconstructed path (non-empty only on final step).
    found       : True when the goal was just reached.
    exhausted   : True when the open set emptied (no path exists).
    nodes_explored : running count of expansions.
    """
    current: Optional[State]
    open_set: frozenset
    closed_set: frozenset
    g_cost: Dict[State, float]
    path: List[State]
    found: bool
    exhausted: bool
    nodes_explored: int


# ---------------------------------------------------------------------------
# AStarSolver
# ---------------------------------------------------------------------------

class AStarSolver:
    """
    Goal-directed A* search over a GridWorld.

    Parameters
    ----------
    grid      : GridWorld environment to search.
    heuristic : callable (state, goal) → estimated cost.
                Defaults to Manhattan distance.

    Usage
    -----
        solver = AStarSolver(grid)
        for step in solver.run():
            # step is a SearchStep
            if step.found or step.exhausted:
                break
    """

    def __init__(
        self,
        grid: GridWorld,
        heuristic: Callable[[State, State], float] = manhattan_distance,
    ) -> None:
        self.grid = grid
        self.heuristic = heuristic

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> Generator[SearchStep, None, None]:
        """
        Generator: yield one SearchStep per node expansion.

        The caller drives the search by iterating (e.g. calling next()
        once per animation frame).  When a SearchStep with
        found=True or exhausted=True is yielded, the search is complete.
        """
        start = self.grid.start
        goal  = self.grid.goal

        # g_cost[state] = cheapest known cost from start to state
        g_cost: Dict[State, float] = {start: 0.0}

        # Parent pointers for path reconstruction
        came_from: Dict[State, Optional[State]] = {start: None}

        # Priority queue (min-heap by f value)
        counter = 0
        open_heap: List[_HeapItem] = []
        h0 = self.heuristic(start, goal)
        heapq.heappush(open_heap, _HeapItem(f=h0, counter=counter, state=start))

        # Fast membership test for open set (mirrors the heap)
        open_set: Set[State] = {start}

        # States fully expanded
        closed_set: Set[State] = set()

        nodes_explored = 0

        while open_heap:
            # Pop lowest-f node
            item = heapq.heappop(open_heap)
            current = item.state

            # Skip stale entries (state was re-inserted with better g)
            if current in closed_set:
                continue

            open_set.discard(current)
            closed_set.add(current)
            nodes_explored += 1

            # ----- Yield snapshot so the GUI can render this step -----
            is_goal = self.grid.is_goal(current)
            path = reconstruct_path(came_from, current) if is_goal else []

            yield SearchStep(
                current=current,
                open_set=frozenset(open_set),
                closed_set=frozenset(closed_set),
                g_cost=dict(g_cost),
                path=path,
                found=is_goal,
                exhausted=False,
                nodes_explored=nodes_explored,
            )

            if is_goal:
                return   # Search complete

            # ----- Expand neighbours -----
            for neighbour, step_cost in self.grid.neighbors(current):
                if neighbour in closed_set:
                    continue

                tentative_g = g_cost[current] + step_cost

                if tentative_g < g_cost.get(neighbour, float("inf")):
                    # Found a better path to neighbour
                    g_cost[neighbour] = tentative_g
                    came_from[neighbour] = current

                    h = self.heuristic(neighbour, goal)
                    f = tentative_g + h
                    counter += 1
                    heapq.heappush(open_heap, _HeapItem(f=f, counter=counter,
                                                        state=neighbour))
                    open_set.add(neighbour)

        # Open set exhausted — no path exists
        yield SearchStep(
            current=None,
            open_set=frozenset(),
            closed_set=frozenset(closed_set),
            g_cost=dict(g_cost),
            path=[],
            found=False,
            exhausted=True,
            nodes_explored=nodes_explored,
        )

    def solve(self) -> Optional[List[State]]:
        """
        Convenience: run A* to completion and return the path (or None).

        Useful for non-animated use-cases and unit testing.
        """
        last_step: Optional[SearchStep] = None
        for step in self.run():
            last_step = step
        if last_step and last_step.found:
            return last_step.path
        return None
