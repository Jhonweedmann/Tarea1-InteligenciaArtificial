import random
from collections import deque


class CellType:
    FREE = "free"
    WALL = "wall"
    FIRE = "fire"
    EXIT = "exit"
    AGENT = "agent"


class Environment:
    def __init__(self, grid, fire_propagation_interval=3, congestion_k=0.1, fire_seed=None, num_agents=80):
        self.grid = [row[:] for row in grid]
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.fire_propagation_interval = fire_propagation_interval
        self.congestion_k = congestion_k
        self.fire_turn = 0
        self.agent_positions = {}
        self.exit_pos = None
        self.num_agents = num_agents
        self._parse_grid()
        self._place_agents_randomly(num_agents)
        self._add_random_fire(fire_seed)

    def _parse_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell == CellType.EXIT:
                    self.exit_pos = (r, c)
                elif cell == CellType.AGENT:
                    self.grid[r][c] = CellType.FREE

    def _add_random_fire(self, seed):
        if seed is None:
            return
        rng = random.Random(seed)
        fire_cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == CellType.FREE and rng.random() < 0.05:
                    self.grid[r][c] = CellType.FIRE
                    fire_cells.append((r, c))
        if not self._has_path():
            rng.shuffle(fire_cells)
            for (r, c) in fire_cells:
                self.grid[r][c] = CellType.FREE
                if self._has_path():
                    break

    def _place_agents_randomly(self, num_agents):
        free_cells = self.get_free_cells()
        if not free_cells:
            return
        rng = random.Random(42)
        for _ in range(num_agents):
            pos = rng.choice(free_cells)
            self.agent_positions[pos] = self.agent_positions.get(pos, 0) + 1

    def _has_path(self):
        if self.exit_pos is None:
            return False
        start_pos = None
        for pos, count in self.agent_positions.items():
            if count > 0:
                start_pos = pos
                break
        if start_pos is None:
            return False
        visited = set()
        visited.add(start_pos)
        queue = deque([start_pos])
        while queue:
            current = queue.popleft()
            if current == self.exit_pos:
                return True
            for nr, nc in self.get_neighbors(current[0], current[1]):
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return False

    def move_agent(self, old_pos, new_pos):
        if old_pos in self.agent_positions:
            self.agent_positions[old_pos] -= 1
            if self.agent_positions[old_pos] <= 0:
                del self.agent_positions[old_pos]
        self.agent_positions[new_pos] = self.agent_positions.get(new_pos, 0) + 1

    def remove_agent(self, pos):
        if pos in self.agent_positions:
            self.agent_positions[pos] -= 1
            if self.agent_positions[pos] <= 0:
                del self.agent_positions[pos]

    def get_occupation(self, r, c):
        return self.agent_positions.get((r, c), 0)

    def cost(self, r, c):
        occupation = self.get_occupation(r, c)
        return 1 + self.congestion_k * (occupation ** 2)

    def get_cell(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c]
        return CellType.WALL

    def is_free(self, r, c):
        return self.get_cell(r, c) == CellType.FREE

    def is_wall(self, r, c):
        return self.get_cell(r, c) == CellType.WALL

    def is_fire(self, r, c):
        return self.get_cell(r, c) == CellType.FIRE

    def is_exit(self, r, c):
        return self.get_cell(r, c) == CellType.EXIT

    def propagate_fire(self):
        self.fire_turn += 1
        if self.fire_turn % self.fire_propagation_interval != 0:
            return
        new_fires = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == CellType.FIRE:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.grid[nr][nc] == CellType.FREE and (nr, nc) != self.exit_pos:
                                new_fires.append((nr, nc))
        for (r, c) in new_fires:
            self.grid[r][c] = CellType.FIRE

    def step(self):
        self.propagate_fire()
        agents_to_remove = []
        for pos, count in list(self.agent_positions.items()):
            r, c = pos
            if self.is_fire(r, c):
                agents_to_remove.append(pos)
        for pos in agents_to_remove:
            self.remove_agent(pos)

    def all_agents_at_exit(self):
        if not self.agent_positions:
            return False
        for pos, count in self.agent_positions.items():
            if count > 0 and pos != self.exit_pos:
                return False
        return True

    def any_agent_alive(self):
        return any(count > 0 for count in self.agent_positions.values())

    def get_free_cells(self):
        cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == CellType.FREE and not self.is_fire(r, c):
                    cells.append((r, c))
        return cells

    def get_neighbors(self, r, c):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid[nr][nc] != CellType.WALL and not self.is_fire(nr, nc):
                    neighbors.append((nr, nc))
        return neighbors

    def clone(self):
        new_env = Environment(
            self.grid,
            self.fire_propagation_interval,
            self.congestion_k,
            fire_seed=random.randint(0, 2**31 - 1),
            num_agents=0
        )
        new_env.agent_positions = dict(self.agent_positions)
        new_env.exit_pos = self.exit_pos
        new_env.fire_turn = self.fire_turn
        return new_env

    def to_string(self):
        lines = []
        for r in range(self.rows):
            row = ""
            for c in range(self.cols):
                if self.get_occupation(r, c) > 0:
                    row += str(self.get_occupation(r, c)) if self.get_occupation(r, c) > 1 else "A"
                elif self.grid[r][c] == CellType.WALL:
                    row += "#"
                elif self.grid[r][c] == CellType.FIRE:
                    row += "F"
                elif self.grid[r][c] == CellType.EXIT:
                    row += "E"
                else:
                    row += "."
            lines.append(row)
        return "\n".join(lines)


CELL_MAP = {
    "free": CellType.FREE,
    "wall": CellType.WALL,
    "fire": CellType.FIRE,
    "exit": CellType.EXIT,
    "agent": CellType.AGENT,
}


def _convert_grid(raw_grid):
    return [[CELL_MAP[cell] for cell in row] for row in raw_grid]


def make_map1():
    raw_grid = [
        ["free", "free", "free", "free", "free", "free", "free"],
        ["free", "wall", "wall", "wall", "wall", "wall", "free"],
        ["free", "wall", "free", "free", "free", "wall", "free"],
        ["free", "wall", "free", "wall", "free", "wall", "free"],
        ["free", "free", "free", "wall", "exit", "free", "free"],
        ["free", "wall", "wall", "wall", "wall", "wall", "free"],
        ["free", "free", "free", "free", "free", "free", "free"],
    ]
    grid = _convert_grid(raw_grid)
    grid[6][6] = CellType.FIRE
    grid[0][5] = CellType.FIRE
    return grid


def make_map2():
    raw_grid = [
        ["free", "free", "free", "free", "free", "free", "free", "free"],
        ["free", "wall", "wall", "wall", "free", "wall", "wall", "free"],
        ["free", "wall", "free", "free", "free", "free", "wall", "free"],
        ["free", "free", "free", "wall", "wall", "free", "wall", "free"],
        ["wall", "wall", "free", "wall", "exit", "free", "free", "free"],
        ["free", "free", "free", "wall", "free", "wall", "wall", "free"],
        ["free", "wall", "wall", "wall", "free", "free", "free", "free"],
        ["free", "free", "free", "free", "free", "wall", "free", "free"],
    ]
    grid = _convert_grid(raw_grid)
    grid[7][7] = CellType.FIRE
    grid[0][4] = CellType.FIRE
    return grid


def make_map3():
    raw_grid = [
        ["free", "free", "free", "free", "free", "free", "free", "free", "free"],
        ["free", "free", "wall", "free", "free", "free", "free", "free", "free"],
        ["free", "free", "free", "free", "wall", "free", "free", "free", "free"],
        ["wall", "wall", "free", "wall", "wall", "free", "wall", "wall", "wall"],
        ["free", "free", "free", "free", "exit", "free", "free", "free", "free"],
        ["wall", "wall", "free", "wall", "wall", "free", "wall", "wall", "wall"],
        ["free", "free", "free", "free", "wall", "free", "free", "free", "free"],
        ["free", "free", "wall", "free", "free", "free", "free", "free", "free"],
        ["free", "free", "free", "free", "free", "free", "free", "free", "free"],
    ]
    grid = _convert_grid(raw_grid)
    grid[0][4] = CellType.FIRE
    grid[4][0] = CellType.FIRE
    return grid
