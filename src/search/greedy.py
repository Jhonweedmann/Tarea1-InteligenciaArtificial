import heapq


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


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
