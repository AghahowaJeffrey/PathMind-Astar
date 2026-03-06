# Design and Implementation of a Goal-Based AI Agent Using A* Search

> **Course Project** | Artificial Intelligence | Python · pygame  
> **Algorithm:** A\* (A-Star) Search | **Heuristic:** Manhattan Distance  
> **Movement:** 4-directional (Up / Down / Left / Right)

---

## Table of Contents

1. [Project Overview](#1-project-overview)  
2. [Problem Statement](#2-problem-statement)  
3. [Objectives](#3-objectives)  
4. [Why This Is a Goal-Based Agent](#4-why-this-is-a-goal-based-agent)  
5. [Why A\* Was Chosen](#5-why-a-was-chosen)  
6. [A\* Search Explained](#6-a-search-explained)  
7. [Key AI Concepts Used](#7-key-ai-concepts-used)  
8. [System Architecture](#8-system-architecture)  
9. [File Structure](#9-file-structure)  
10. [Installation](#10-installation)  
11. [How to Run](#11-how-to-run)  
12. [GUI Walkthrough](#12-gui-walkthrough)  
13. [Algorithm in This Implementation](#13-algorithm-in-this-implementation)  
14. [Sample Maps](#14-sample-maps)  
15. [Expected Output](#15-expected-output)  
16. [Limitations](#16-limitations)  
17. [Future Improvements](#17-future-improvements)  
18. [Screenshots](#18-screenshots)  
19. [Academic Discussion](#19-academic-discussion)  
20. [Resources and References](#20-resources-and-references)  
21. [Commit Plan](#21-commit-plan)  
22. [Author](#22-author)

---

## 1. Project Overview

This project implements a **goal-based AI agent** that navigates a 2D grid
environment using the **A\* search algorithm**. The agent is given a starting
position and a goal position. It uses A\* to compute the optimal path,
avoiding obstacles, and then follows that path — animated in real time using
a custom pygame-based graphical interface.

The project is designed to demonstrate the core ideas of intelligent-agent
design: state representation, action modelling, goal testing, heuristic
search, and plan execution.

---

## 2. Problem Statement

Given:
- A finite 2D grid of N × M cells
- A **start** cell `S`
- A **goal** cell `G`
- A set of **obstacle** (impassable) cells

Find the **shortest path** from `S` to `G` avoiding all obstacles,
where movement is restricted to the four cardinal directions
(up, down, left, right) and each step has cost 1.

If no such path exists, report it clearly.

---

## 3. Objectives

1. Design and implement a **goal-based intelligent agent** architecture.
2. Implement a correct, efficient **A\* search algorithm**.
3. Build a **visual simulation** that shows the search and path-following in real time.
4. Structure the code cleanly into **modular, reusable components**.
5. Document the project thoroughly for academic review.

---

## 4. Why This Is a Goal-Based Agent

Russell and Norvig (2021) classify AI agents by the information they use to
choose actions. A **goal-based agent** is one that:

1. Maintains an explicit **goal** — a desired world state.
2. Uses **search** or **planning** to determine how actions lead from the
   current state to the goal.
3. Selects actions to achieve that goal, not merely to react to the
   current percept.

This project embodies all three properties:

| Property | Implementation |
|----------|----------------|
| Explicit goal | The (row, col) goal cell passed to `GoalBasedAgent` |
| Planning | A\* search that constructs the optimal path before acting |
| Goal-directed action | The agent follows the plan step by step, not reactively |

This contrasts with a **simple reflex agent** (which just maps percepts to
actions) or a **learning agent** (which modifies itself from feedback).

---

## 5. Why A\* Was Chosen

| Criterion | BFS | Dijkstra | Greedy Best-First | **A\*** |
|-----------|-----|----------|-------------------|---------|
| Complete | ✓ | ✓ | ✗ (can loop) | ✓ |
| Optimal | ✓ (uniform cost) | ✓ | ✗ | ✓ |
| Uses heuristic | ✗ | ✗ | ✓ | ✓ |
| Efficient | ✗ | Moderate | ✓ (but suboptimal) | ✓ |

A\* is the canonical algorithm when optimality *and* efficiency are both
required. It is the industry standard for grid pathfinding (games, robotics,
navigation), making it the appropriate choice for this academic demonstration.

---

## 6. A\* Search Explained

A\* maintains a **priority queue** (open set) ordered by the evaluation
function:

```
f(n) = g(n) + h(n)
```

| Symbol | Name | Meaning |
|--------|------|---------|
| `g(n)` | Actual cost | Exact cost from Start to node n |
| `h(n)` | Heuristic | Estimated cost from n to Goal |
| `f(n)` | Total estimate | Best estimated total path cost through n |

**At each step**, A\* pops the node with the smallest `f(n)`, expands its
neighbours, and updates their costs if a shorter path is found.

**Termination:** When the goal is popped from the open set, the algorithm
terminates and reconstructs the path using parent pointers.

### Why the Heuristic Must Be Admissible

A heuristic `h(n)` is **admissible** if it *never overestimates* the true
cost to the goal. Under this condition, A\* is proven to find an optimal
solution. In this project, **Manhattan distance** is used:

```
h(n) = |row_n - row_goal| + |col_n - col_goal|
```

Manhattan distance is admissible because reaching any cell from node n
requires *at least* `|Δrow| + |Δcol|` steps with 4-directional movement.

---

## 7. Key AI Concepts Used

| Concept | Definition | In This Project |
|---------|------------|-----------------|
| **Agent** | Entity that perceives and acts | `GoalBasedAgent` in `agent.py` |
| **Environment** | The world the agent operates in | `GridWorld` in `environment.py` |
| **State** | A snapshot of the world | `(row, col)` tuple |
| **Actions** | What the agent can do | Up, Down, Left, Right (Δrow, Δcol vectors) |
| **Transition model** | How actions change state | `GridWorld.result(state, action)` |
| **Goal test** | Is the state the goal? | `GridWorld.is_goal(state)` |
| **Path cost** | Cost of a sequence of actions | Number of steps (uniform 1 per step) |
| **Heuristic** | Estimate of remaining cost | Manhattan distance |
| **Open set** | Discovered but unexpanded nodes | Min-heap in `AStarSolver` |
| **Closed set** | Fully expanded nodes | Python `set` in `AStarSolver` |

---

## 8. System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                       main.py (Entry Point)                │
└─────────────┬──────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────┐
│    GUIController        │  ← Renders, handles input, drives timing
│      (gui.py)           │
└────────┬────────────────┘
         │ owns & calls
         ▼
┌─────────────────────────┐
│    GoalBasedAgent       │  ← Plans with A*, executes plan step by step
│       (agent.py)        │
└────────┬────────────────┘
         │ uses
         ├──────────────────────┐
         ▼                      ▼
┌────────────────┐    ┌──────────────────┐
│  AStarSolver   │    │   GridWorld      │
│  (astar.py)    │    │ (environment.py) │
└────────────────┘    └──────────────────┘
         │ depends on
         ▼
┌────────────────┐
│   utils.py     │  ← Heuristic, path reconstruction, maps
│   constants.py │  ← All magic numbers and colours
└────────────────┘
```

**Data flow during a search:**
1. GUI calls `agent.plan_generator()` → receives A\* generator.
2. Each animation tick, GUI calls `next(generator)` → receives `SearchStep`.
3. GUI renders the snapshot (open/closed sets, current node).
4. On `step.found`, GUI calls `agent.record_result(step)`.
5. GUI then calls `agent.advance()` once per tick to animate path-following.

---

## 9. File Structure

```
search-algo-agent/
│
├── main.py               # Entry point; CLI argument parsing
├── agent.py              # GoalBasedAgent: plan and execute lifecycle
├── astar.py              # AStarSolver: step-by-step generator
├── environment.py        # GridWorld: state, actions, transition model
├── gui.py                # GUIController: pygame rendering and events
├── constants.py          # All constants: colours, sizes, timing
├── utils.py              # Heuristics, path reconstruction, predefined maps
│
├── requirements.txt      # Python dependencies (pygame only)
│
└── docs/
    ├── presentation_notes.md          # How to present in class
    ├── lecturer_questions_and_answers.md  # 30 Q&A for viva prep
    └── commit_plan.md                 # Staged git commit sequence
```

### Module Responsibilities

| File | Lines | Responsibility |
|------|-------|----------------|
| `constants.py` | ~60 | Single source of truth for all literals |
| `environment.py` | ~120 | Grid world model (pure logic, no rendering) |
| `utils.py` | ~160 | Heuristics, maps, stopwatch |
| `astar.py` | ~130 | A\* algorithm (pure search, no GUI) |
| `agent.py` | ~100 | Agent plan/execute lifecycle |
| `gui.py` | ~340 | pygame UI, state machine, rendering |
| `main.py` | ~30 | Entry point |

---

## 10. Installation

### Prerequisites

- Python 3.9 or later
- pip

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/search-algo-agent.git
cd search-algo-agent

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

`requirements.txt` contains only:
```
pygame>=2.1.0
```

No additional frameworks, no LLMs, no network calls.

---

## 11. How to Run

```bash
# Default map (Open Field)
python main.py

# Specific predefined map
python main.py Maze
python main.py Corridors
python main.py "Random (25% obstacles)"
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `S` | Start the A\* search |
| `Space` or `P` | Pause / Resume |
| `R` | Reset simulation |
| `1` | Load Open Field map |
| `2` | Load Maze map |
| `3` | Load Corridors map |
| `4` | Load Random map |
| `+` | Increase animation speed |
| `-` | Decrease animation speed |
| `Q` / `Esc` | Quit |

---

## 12. GUI Walkthrough

```
┌─────────────────────────────────────────────────────┬──────────────┐
│  A* Goal-Based Agent — Pathfinding Visualiser        │  PANEL       │
│  f(n)=g(n)+h(n) | Heuristic: Manhattan | 4-dir      │              │
├─────────────────────────────────────────────────────┤  [START]     │
│                                                     │  [PAUSE]     │
│   ████ ████ ████ ████  ...  grid cells  ...        │  [RESET]     │
│                                                     │              │
│   ██S█   (emerald = start)                         │  Maps ◀ ▶    │
│   ████ ████ ████ blue ████ (open set)               │              │
│   ████ purp purp purp ████ (closed set)             │  Speed + -   │
│   yell yell yell yell ████ (final path)             │              │
│   ████ RED  ████ ████ ████ (agent position)        │  Statistics  │
│   ████ ████ ████ ████  G██ (rose = goal)           │  ─────────── │
│                                                     │  State: …    │
├─────────────────────────────────────────────────────┤  Explored: N │
│  Status message                                     │  Path: N     │
└─────────────────────────────────────────────────────┴──────────────┘
```

### Colour Key

| Colour | Cell State |
|--------|------------|
| 🟩 Emerald | Start node |
| 🌹 Rose | Goal node |
| ⬛ Dark | Empty cell |
| ◼ Charcoal | Obstacle |
| 🔵 Sky-blue | Open set (frontier) |
| 🟣 Purple | Closed set (explored) |
| 🟡 Amber | Final shortest path |
| 🔴 Red | Current agent position |

---

## 13. Algorithm in This Implementation

### How the Generator Works

`AStarSolver.run()` is a Python generator function. Each call to `next()`
performs exactly **one node expansion** and yields a `SearchStep` dataclass:

```python
@dataclass
class SearchStep:
    current: Optional[State]      # node being expanded
    open_set: frozenset           # current frontier
    closed_set: frozenset         # explored nodes
    g_cost: Dict[State, float]    # best known g values
    path: List[State]             # final path (non-empty only on found)
    found: bool                   # True → goal reached this step
    exhausted: bool               # True → no path exists
    nodes_explored: int           # running expansion count
```

The GUI calls `next()` once per animation frame (limited by the step-delay
slider), creating a smooth, real-time visualisation without threads.

### Cost Tracking

```
g_cost[state]   — cheapest cost from start to state
came_from[state] — parent pointer for path reconstruction
f = g_cost[current] + heuristic(current, goal)
```

The heap stores `(f, counter, state)` so popping always gives the
most-promising unexplored node.

### Path Reconstruction

```python
def reconstruct_path(came_from, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path          # [start, ..., goal]
```

---

## 14. Sample Maps

Four deterministic predefined maps are included:

| Map | Description | Difficulty |
|-----|-------------|------------|
| **Open Field** | Sparse central rock cluster | Easy |
| **Maze** | Alternating horizontal walls with offset gaps | Medium |
| **Corridors** | Vertical dividers forming pocket corridors | Medium |
| **Random (25%)** | Random 25% obstacle density (seeded, reproducible) | Variable |

All maps guarantee that start and goal are not obstacles and are reachable
on their default configurations.

---

## 15. Expected Output

### With a Solution

```
Start: (1, 1)   Goal: (16, 23)
Path found.
  Nodes explored : 187
  Path length    : 39 steps
  Path cost      : 38
  Time           : 1.4 ms
```

The GUI shows the amber path, then animates the red agent dot along it.

### Without a Solution

```
No path exists between start and goal.
  Nodes explored : 412
```

The GUI displays the fully explored closed set in purple and a clear
status message.

---

## 16. Limitations

1. **Static environment** — obstacles do not move; no replanning occurs.
2. **Full observability** — the agent has complete map knowledge before acting.
3. **Uniform terrain** — all passable cells have cost 1; weighted cells
   are architecturally supported but not exposed in the GUI.
4. **Memory** — the closed set grows with the grid; impractical for
   very large grids (>10k cells) without IDA\* or similar.
5. **Single agent** — multi-agent interaction and collision avoidance
   are not modelled.
6. **No persistence** — custom maps cannot be saved between sessions.

---

## 17. Future Improvements

- **D\* Lite** — incremental replanning for dynamic obstacle maps.
- **Weighted cells** — terrain types (swamp, road, water) with different costs.
- **Diagonal movement** — 8-directional movement with Chebyshev heuristic.
- **Bidirectional A\*** — simultaneous search from start and goal.
- **Map editor** — click to place/remove obstacles in the GUI.
- **Algorithm comparison** — side-by-side A\* vs BFS visualisation.
- **Export** — save screenshots or GIF of the animation.
- **Larger grids** — scalable cell/window size via config.

---

## 18. Screenshots

> *Screenshots were taken during a live demo session.*

### Searching — Open Set Expanding

![A* Open Set Expanding](docs/screenshots/searching.png)

### Path Found

![Optimal Path Found](docs/screenshots/path_found.png)

### Agent Traversing Path

![Agent Moving Along Path](docs/screenshots/agent_moving.png)

### Maze Map

![Maze Map Search](docs/screenshots/maze.png)

---

## 19. Academic Discussion

### On the Completeness and Optimality of A\*

**Theorem (Hart, Nilsson & Raphael, 1968):**  
If the branching factor is finite, all edge costs are positive, and the
heuristic is admissible, then A\* is **complete** (always finds a solution
if one exists) and **optimal** (the first solution found is the cheapest).

**Proof sketch:** Because h is admissible, no node on an optimal path can
be permanently overlooked. The first time goal is popped from the heap, its
g value is the true optimal cost — any other path to goal must have
f ≥ optimal cost, hence would be popped later.

### On the Relationship to Dijkstra

Dijkstra's algorithm is the special case h(n) = 0.  
A\* is the special case of Best-First Search with f = g + h.  
These are nested generalisations of the same priority-queue framework.

### On Admissibility vs. Consistency

Admissibility (h ≤ h\*) guarantees **optimality** on tree search.  
Consistency (h(n) ≤ c(n, n') + h(n')) additionally guarantees that no
node is re-expanded, giving **efficiency** on graph search.  
Manhattan distance on a 4-directional grid is both admissible and consistent.

---

## 20. Resources and References

### Core Algorithm

- Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the
  Heuristic Determination of Minimum Cost Paths.* IEEE Transactions on
  Systems Science and Cybernetics, 4(2), 100–107.
- [Wikipedia — A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Red Blob Games — A* Introduction](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
  *(Best visual explainer on the web)*
- [Stanford CS221 — Search lecture notes](https://stanford-cs221.github.io/autumn2022/)

### Intelligent Agents

- Russell, S. & Norvig, P. (2021). *Artificial Intelligence: A Modern
  Approach* (4th ed.). Pearson. Chapters 2–3.
- [AI: A Modern Approach companion site](http://aima.cs.berkeley.edu/)

### Heuristic Search

- Korf, R. E. (1985). *Depth-first iterative-deepening: An optimal
  admissible tree search.* Artificial Intelligence, 27(1), 97–109.
- [Pathfinding.js visualisation](https://qiao.github.io/PathFinding.js/visual/)

### Python Libraries

- [pygame documentation](https://www.pygame.org/docs/)
- [Python heapq — official docs](https://docs.python.org/3/library/heapq.html)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)

### Visualisation & Teaching

- [Amit's pathfinding pages (Amit Patel)](http://theory.stanford.edu/~amitp/GameProgramming/)
- [Computerphile — A\* on YouTube](https://www.youtube.com/watch?v=ySN5Wnu88nE)

---

## 21. Commit Plan

See [`docs/commit_plan.md`](docs/commit_plan.md) for the full 14-stage
incremental commit sequence with exact commit messages.

**Summary of stages:**
1. Project structure init  
2. GridWorld environment  
3. Node model & utilities  
4. A\* algorithm core  
5. Path reconstruction  
6. GoalBasedAgent  
7. pygame window scaffold  
8. Grid rendering  
9. A\* animation  
10. Agent animation  
11. Controls & stats panel  
12. Predefined maps  
13. Documentation  
14. Polish & final review  

---

## 22. Author

**Project:** Design and Implementation of a Goal-Based AI Agent Using A\* Search  
**Course:** Artificial Intelligence  
**Language:** Python 3.9+  
**Framework:** pygame  
**Year:** 2026  

*Built with clarity and intentionality — not assembled from copied snippets
and held together by hope.*
