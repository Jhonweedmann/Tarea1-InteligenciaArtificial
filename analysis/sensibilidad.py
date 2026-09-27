"""
Analisis de sensibilidad: ¿las diferencias entre algoritmos aparecen si el
entorno da mas holgura?

Experimento A: mapas del benchmark con propagacion del fuego cada 3, 5 y 7 turnos.
Experimento B: mapas de 25x25 con la misma topologia de cada nivel de densidad,
               con el fuego aleatorio del 5% y sin el.

Todos los algoritmos usan las mismas semillas (comparacion pareada). El algoritmo
genetico se excluye por su costo computacional (~3 s por simulacion en los mapas
pequenos y bastante mas en 25x25).
"""
import os
import sys
import csv
import math
import random
import statistics

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "benchmark", "results")
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import environment
from environment import CellType
from maps import MAPS
from simulation import run_simulation

ALGORITHMS = ["bfs", "ucs", "astar", "greedy"]
NUM_SEEDS = 100
SEED = 2026

# Mapas de 25x25, solo para este experimento. "#" muro, "." libre, "E" salida,
# "F" foco de fuego fijo.
BIG_MAPS = {
    # Pasillos de ancho 1 que convergen en un unico pasillo final
    "map1": ["F.......................F"]
            + [".#" * 12 + "."] * 13
            + ["." * 25]
            + ["##.#########.#########.##"] * 3
            + ["##" + "." * 21 + "##"]
            + ["############.############"] * 5
            + ["############E############"],
    # 16 salas conectadas por puertas, con tabiques y rincones ciegos
    "map2": [
        "F.....#.....#.....#.....F",
        "......#..#..#.....#......",
        ".###.....#..#.###.....#..",
        "...#..#.##......#.#.###..",
        "......#.....#.....#......",
        "......#.....#.....#......",
        "##.############.#####.###",
        "......#.....#.....#......",
        "....#.#.....#.#...#......",
        "..###...###.#.#......###.",
        "......#...#.#.##..#..#...",
        "......#.....#.....#......",
        "###.#####.#####.#########",
        "......#.....#.....#......",
        "...#..#.#...#.....#..#...",
        ".###..#.#.....###....#...",
        "......#.##..#...#.#..##..",
        "......#.....#.....#......",
        "##.######.############.##",
        "......#.....#.....#......",
        "......#.....#.....#......",
        "..##........#.###......#.",
        "...#..#.....#.#...#..###.",
        "...#..#.....#.....#......",
        "......#..E..#.....#......",
    ],
    # Planta abierta con pilares 2x2 y la salida al centro
    "map3": [
        "F...........#............",
        ".........................",
        ".........................",
        "...##....##....##....##..",
        "...##....##....##....##..",
        ".........................",
        "............#............",
        "............#............",
        ".........................",
        "...##....##....##....##..",
        "...##....##....##....##..",
        ".........................",
        "#.....##....E....##.....#",
        ".........................",
        ".........................",
        "...##....##....##....##..",
        "...##....##....##....##..",
        "............#............",
        "............#............",
        ".........................",
        ".........................",
        "...##....##....##....##..",
        "...##....##....##....##..",
        ".........................",
        "............#...........F",
    ],
}

SYMBOLS = {".": CellType.FREE, "#": CellType.WALL, "E": CellType.EXIT, "F": CellType.FIRE}


def _grid_factory(rows):
    return lambda: [[SYMBOLS[ch] for ch in row] for row in rows]


def _run(map_name, algo, seeds, **kwargs):
    survived = [run_simulation(map_name, algo, fire_seed=s, **kwargs)["survived"] for s in seeds]
    mean = statistics.mean(survived)
    half = 1.96 * statistics.stdev(survived) / math.sqrt(len(survived))
    return mean, half


def main():
    rng = random.Random(SEED)
    seeds = [rng.randint(0, 2**31 - 1) for _ in range(NUM_SEEDS)]
    rows = []

    print("Experimento A: intervalo de propagacion del fuego (mapas del benchmark)")
    for k in (3, 5, 7):
        for map_name in MAPS:
            for algo in ALGORITHMS:
                mean, half = _run(map_name, algo, seeds, fire_propagation_interval=k)
                rows.append({"experiment": "A_fire_interval", "variant": f"k={k}",
                             "map": map_name, "algorithm": algo,
                             "survival_rate": round(mean, 4), "ci95_half": round(half, 4)})
                print(f"  k={k} {map_name} {algo:<7} {mean:.3f} ± {half:.3f}", flush=True)

    print("Experimento B: mapas de 25x25")
    original_maps = dict(MAPS)
    original_fire = environment.Environment._add_random_fire
    MAPS.update({name: _grid_factory(g) for name, g in BIG_MAPS.items()})
    try:
        for variant, random_fire in (("25x25 con fuego aleatorio", True),
                                     ("25x25 sin fuego aleatorio", False)):
            environment.Environment._add_random_fire = (
                original_fire if random_fire else (lambda self, seed: None))
            for map_name in BIG_MAPS:
                for algo in ALGORITHMS:
                    mean, half = _run(map_name, algo, seeds)
                    rows.append({"experiment": "B_map_size", "variant": variant,
                                 "map": map_name, "algorithm": algo,
                                 "survival_rate": round(mean, 4), "ci95_half": round(half, 4)})
                    print(f"  {variant} {map_name} {algo:<7} {mean:.3f} ± {half:.3f}", flush=True)
    finally:
        environment.Environment._add_random_fire = original_fire
        MAPS.clear()
        MAPS.update(original_maps)

    out = os.path.join(RESULTS_DIR, "sensibilidad.csv")
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Resultados guardados en {out}")


if __name__ == "__main__":
    main()
