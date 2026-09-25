from collections import deque
from environment import Environment
from agent import Agent


def bfs(env, start, goal):
    if start == goal:
        return [start]
    visited = set()
    visited.add(start)
    queue = deque([(start, [start])])
    while queue:
        current, path = queue.popleft()
        for nr, nc in env.get_neighbors(current[0], current[1]):
            if (nr, nc) in visited:
                continue
            new_path = path + [(nr, nc)]
            if (nr, nc) == goal:
                return new_path
            visited.add((nr, nc))
            queue.append(((nr, nc), new_path))
    return None


def bfs_search(env, agent_start, exit_pos):
    path = bfs(env, agent_start, exit_pos)
    if path is None:
        return None
    return path[1:]
