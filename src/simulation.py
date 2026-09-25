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
                   fire_seed=None, max_turns=500):
    from maps import MAPS
    grid = MAPS[map_name]()
    env = Environment(grid, fire_propagation_interval=fire_propagation_interval,
                      congestion_k=congestion_k, fire_seed=fire_seed,
                      num_agents=num_agents)

    exit_pos = env.exit_pos
    free_cells = env.get_free_cells()
    if not free_cells:
        return {"survived": False, "turns": 0, "agents_escaped": 0}

    rng = random.Random(fire_seed if fire_seed is not None else 42)
    agents = []
    for _ in range(num_agents):
        start_pos = rng.choice(free_cells)
        agent = Agent(start_pos, env)
        path = _find_path(algorithm_name, env, start_pos, exit_pos)
        if path is not None:
            agent.set_path(path)
        agents.append(agent)

    turn = 0
    while turn < max_turns:
        for agent in agents:
            if agent.alive and not agent.escaped:
                if agent.path:
                    agent.move(env)
                else:
                    agent.wait(env)

        if not any(a.alive for a in agents):
            return {"survived": False, "turns": turn + 1, "agents_escaped": count_escaped(agents)}
        if all(a.escaped or not a.alive for a in agents):
            escaped_count = count_escaped(agents)
            return {"survived": escaped_count > 0, "turns": turn + 1, "agents_escaped": escaped_count}

        env.step()

        for agent in agents:
            if agent.alive and not agent.escaped:
                if env.is_fire(agent.current_pos[0], agent.current_pos[1]):
                    agent.alive = False
                    env.remove_agent(agent.current_pos)

        if not any(a.alive for a in agents):
            return {"survived": False, "turns": turn + 1, "agents_escaped": count_escaped(agents)}
        if all(a.escaped or not a.alive for a in agents):
            escaped_count = count_escaped(agents)
            return {"survived": escaped_count > 0, "turns": turn + 1, "agents_escaped": escaped_count}

        if turn % fire_propagation_interval == fire_propagation_interval - 1:
            for agent in agents:
                if agent.alive and not agent.escaped:
                    new_path = _find_path(algorithm_name, env, agent.current_pos, exit_pos)
                    agent.set_path(new_path)

        turn += 1

    escaped_count = count_escaped(agents)
    still_alive = sum(1 for a in agents if a.alive and not a.escaped)
    return {"survived": escaped_count > 0 and still_alive == 0,
            "turns": turn, "agents_escaped": escaped_count}


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
