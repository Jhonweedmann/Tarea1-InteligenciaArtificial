"""
Caracterizacion de los mapas y del cuello de botella de la salida.

1. Metricas topologicas de cada mapa: densidad de muros, celdas libres,
   agentes por celda libre, rutas disjuntas hacia la salida (corte minimo),
   intersecciones y callejones sin salida.
2. A partir de los CSV del benchmark: turno en que el fuego sella la salida
   (todas sus celdas vecinas quemadas) y cuanto se acercan los evacuados a la
   cota 3 x T impuesta por la capacidad de la salida.
"""
import os
import sys
import csv
import statistics
from collections import deque

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "benchmark", "results")
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from environment import Environment, CellType
from maps import MAPS

ALGORITHMS = ["bfs", "ucs", "astar", "greedy", "genetic"]
NUM_AGENTS = 80
CELL_CAPACITY = 3


def _passable(grid, r, c):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] != CellType.WALL


def _neighbors(grid, r, c):
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        if _passable(grid, r + dr, c + dc):
            yield r + dr, c + dc


def _exit_routes(grid, exit_pos, min_dist=3):
    """Numero maximo de rutas sin celdas en comun que llegan a la salida desde
    celdas a distancia >= min_dist. Por el teorema de Menger es igual al
    minimo de celdas que habria que bloquear para aislar la salida.
    Se calcula como flujo maximo con capacidad 1 por celda (Edmonds-Karp)."""
    dist = {exit_pos: 0}
    queue = deque([exit_pos])
    while queue:
        u = queue.popleft()
        for v in _neighbors(grid, *u):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)

    inf = 10 ** 9
    cap, adj = {}, {}

    def add_edge(u, v, w):
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
        cap[(u, v)] = cap.get((u, v), 0) + w
        cap.setdefault((v, u), 0)

    for cell in dist:
        add_edge((cell, "in"), (cell, "out"), inf if cell == exit_pos else 1)
        for v in _neighbors(grid, *cell):
            add_edge((cell, "out"), (v, "in"), inf)
        if dist[cell] >= min_dist:
            add_edge("S", (cell, "in"), inf)

    target = (exit_pos, "in")
    flow = 0
    while True:
        parent = {"S": None}
        queue = deque(["S"])
        while queue and target not in parent:
            u = queue.popleft()
            for v in adj.get(u, []):
                if v not in parent and cap[(u, v)] > 0:
                    parent[v] = u
                    queue.append(v)
        if target not in parent:
            return flow
        v = target
        while parent[v] is not None:
            u = parent[v]
            cap[(u, v)] -= 1
            cap[(v, u)] += 1
            v = u
        flow += 1


def map_stats(grid):
    rows, cols = len(grid), len(grid[0])
    exit_pos = next((r, c) for r in range(rows) for c in range(cols)
                    if grid[r][c] == CellType.EXIT)
    walls = sum(cell == CellType.WALL for row in grid for cell in row)
    # Libres = donde puede partir un agente (sin muros, salida ni focos fijos)
    free = sum(cell == CellType.FREE for row in grid for cell in row)
    degrees = [len(list(_neighbors(grid, r, c)))
               for r in range(rows) for c in range(cols)
               if grid[r][c] != CellType.WALL and (r, c) != exit_pos]
    return {
        "size": f"{rows}x{cols}",
        "wall_density": walls / (rows * cols),
        "free_cells": free,
        "agents_per_free_cell": NUM_AGENTS / free,
        "exit_routes": _exit_routes(grid, exit_pos),
        "intersections": sum(d >= 3 for d in degrees),
        "dead_ends": sum(d == 1 for d in degrees),
    }


def exit_seal_turn(map_name, fire_seed, fire_propagation_interval=3, max_turns=500):
    """Turno en que todas las celdas vecinas de la salida estan quemadas.
    El fuego no depende de los agentes, asi que basta con simular solo el fuego."""
    env = Environment(MAPS[map_name](), fire_propagation_interval=fire_propagation_interval,
                      fire_seed=fire_seed)
    er, ec = env.exit_pos
    around = [(er + dr, ec + dc) for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
              if _passable(env.grid, er + dr, ec + dc)]
    for turn in range(1, max_turns + 1):
        env.propagate_fire()
        if all(env.is_fire(r, c) for r, c in around):
            return turn
    return None


def load_rows(map_name, algo):
    path = os.path.join(RESULTS_DIR, f"{map_name}_{algo}.csv")
    with open(path) as f:
        return list(csv.DictReader(f))


def main():
    print("Metricas topologicas de los mapas")
    print(f"{'Mapa':<6} {'Tam':<6} {'Muros':>6} {'Libres':>7} {'Ag/celda':>9} "
          f"{'Rutas':>6} {'Inters':>7} {'Callej':>7}")
    for name in MAPS:
        s = map_stats(MAPS[name]())
        print(f"{name:<6} {s['size']:<6} {s['wall_density']:>6.0%} {s['free_cells']:>7} "
              f"{s['agents_per_free_cell']:>9.2f} {s['exit_routes']:>6} "
              f"{s['intersections']:>7} {s['dead_ends']:>7}")

    print("\nSellado de la salida y uso de su capacidad (sobre las semillas del benchmark)")
    print(f"{'Mapa':<6} {'% sellada':>10} {'Turno medio':>12} {'Evacuados / (3*T)':>18}")
    for name in MAPS:
        seal_turns, sealed, total, ratios = [], 0, 0, []
        for algo in ALGORITHMS:
            for row in load_rows(name, algo):
                total += 1
                t = exit_seal_turn(name, int(row["fire_seed"]))
                if t is not None:
                    sealed += 1
                    seal_turns.append(t)
                if row["turns"]:
                    ratios.append(int(row["agents_escaped"]) / (CELL_CAPACITY * int(row["turns"])))
        mean_seal = statistics.mean(seal_turns) if seal_turns else float("nan")
        print(f"{name:<6} {sealed / total:>10.0%} {mean_seal:>12.1f} {statistics.mean(ratios):>18.0%}")


if __name__ == "__main__":
    main()
