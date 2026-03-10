import heapq
from environment import GridWorld

def astar_on_paper(grid, start, goal):
    """
    Consolidated A* implementation for paper/presentation.
    f(n) = g(n) + h(n)
    """
    # 1. Heuristic function (Manhattan Distance)
    def h(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    # 2. Data Structures
    open_heap = [(h(start), start)]
    g_score = {start: 0}
    came_from = {}
    closed_set = set()

    while open_heap:
        # 3. Pop the node with the lowest f(n)
        f, current = heapq.heappop(open_heap)

        # 4. Goal Test
        if current == goal:
            # Consolidating path reconstruction
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        # 5. Move current to closed set (fully explored)
        closed_set.add(current)

        # 6. Expand Neighbors
        for neighbor, cost in grid.neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + cost

            if tentative_g < g_score.get(neighbor, float('inf')):
                # 7. Update path and costs
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                
                # f(n) = g(n) + h(n)
                f_score = tentative_g + h(neighbor)
                heapq.heappush(open_heap, (f_score, neighbor))
                
    return None

if __name__ == "__main__":
    grid = GridWorld.from_dict({
        "rows": 10,
        "cols": 10,
        "start": (0, 0),
        "goal": (3, 3), # Shortened for quick print
        "obstacles": [(1, 1), (1, 2), (1, 3)]
    })
    path = astar_on_paper(grid, (0, 0), (3, 3))
    print(f"Path found: {path}")