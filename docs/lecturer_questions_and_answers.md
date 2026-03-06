# docs/lecturer_questions_and_answers.md
# Likely Lecturer Questions and Model Answers

*This document covers 30 questions a lecturer or examiner is likely to ask
during a viva, demonstration, or written assessment of this project.*

---

## 1. What is an AI agent?

**Answer:**  
An AI agent is any entity that perceives its environment through *sensors*,
processes that perception, and takes *actions* through actuators to affect
the environment (Russell & Norvig, *Artificial Intelligence: A Modern Approach*).
Critically, an agent acts on behalf of an objective — it is goal-directed,
not merely reactive.

---

## 2. What makes this agent *goal-based*?

**Answer:**  
A goal-based agent differs from a simple reflex agent in that it maintains
an explicit representation of desired outcomes (a goal state) and chooses
actions specifically to achieve that goal. In this project:

- The goal is a specific (row, col) position on the grid.
- The agent uses A\* to *plan* a sequence of actions that reaches the goal.
- It acts by executing that plan, not by reacting to each percept independently.

This is the defining property of a goal-based agent: deliberate planning
toward a declared objective.

---

## 3. Why A\* instead of BFS or DFS?

**Answer:**  

| Algorithm | Complete | Optimal | Uses heuristic |
|-----------|----------|---------|----------------|
| DFS       | No (cycles) | No   | No             |
| BFS       | Yes      | Yes (unit costs) | No    |
| A\*       | Yes      | Yes     | Yes            |

- **DFS** is neither complete nor optimal — it can follow an infinite branch.
- **BFS** is optimal on uniform-cost grids but explores cells in concentric
  rings, ignoring the direction of the goal.
- **A\*** exploits the heuristic to prioritise nodes closer (in estimated cost)
  to the goal, making it significantly faster than BFS in practice while
  maintaining optimality guarantees.

---

## 4. What is the role of the heuristic?

**Answer:**  
The heuristic `h(n)` provides an *estimate* of the remaining cost from node
`n` to the goal. It is used to compute `f(n) = g(n) + h(n)`, which is the
priority key in the open-set heap. A good heuristic focuses the search towards
the goal rather than expanding nodes uniformly, dramatically reducing the
number of nodes explored.

---

## 5. What happens if the heuristic overestimates?

**Answer:**  
The heuristic becomes **inadmissible**. A\* may return a path that is *not*
the shortest, because it might prematurely close optimal nodes in favour of
nodes that only *appear* cheaper due to the inflated estimate. The algorithm
remains complete but loses its optimality guarantee.

---

## 6. Is A\* always optimal?

**Answer:**  
A\* is optimal **if and only if the heuristic is admissible** (never
overestimates). On a uniform-cost grid with Manhattan distance as the
heuristic, Manhattan distance is provably admissible because moving to any
cell requires at least `|Δrow| + |Δcol|` steps. Therefore this implementation
is always optimal in the given environment.

---

## 7. What is the difference between informed and uninformed search?

**Answer:**  
- **Uninformed (blind) search** — BFS, DFS, Uniform-Cost Search — has no
  knowledge about how far it is from the goal. It can only distinguish
  states by their cost so far.
- **Informed (heuristic) search** — Best-First, A\*, Greedy — uses a
  domain-specific heuristic to estimate remaining cost and prioritise
  promising nodes first.

A\* is the canonical informed search algorithm.

---

## 8. What are the limitations of your implementation?

**Answer:**  
1. **Static environment** — the grid is fixed; the agent cannot replan for
   moving obstacles.
2. **Full observability** — the agent sees the entire map. Real-world agents
   often cannot.
3. **Uniform step cost** — all moves cost 1. Weighted terrain is not
   supported (though the architecture allows it via `step_cost()`).
4. **Memory** — A\*'s closed set grows linearly with the number of expanded
   nodes. On very large grids this becomes significant.
5. **No multi-agent support** — only one agent operates at a time.

---

## 9. Can this work in a dynamic environment?

**Answer:**  
Not without modification. A\* assumes a static environment. If obstacles
move, the planned path becomes invalid. Possible extensions include:

- **Replanning A\*** — re-run A\* whenever the environment changes.
- **D\* Lite** — an incremental algorithm designed for dynamic environments
  that repairs the existing plan efficiently.
- **Real-Time A\* (RTA\*)** — the agent plans locally and replans at each step.

---

## 10. What is the time complexity of A\*?

**Answer:**  
In the worst case, A\* has time complexity **O(b^d)** where `b` is the
branching factor and `d` is the depth of the solution. With an effective
heuristic, the effective branching factor is reduced, often dramatically.
For a grid with `N` cells, the worst case is **O(N log N)** due to the
heap operations. In practice, with Manhattan distance, A\* explores far
fewer nodes than BFS.

---

## 11. What is the space complexity of A\*?

**Answer:**  
**O(N)** where N is the number of nodes — A\* must keep the entire search
frontier (open set) and the visited nodes (closed set) in memory. This is
A\*'s main practical limitation on very large grids. Memory-bounded variants
like IDA\* reduce space to O(d) at the cost of re-expanding nodes.

---

## 12. Why is Manhattan distance appropriate here?

**Answer:**  
Manhattan distance (`|Δrow| + |Δcol|`) is appropriate because:

1. **4-directional movement** — the agent can only move up/down/left/right.
   It cannot "cut corners" diagonally.
2. **Admissibility** — for 4-directional movement, Manhattan distance equals
   the *exact* cost in an obstacle-free grid, so it never overestimates.
3. **Consistency** — `h(n) ≤ step_cost(n, n') + h(n')` for all successors
   `n'`, guaranteeing that A\* never re-opens closed nodes.

Using Euclidean distance would still be admissible but would be a weaker
(less informed) heuristic.

---

## 13. What would change if diagonal movement were allowed?

**Answer:**  
Two things change:

1. **Actions** — extend `ACTIONS` in `environment.py` from 4 to 8 vectors
   (including the four diagonals).
2. **Heuristic** — Manhattan distance becomes inadmissible. Replace it with
   **Chebyshev distance** `max(|Δrow|, |Δcol|)` for uniform diagonal cost,
   or **Euclidean distance** for true diagonal step cost `√2`.

The rest of the architecture (A\* solver, agent, GUI) requires no changes.

---

## 14. What data structure did you use for the priority queue?

**Answer:**  
Python's `heapq` module (a **binary min-heap**). The heap stores `_HeapItem`
objects ordered by `f(n)`. Heap operations are:

- **Push** — O(log n)
- **Pop minimum** — O(log n)
- **Peek** — O(1)

A tie-breaking counter is included in each item to ensure FIFO ordering
when two nodes have identical `f` values, preventing non-determinism.

---

## 15. How does the agent know the environment?

**Answer:**  
This implementation assumes **full observability** — the agent has a complete
model of the grid (dimensions, obstacle positions, start, goal) before
planning begins. This is encoded in the `GridWorld` class, which is passed
to the `GoalBasedAgent` at construction. This is realistic for many planning
problems (e.g. indoor navigation with a map) but not for all (e.g. unknown
terrain exploration).

---

## 16. What happens if no path exists?

**Answer:**  
When A\*'s open set empties without finding the goal, the generator yields
a final `SearchStep` with `exhausted=True` and `found=False`. The GUI
transitions to the `NO_PATH` state and displays the message *"No path exists
between start and goal."* The agent's `plan_found` attribute is set to
`False` and no movement animation occurs.

---

## 17. How is this different from reinforcement learning?

**Answer:**  

| Property | A\* / Classical planning | Reinforcement Learning |
|----------|--------------------------|------------------------|
| Model required | Yes (full map) | No (learns from interaction) |
| Training needed | No | Yes |
| Optimality | Guaranteed (given admissible h) | Asymptotically, with enough training |
| Speed | Instant for static problems | Slow convergence |
| Adaptability | Static environments | Dynamic, unknown environments |

A\* is a *search* algorithm — it solves a known problem exactly. RL learns a
*policy* through trial and error in an unknown environment. They solve
different problem classes.

---

## 18. What are open and closed sets?

**Answer:**  
- **Open set** — the *frontier*: nodes that have been *discovered* but not
  yet fully *expanded*. A\* always expands the lowest-f node in this set.
  Implemented as a min-heap.
- **Closed set** — fully expanded nodes. A\* will not re-expand these (when
  using a consistent heuristic), guaranteeing that each node is processed
  at most once.

In the GUI, open = blue, closed = purple.

---

## 19. How do you reconstruct the final path?

**Answer:**  
During search, each node stores its *parent* — the node from which it was
discovered with the lowest cost. This forms a chain of parent pointers:
`goal → ... → start`. At the end, `reconstruct_path()` in `utils.py`
walks this chain from goal back to start (the start has parent = `None`)
and reverses the result to get a start-to-goal ordered list.

---

## 20. How can this be applied in the real world?

**Answer:**  
A\* is used in:

1. **Game AI** — NPC navigation in games like StarCraft and many others.
2. **Robotics** — motion planning for autonomous robots (e.g. warehouse robots).
3. **GPS navigation** — road network route finding (often with variants like
   bidirectional A\* or Contraction Hierarchies at scale).
4. **VLSI design** — wire routing in circuit layouts.
5. **Natural language processing** — decoding in statistical parsers.

The grid environment here is a simplified abstraction of these real problems.

---

## 21. What is f(n) = g(n) + h(n) and why does it work?

**Answer:**  
`g(n)` is the *exact* cost of the path found so far from start to `n`.
`h(n)` is the *estimated* remaining cost from `n` to goal.
`f(n)` is therefore the *total estimated cost* of the best path through `n`.

A\* always expands the node with the smallest `f(n)`, meaning it always
explores the most *promising* path first. Because `h` is admissible,
the first time A\* reaches the goal it has found the true optimal path —
no other unexpanded path could be better.

---

## 22. What is the difference between A\* and Dijkstra's algorithm?

**Answer:**  
Dijkstra's algorithm is equivalent to A\* with `h(n) = 0` (no heuristic).
It always finds the optimal path but expands nodes in order of `g(n)` only,
searching uniformly outward from the start.  
A\* adds `h(n)` to bias expansion toward the goal, making it faster while
maintaining the same correctness guarantees.

---

## 23. What is IDA\*?

**Answer:**  
Iterative Deepening A\* (IDA\*) is a memory-efficient variant that uses
depth-limited DFS with an `f`-value cutoff, increasing the cutoff
iteratively. It uses **O(d)** space instead of O(N) but re-expands nodes
multiple times. Useful when memory is the bottleneck, e.g. on embedded systems.

---

## 24. What is a consistent (monotone) heuristic?

**Answer:**  
A heuristic is **consistent** if for every node `n` and successor `n'`:
```
h(n) ≤ step_cost(n, n') + h(n')
```
This is the triangle inequality applied to heuristic values.
Consistency implies admissibility, and it guarantees that `f(n)` is
non-decreasing along any path A\* explores, so the algorithm never needs
to re-open a closed node.

Manhattan distance is consistent for 4-directional uniform grids.

---

## 25. How does your code separate concerns?

**Answer:**  
The project uses six modules, each with a single clear responsibility:

| Module | Responsibility |
|--------|----------------|
| `constants.py` | All configuration values — one place to change anything |
| `environment.py` | Grid model — state space, moves, goal test |
| `utils.py` | Pure functions — heuristic, path reconstruction, maps |
| `astar.py` | Search algorithm only — no GUI, no agent lifecycle |
| `agent.py` | Agent lifecycle — plan phase and execute phase |
| `gui.py` | Rendering and user interaction only |

This separation means the algorithm can be tested without pygame installed,
and the GUI can be swapped (e.g. to tkinter) without changing any logic.

---

## 26. How do you handle ties in f values on the heap?

**Answer:**  
Two nodes can have the same `f` value. Without tie-breaking, Python's heap
would compare the states (tuples), which is technically fine but
non-deterministic in ordering effect. Instead, a monotonically increasing
`counter` is included as the second element of each `_HeapItem`. This
produces FIFO ordering among equal-f nodes, ensuring deterministic, stable
results across runs.

---

## 27. Why is the solver implemented as a generator?

**Answer:**  
The GUI must animate the search without blocking the event loop. A generator
(using `yield`) does this elegantly:

- It runs one expansion per `next()` call.
- The GUI calls `next()` once per animation tick.
- No threads or complex state machines are needed.
- The whole algorithm remains in a single, readable function in `astar.py`.

---

## 28. What is the branching factor in this implementation?

**Answer:**  
The maximum branching factor is **4** (up/down/left/right). At grid borders
it is reduced by 1–2; at corners it is 2. This bounded branching factor
means A\* is practical even on large grids.

---

## 29. Can your agent handle weighted cells?

**Answer:**  
The architecture supports it. `GridWorld.step_cost()` is a separate method
that returns 1 for all cells currently. To add weighted terrain, override
this method to return different costs based on the cell type (e.g. mud = 3,
water = 5). A\* will automatically find the minimum-cost path because `g(n)`
accumulates actual step costs.

---

## 30. What would you change or improve given more time?

**Answer:**  
1. **D\* Lite** for dynamic replanning when obstacles change.
2. **Weighted cells** — terrain types with different movement costs.
3. **Bidirectional A\*** — simultaneously search from both start and goal to
   roughly halve the search space.
4. **Multiple agents** — cooperative pathfinding to avoid agent collisions.
5. **Performance benchmarks** — compare A\* vs BFS vs Greedy side by side
   on the same map with live statistics.
6. **Export** — screenshot or GIF export for reports.

---

*References: Russell, S. & Norvig, P. (2021). Artificial Intelligence: A Modern Approach (4th ed.). Pearson.*
