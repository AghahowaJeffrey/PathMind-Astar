# docs/commit_plan.md

## Suggested Incremental Commit Plan

A sensible commit history makes the project readable during code review and
demonstrates that development was structured and intentional.

---

### Stage 1 — Project Initialisation
```
git commit -m "chore: initialise project structure and requirements"
```
**Files:** `requirements.txt`, `.gitignore`, empty module stubs  
**Goal:** Establish the repo skeleton.

---

### Stage 2 — Grid Environment
```
git commit -m "feat(env): implement GridWorld with state, actions, transition model"
```
**Files:** `environment.py`, `constants.py`  
**Goal:** Core AI environment with fully working neighbor expansion and goal test.

---

### Stage 3 — Node Model and Utilities
```
git commit -m "feat(utils): add heuristics, path reconstruction, and Stopwatch"
```
**Files:** `utils.py`  
**Goal:** Manhattan heuristic, `reconstruct_path`, `Stopwatch`, predefined maps.

---

### Stage 4 — A* Algorithm (Core)
```
git commit -m "feat(astar): implement generator-based A* solver"
```
**Files:** `astar.py`  
**Goal:** Correct A* with open/closed sets, g/h/f costs, per-step yielding.

---

### Stage 5 — Path Reconstruction
```
git commit -m "feat(astar): add path reconstruction and SearchStep dataclass"
```
**Files:** `astar.py`  
**Goal:** `SearchStep` snapshot and `reconstruct_path` integration.

---

### Stage 6 — Goal-Based Agent
```
git commit -m "feat(agent): implement GoalBasedAgent with plan/execute lifecycle"
```
**Files:** `agent.py`  
**Goal:** Agent wraps solver; exposes `plan_generator()` and `advance()`.

---

### Stage 7 — Basic pygame Window
```
git commit -m "feat(gui): create pygame window and main event loop skeleton"
```
**Files:** `gui.py`, `main.py`  
**Goal:** Opens a window, handles quit events, nothing more.

---

### Stage 8 — Grid Rendering
```
git commit -m "feat(gui): render grid cells with state-based colouring"
```
**Files:** `gui.py`  
**Goal:** Colours for empty, obstacle, start, goal appear correctly.

---

### Stage 9 — A* Exploration Animation
```
git commit -m "feat(gui): animate A* open/closed set expansion step by step"
```
**Files:** `gui.py`  
**Goal:** Blue open set, purple closed set animate in real time.

---

### Stage 10 — Final Path and Agent Animation
```
git commit -m "feat(gui): animate path reconstruction and agent traversal"
```
**Files:** `gui.py`  
**Goal:** Amber path cells appear; red agent dot walks along path.

---

### Stage 11 — Controls and Statistics Panel
```
git commit -m "feat(gui): add control buttons, stats panel, legend, keyboard shortcuts"
```
**Files:** `gui.py`  
**Goal:** Start/Pause/Reset buttons, speed control, full stats display.

---

### Stage 12 — Predefined Maps
```
git commit -m "feat(maps): add four predefined scenario maps"
```
**Files:** `utils.py`  
**Goal:** Open Field, Maze, Corridors, Random maps selectable in GUI.

---

### Stage 13 — Documentation
```
git commit -m "docs: add README, presentation notes, and Q&A guide"
```
**Files:** `README.md`, `docs/presentation_notes.md`,
           `docs/lecturer_questions_and_answers.md`  
**Goal:** Full academic documentation in place.

---

### Stage 14 — Polish and Final Review
```
git commit -m "chore: final polish, docstrings, type hints, edge case handling"
```
**Files:** All python files  
**Goal:** Presentation-ready state; all edge cases handled.

---

> **Tip:** Use `git log --oneline` during your demo to show the commit history.
> It reinforces that the project was built incrementally and thoughtfully.
