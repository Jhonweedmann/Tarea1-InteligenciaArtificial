import random
from environment import Environment, CellType
from agent import Agent
from search.bfs import bfs_search
from search.ucs import ucs_search
from search.astar import astar_search
from search.greedy import greedy_search
from search.genetic import GeneticAlgorithm


ALGORITHMS = {
    "bfs": bfs_search,
    "ucs": ucs_search,
    "astar": astar_search,
    "greedy": greedy_search,
}

NUM_AGENTS_DEFAULT = 80


def run_simulation(map_name, algorithm_name, num_agents=80,
                   fire_propagation_interval=3, congestion_k=0.1,
                   fire_seed=None, max_turns=500, cell_capacity=3):
    from maps import MAPS
    grid = MAPS[map_name]()
    # num_agents=0: el entorno solo registra a los agentes reales creados abajo
    env = Environment(grid, fire_propagation_interval=fire_propagation_interval,
                      congestion_k=congestion_k, fire_seed=fire_seed,
                      num_agents=0, cell_capacity=cell_capacity)

    exit_pos = env.exit_pos
    free_cells = env.get_free_cells()
    if not free_cells:
        return {"survived": 0.0, "turns": None, "agents_escaped": 0}

    rng = random.Random(fire_seed if fire_seed is not None else 42)
    agents = []
    for _ in range(num_agents):
        # Respeta la capacidad de cada celda al ubicar a los agentes
        candidates = [cell for cell in free_cells if env.has_capacity(*cell)] or free_cells
        start_pos = rng.choice(candidates)
        agents.append(Agent(start_pos, env))
        env.add_agent(start_pos)

    # Se planifica con todos los agentes ya ubicados, para que la congestion sea visible
    for agent in agents:
        agent.set_path(_find_path(algorithm_name, env, agent.current_pos, exit_pos))

    # Tiempo de despeje: turno en que el ultimo sobreviviente alcanzo la salida
    last_escape_turn = None
    turn = 0
    while turn < max_turns:
        for agent in agents:
            if agent.alive and not agent.escaped:
                agent.move(env)
                if agent.escaped:
                    last_escape_turn = turn + 1

        # Los evacuados abandonan la salida al final del turno; asi la capacidad
        # de la salida limita cuantos agentes evacuan por turno
        while env.get_occupation(*exit_pos) > 0:
            env.remove_agent(exit_pos)

        if all_done(agents):
            break

        env.step()

        for agent in agents:
            if agent.alive and not agent.escaped:
                if env.is_fire(agent.current_pos[0], agent.current_pos[1]):
                    agent.alive = False
                    env.remove_agent(agent.current_pos)

        if all_done(agents):
            break

        if turn % fire_propagation_interval == fire_propagation_interval - 1:
            for agent in agents:
                if agent.alive and not agent.escaped:
                    new_path = _find_path(algorithm_name, env, agent.current_pos, exit_pos)
                    agent.set_path(new_path)

        turn += 1

    escaped_count = count_escaped(agents)
    return {"survived": escaped_count / num_agents, "turns": last_escape_turn,
            "agents_escaped": escaped_count}


def all_done(agents):
    return all(a.escaped or not a.alive for a in agents)


def count_escaped(agents):
    return sum(1 for a in agents if a.escaped)


def _find_path(algorithm_name, env, start, goal):
    if algorithm_name == "genetic":
        ga = GeneticAlgorithm(env, start, goal, pop_size=15, generations=20, max_path_length=150)
        path, _ = ga.run()
        return path
    elif algorithm_name in ALGORITHMS:
        return ALGORITHMS[algorithm_name](env, start, goal)
    else:
        return bfs_search(env, start, goal)
