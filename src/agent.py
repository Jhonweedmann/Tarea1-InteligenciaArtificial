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
        self.path = list(path) if path else []

    def move(self, env):
        if self.escaped or not self.alive:
            return
        self.turns_taken += 1
        if not self.path:
            return
        next_pos = self.path[0]
        nr, nc = next_pos
        # Accion esperar: la ruta repite la posicion actual
        if next_pos == self.current_pos:
            self.path.pop(0)
            return
        # Solo desplazamientos ortogonales de una casilla
        dist = abs(nr - self.current_pos[0]) + abs(nc - self.current_pos[1])
        if dist != 1 or env.is_wall(nr, nc) or env.is_fire(nr, nc):
            # Ruta invalida: el agente espera y replanifica en la proxima oportunidad
            self.path = []
            return
        # Cuello de botella: si la celda esta llena, el agente espera su turno
        if not env.has_capacity(nr, nc):
            return
        self.path.pop(0)
        env.move_agent(self.current_pos, next_pos)
        self.current_pos = next_pos
        if self.current_pos == env.exit_pos:
            self.escaped = True

    def wait(self, env):
        if self.escaped or not self.alive:
            return
        if env.is_fire(self.current_pos[0], self.current_pos[1]):
            self.alive = False

    def die(self):
        self.alive = False
        self.escaped = False