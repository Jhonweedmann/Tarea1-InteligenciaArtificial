import heapq
from environment import Environment


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_search(env, start, goal):
    if start == goal:
        return [start]
    open_set = []
    heapq.heappush(open_set, (manhattan(start, goal), 0, start, [start]))
    g_score = {start: 0}
    visited = set()

    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        if current in visited:
            continue
        visited.add(current)
        if current == goal:
            return path[1:]
        for nr, nc in env.get_neighbors(current[0], current[1]):
            tentative_g = g + env.cost(nr, nc)
            neighbor = (nr, nc)
            if neighbor in g_score and tentative_g >= g_score[neighbor]:
                continue
            g_score[neighbor] = tentative_g
            f_score = tentative_g + manhattan(neighbor, goal)
            new_path = path + [(nr, nc)]
            heapq.heappush(open_set, (f_score, tentative_g, neighbor, new_path))
    return None


def greedy_search(env, start, goal):
    if start == goal:
        return [start]
    open_set = []
    heapq.heappush(open_set, (manhattan(start, goal), start, [start]))
    visited = set()

    while open_set:
        h, current, path = heapq.heappop(open_set)
        if current in visited:
            continue
        visited.add(current)
        if current == goal:
            return path[1:]
        for nr, nc in env.get_neighbors(current[0], current[1]):
            if (nr, nc) in visited:
                continue
            new_path = path + [(nr, nc)]
            heapq.heappush(open_set, (manhattan((nr, nc), goal), (nr, nc), new_path))
    return None
