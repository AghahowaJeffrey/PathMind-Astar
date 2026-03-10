# A* Algorithm: Core Logic Breakdown

This document segments the A* implementation into its fundamental components for educational review. 

## 1. The Environment (The Search Space)
The environment defines the "rules" of the world: what states exist and how we move between them. In our case, it's a **GridWorld**.

```python
class GridWorld:
    # State: (row, col)
    # Actions: Up, Down, Left, Right
    
    def neighbors(self, state):
        """Yield (next_state, cost) for legal moves."""
        for action in ACTIONS:
            next_state = self.result(state, action)
            if next_state:
                yield next_state, MOVE_COST # Usually 1
```

## 2. The Heuristic ($h(n)$)
The "educated guess" of the distance from a node to the goal. We use **Manhattan Distance** ($L_1$ norm) for grid-based movement.

```python
def h(pos):
    # |x1 - x2| + |y1 - y2|
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
```

## 3. Priority Queue & State Initialization
We use a **min-heap** (`open_heap`) to always visit the node with the lowest $f(n) = g(n) + h(n)$ first.

```python
# (f_score, position)
open_heap = [(h(start), start)] 
g_score = {start: 0}   # Cost from start to current node
came_from = {}         # For path reconstruction
closed_set = set()     # Nodes already fully explored
```

## 4. The Main Loop & Exploration
While we have nodes to visit, we pop the "best" one and expand its neighbors.

```python
while open_heap:
    f, current = heapq.heappop(open_heap) # Get node with lowest f(n)
    
    if current == goal:
        return reconstruct_path(current) # Success!

    closed_set.add(current) # Mark as explored

    for neighbor, cost in grid.neighbors(current):
        if neighbor in closed_set: continue
        
        # New cost = current path cost + edge cost
        tentative_g = g_score[current] + cost
        
        if tentative_g < g_score.get(neighbor, float('inf')):
            # This path is better! Record it.
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            
            # f(n) = g(n) + h(n)
            f_score = tentative_g + h(neighbor)
            heapq.heappush(open_heap, (f_score, neighbor))
```

## 5. Path Reconstruction
Backtracking from the goal to the start using the `came_from` mapping.

```python
path = []
while current in came_from:
    path.append(current)
    current = came_from[current]
path.reverse()
```

## 6. Entry Point (`main.py`)
The `main.py` file serves as the entry point, handling user input (CLI arguments) and initializing the GUI.

```python
def main():
    # 1. Handle Command Line Arguments
    map_name = "Open Field" 
    if len(sys.argv) > 1:
        map_name = sys.argv[1]

    # 2. Initialize and Run the Controller
    app = GUIController(map_name=map_name)
    app.run()
```

## 7. The Visualiser (`gui.py`)
The GUI uses **pygame** to render the search process in real-time. It separates logical state from visual representation.

```python
class GUIController:
    def run(self):
        """Main application loop."""
        while self.running:
            self._handle_events() # Inputs
            self._update()        # Logic (inc. A* steps)
            self._render()        # Visuals (pygame.draw)

    def _draw_grid(self):
        """Renders cells based on their A* state."""
        for r in range(self.rows):
            for c in range(self.cols):
                color = self._cell_color(r, c)
                pygame.draw.rect(self.screen, color, rect)
```
