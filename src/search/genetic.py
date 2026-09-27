import random
from environment import Environment, CellType
from .astar import manhattan, astar_search

# Genes: acciones ortogonales o esperar
ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]


class GeneticAlgorithm:
    """
    Cada individuo es una secuencia de acciones (arriba, abajo, izquierda,
    derecha, esperar). Al decodificarla desde la posicion inicial, una accion
    que choca con un muro, fuego o el borde se convierte en esperar, por lo
    que toda ruta resultante respeta el movimiento ortogonal de una casilla.
    """

    def __init__(self, env, start, goal, pop_size=15, generations=20,
                 mutation_rate=0.2, tournament_size=3, max_path_length=200):
        self.env = env
        self.start = start
        self.goal = goal
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.max_path_length = max_path_length

    def _random_action(self):
        return random.choice(ACTIONS)

    def _is_passable(self, r, c):
        return (0 <= r < self.env.rows and 0 <= c < self.env.cols
                and not self.env.is_wall(r, c) and not self.env.is_fire(r, c))

    def _path_to_actions(self, path):
        actions = []
        pos = self.start
        for nxt in path:
            actions.append((nxt[0] - pos[0], nxt[1] - pos[1]))
            pos = nxt
        return actions

    def _generate_individual(self, smart=False):
        if smart and self.start != self.goal:
            astar_path = astar_search(self.env, self.start, self.goal)
            if astar_path:
                actions = self._path_to_actions(astar_path)
                # Cola aleatoria para que el cruce tenga material con que trabajar
                extra = random.randint(0, 5)
                actions += [self._random_action() for _ in range(extra)]
                return actions[:self.max_path_length]

        length = random.randint(20, self.max_path_length)
        return [self._random_action() for _ in range(length)]

    def _decode(self, actions):
        """Convierte acciones en la ruta de coordenadas y la corta al llegar a la salida."""
        path = []
        pos = self.start
        for dr, dc in actions:
            nr, nc = pos[0] + dr, pos[1] + dc
            if not self._is_passable(nr, nc):
                nr, nc = pos
            pos = (nr, nc)
            path.append(pos)
            if pos == self.goal:
                break
        return path

    def _simulate(self, actions):
        path = self._decode(actions)
        total_cost = sum(self.env.cost(r, c) for r, c in path)
        pos = path[-1] if path else self.start
        return pos, total_cost, len(path), pos == self.goal

    def _fitness(self, actions):
        pos, total_cost, steps, reached = self._simulate(actions)
        if reached:
            return -steps - 0.05 * total_cost + 200
        dist = manhattan(pos, self.goal)
        return -dist - 2 * total_cost

    def _selection(self, population, fitnesses):
        tournament = random.sample(list(zip(population, fitnesses)), self.tournament_size)
        tournament.sort(key=lambda x: x[1], reverse=True)
        return tournament[0][0]

    def _crossover(self, parent1, parent2):
        min_len = min(len(parent1), len(parent2))
        if min_len < 4:
            return parent1[:]
        cx_point = random.randint(2, min_len - 2)
        return parent1[:cx_point] + parent2[cx_point:]

    def _mutate(self, actions):
        mutated = actions[:]
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                mutated[i] = self._random_action()
        return mutated

    def run(self):
        if self.start == self.goal:
            return [], 0

        population = []
        for _ in range(self.pop_size):
            smart = random.random() < 0.6
            population.append(self._generate_individual(smart=smart))

        best_individual = None
        best_fitness = float('-inf')

        for generation in range(self.generations):
            fitnesses = [self._fitness(ind) for ind in population]

            max_fit = max(fitnesses)
            if max_fit > best_fitness:
                best_fitness = max_fit
                best_individual = population[fitnesses.index(max_fit)][:]

            new_population = []
            elite_count = max(2, self.pop_size // 5)
            sorted_pop = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
            for i in range(elite_count):
                new_population.append(sorted_pop[i][0][:])

            while len(new_population) < self.pop_size:
                parent1 = self._selection(population, fitnesses)
                parent2 = self._selection(population, fitnesses)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)

            population = new_population

        # Ultima generacion tambien se evalua
        fitnesses = [self._fitness(ind) for ind in population]
        max_fit = max(fitnesses)
        if max_fit > best_fitness:
            best_fitness = max_fit
            best_individual = population[fitnesses.index(max_fit)][:]

        return self._decode(best_individual), best_fitness
