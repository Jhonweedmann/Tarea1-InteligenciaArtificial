import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from environment import Environment, CellType
from agent import Agent
from search.bfs import bfs_search
from search.ucs import ucs_search
from search.astar import astar_search, greedy_search
from search.genetic import GeneticAlgorithm

ALGORITHMS = {
    "bfs": bfs_search,
    "ucs": ucs_search,
    "astar": astar_search,
    "greedy": greedy_search,
}


def render(env, agent, turn):
    print(f"{'='*env.cols*4}  Turno: {turn}  {'='*env.cols*4}")
    for r in range(env.rows):
        line = ""
        for c in range(env.cols):
            if (r, c) == agent.current_pos:
                line += " [A] "
            elif env.is_fire(r, c):
                line += " [F] "
            elif env.is_wall(r, c):
                line += " [##] "
            elif env.is_exit(r, c):
                line += " [E] "
            else:
                line += " [ ] "
        print(line)
    status = "VIVO" if agent.alive else "MUERTO"
    esc = "ESCAPO!" if agent.escaped else ""
    print(f"\n  Pos: {agent.current_pos} | Estado: {status} | {esc}")
    if agent.path:
        print(f"  Pasos restantes en ruta: {len(agent.path)}")
    print()


def run_visual(map_name, algorithm_name, fire_seed=None, delay=0.3, max_turns=200):
    from maps import MAPS
    grid = MAPS[map_name]()
    env = Environment(grid, fire_propagation_interval=3, congestion_k=0.1, fire_seed=fire_seed,
                      num_agents=1)

    agent_starts = list(env.agent_positions.keys())
    if not agent_starts:
        print("No hay agentes en el mapa.")
        return

    start_pos = agent_starts[0]
    exit_pos = env.exit_pos
    agent = Agent(start_pos, env)

    path = _find_path(algorithm_name, env, start_pos, exit_pos)
    if path is None:
        print("No existe ruta posible. El fuego bloquea todas las salidas.")
        return
    agent.set_path(path)

    turn = 0
    render(env, agent, turn)
    time.sleep(delay)

    while turn < max_turns:
        if path:
            agent.move(env)
        else:
            agent.wait(env)

        if not agent.alive:
            render(env, agent, turn + 1)
            print(f"*** El agente murio en el turno {turn + 1}!")
            return
        if agent.escaped:
            render(env, agent, turn + 1)
            print(f"*** El agente ESCAPO en {turn + 1} turnos!")
            return

        env.step()

        if not agent.alive:
            render(env, agent, turn + 1)
            print(f"*** El agente murio por fuego en el turno {turn + 1}!")
            return
        if agent.escaped:
            render(env, agent, turn + 1)
            print(f"*** El agente ESCAPO en {turn + 1} turnos!")
            return

        if turn % 3 == 2 and agent.alive:
            new_path = _find_path(algorithm_name, env, agent.current_pos, exit_pos)
            if new_path is not None:
                agent.set_path(new_path)
                path = new_path

        turn += 1
        render(env, agent, turn)
        time.sleep(delay)

    render(env, agent, turn)
    print(f"*** Simulacion terminada despues de {turn} turnos.")
    print(f"Resultado: {'Escape exitoso' if agent.escaped else 'No escapo'}")


def _find_path(algorithm_name, env, start, goal):
    if algorithm_name == "genetic":
        ga = GeneticAlgorithm(env, start, goal, pop_size=15, generations=20, max_path_length=150)
        path, _ = ga.run()
        return path
    elif algorithm_name in ALGORITHMS:
        return ALGORITHMS[algorithm_name](env, start, goal)
    else:
        return bfs_search(env, start, goal)


if __name__ == "__main__":
    print("=== Escape de la Torre - Visualizador ===")
    print()
    print("Mapas disponibles: map1, map2, map3")
    print("Algoritmos: bfs, ucs, astar, greedy, genetic")
    print()

    map_name = input("Selecciona mapa (1, 2, 3): ").strip()
    algo_name = input("Selecciona algoritmo: ").strip()
    delay_str = input("Velocidad seg/turno (default 0.3): ").strip()
    delay = float(delay_str) if delay_str else 0.3

    map_key = f"map{map_name}"
    run_visual(map_key, algo_name, delay=delay)
