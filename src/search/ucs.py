import heapq
from environment import Environment
from agent import Agent


def ucs_search(env, start, goal):
    if start == goal:
        return [start]
    visited = set()
    pq = [(0, start, [start])]
    while pq:
        cost, current, path = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        if current == goal:
            return path[1:]
        for nr, nc in env.get_neighbors(current[0], current[1]):
            if (nr, nc) in visited:
                continue
            new_cost = cost + env.cost(nr, nc)
            new_path = path + [(nr, nc)]
            heapq.heappush(pq, (new_cost, (nr, nc), new_path))
    return None
