from environment import Environment, CellType


class Agent:
    def __init__(self, start_pos, env):
        self.start_pos = start_pos
        self.current_pos = start_pos
        self.path = []
        self.turns_taken = 0
        self.alive = True
        self.escaped = False

    def set_path(self, path):
        self.path = path
        self.turns_taken = 0

    def move(self, env):
        if self.escaped or not self.alive:
            return
        if self.path:
            next_pos = self.path.pop(0)
            nr, nc = next_pos
            if not (0 <= nr < env.rows and 0 <= nc < env.cols) or env.is_wall(nr, nc) or env.is_fire(nr, nc):
                self.alive = False
                return
            env.move_agent(self.current_pos, next_pos)
            self.current_pos = next_pos
            self.turns_taken += 1
            if self.current_pos == env.exit_pos:
                self.escaped = True
        else:
            self.turns_taken += 1

    def wait(self, env):
        if self.escaped or not self.alive:
            return
        if env.is_fire(self.current_pos[0], self.current_pos[1]):
            self.alive = False

    def die(self):
        self.alive = False
        self.escaped = False