import random
from environment import Environment, CellType
from .astar import manhattan, astar_search


class GeneticAlgorithm:
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

    def _random_coord(self):
        nr = random.randint(0, self.env.rows - 1)
        nc = random.randint(0, self.env.cols - 1)
        if self.env.is_wall(nr, nc) or self.env.is_fire(nr, nc):
            return self.start
        return (nr, nc)

    def _generate_individual(self, smart=False):
        if smart and self.start != self.goal:
            astar_path = astar_search(self.env, self.start, self.goal)
            if astar_path is not None and len(astar_path) > 0:
                path = list(astar_path)
                if len(path) < 5:
                    length = random.randint(5, 20)
                    for _ in range(length - len(path)):
                        pos = path[-1] if path else self.start
                        dr, dc = random.choice([(-1,0),(1,0),(0,-1),(0,1)])
                        nr, nc = pos[0]+dr, pos[1]+dc
                        if 0 <= nr < self.env.rows and 0 <= nc < self.env.cols and not self.env.is_wall(nr,nc) and not self.env.is_fire(nr,nc):
                            path.append((nr, nc))
                return path[:self.max_path_length]

        length = random.randint(20, self.max_path_length)
        return [self._random_coord() for _ in range(length)]

    def _simulate(self, path):
        pos = self.start
        total_cost = 0
        steps = 0
        reached = False
        for coord in path:
            nr, nc = coord
            if not (0 <= nr < self.env.rows and 0 <= nc < self.env.cols):
                nr, nc = pos
            if self.env.is_wall(nr, nc) or self.env.is_fire(nr, nc):
                nr, nc = pos
            cost = self.env.cost(nr, nc)
            total_cost += cost
            pos = (nr, nc)
            steps += 1
            if pos == self.goal:
                reached = True
                break
        return pos, total_cost, steps, reached

    def _fitness(self, path):
        pos, total_cost, steps, reached = self._simulate(path)
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
        child = parent1[:cx_point] + parent2[cx_point:]
        return child

    def _mutate(self, path):
        mutated = path[:]
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                mutated[i] = self._random_coord()
        return mutated

    def _repair(self, path):
        repaired = []
        pos = self.start
        for coord in path:
            nr, nc = coord
            if not (0 <= nr < self.env.rows and 0 <= nc < self.env.cols) or self.env.is_wall(nr, nc) or self.env.is_fire(nr, nc):
                nr, nc = pos
            repaired.append((nr, nc))
            pos = (nr, nc)
            if pos == self.goal:
                break
        return repaired

    def run(self):
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
                best_idx = fitnesses.index(max_fit)
                best_individual = population[best_idx][:]

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
                child = self._repair(child)
                new_population.append(child)

            population = new_population

        return best_individual, best_fitness
