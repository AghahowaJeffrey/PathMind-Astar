# docs/presentation_notes.md
# Presentation Guide: Goal-Based AI Agent Using A* Search

---

## Before the Demo

1. Run `python main.py` 15 minutes before to confirm it works on the demo machine.
2. Set the pygame window to the centre of your screen.
3. Make the terminal visible below or beside the window to show the file structure if asked.
4. Have this file open in a second terminal tab as a script.

---

## 3-Minute Lightning Presentation

> *Read naturally; do not rush.*

**[Slide 1 — Title, 20 seconds]**  
"This project implements a **goal-based AI agent** that uses the **A\* search algorithm** to find the shortest path through a 2D grid environment.  
It demonstrates the core ideas from AI — agents, environments, search, and heuristics — in a live, animated simulation."

**[Slide 2 — The Problem, 20 seconds]**  
"An agent sits on a grid. It has a goal. In between are obstacles. The agent must find an optimal route. It cannot move diagonally. Every step costs 1."

**[Slide 3 — Why A\*, 20 seconds]**  
"A\* is the gold standard for this type of problem. It is **complete** — it always finds a path if one exists. It is **optimal** — it finds the shortest one. And it is efficient because of its heuristic, which focuses the search toward the goal."

**[Live Demo — 90 seconds]**  
- Click **START** and let the algorithm run on the Open Field map.  
- Point to the expanding blue open set: *"These are nodes the algorithm is considering."*  
- Point to the purple closed set: *"These have been fully explored."*  
- When the amber path appears: *"That is the optimal path. The agent will now follow it."*  
- Watch the red dot traverse the path: *"There is the agent — acting on its plan."*

**[Wrap-up — 30 seconds]**  
"The system is modular: the environment, algorithm, and GUI are separate files. You can change the map, adjust the animation speed, and step through the algorithm. This is a clean, academic demonstration of how informed search drives an AI agent."

---

## 5–7 Minute Full Presentation

### Opening (30 sec)
"AI agents are defined by how they make decisions.  
A goal-based agent, unlike a reactive one, doesn't just look at its current state.  
It asks: **what is my goal?  How do I get there?**  
This project builds exactly that kind of agent."

### Background concepts (60–90 sec)
Talk through these briefly:

| Term | One-liner |
|------|-----------|
| Agent | A system that perceives its environment and takes actions |
| Environment | The 2D grid — finite, static, fully observable |
| State | A (row, col) tuple |
| Actions | Up, Down, Left, Right |
| Goal test | Is the agent at the goal cell? |
| Path cost | Number of steps taken |
| Heuristic | Manhattan distance — an educated guess of remaining cost |

### The algorithm (90 sec)
Write on the whiteboard or show on slides:

```
f(n) = g(n) + h(n)

g(n) = exact cost from start to n
h(n) = Manhattan distance from n to goal
f(n) = total estimated cost through n
```

"A\* always pops the node with the lowest f(n) from the priority queue.  
Because the heuristic never *overestimates*, the first path found is guaranteed optimal."

### Live demo (2–3 min)
- Load the **Maze** map (press `2`).
- Start search — let it run slowly enough to narrate.
- *"Watch the blue cells fan out — that's the open set growing."*
- *"Purple cells are done — A\* won't revisit them."*
- *"Notice that the algorithm focuses toward the goal, not uniformly in all directions. That's the heuristic working."*
- Path found → agent moves.

### Code walkthrough (60 sec, optional)
Open terminal, `cat astar.py` or show in editor.  
Highlight the heap pop, the tentative_g check, and the generator `yield`.

### Closing (30 sec)
"The project demonstrates three things:  
1. A goal-based agent architecture.  
2. A correct, animated A\* implementation.  
3. Clean software design — six focused modules, no monolith.  
Questions?"

---

## Handling Difficult Questions on Stage

- **"Why not Dijkstra's?"**  
  Dijkstra is A\* with h=0. It works, but explores uniformly in all directions. A\* is strictly faster in practice on grid maps.

- **"Why not BFS?"**  
  BFS finds the path with fewest *edges* on an unweighted graph. On a uniform grid that's also optimal, but BFS doesn't use a heuristic — it's slower because it doesn't prioritise nodes near the goal.

- **"What if the heuristic is wrong?"**  
  If it overestimates (inadmissible), A\* may return a sub-optimal path. If it underestimates (admissible), A\* is still optimal — Manhattan is always admissible for 4-directional grids.

- **"Can this do diagonal movement?"**  
  Yes — change the ACTIONS list in `environment.py` to include diagonals and switch the heuristic to Chebyshev or Euclidean distance.

- **"How does the agent know the full map?"**  
  It assumes a fully-observable, static environment. For partial observability you'd need a replanning approach like D\*.
