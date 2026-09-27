import os
import sys
import csv
import random
import statistics
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from simulation import run_simulation

MAP_NAMES = ["map1", "map2", "map3"]
ALGORITHM_NAMES = ["bfs", "ucs", "astar", "greedy", "genetic"]
NUM_ITERATIONS = 200
RESULTS_DIR = os.path.join(BASE_DIR, "benchmark", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_benchmark():
    all_results = []
    total = len(MAP_NAMES) * len(ALGORITHM_NAMES) * NUM_ITERATIONS
    count = 0
    start_time = time.time()

    for map_name in MAP_NAMES:
        num_agents = 80
        for algo_name in ALGORITHM_NAMES:
            results = []
            print(f"\nRunning {map_name} / {algo_name} ({NUM_ITERATIONS} iterations, {num_agents} agents)...")
            for i in range(NUM_ITERATIONS):
                fire_seed = random.randint(0, 2**31 - 1)
                result = run_simulation(
                    map_name, algo_name,
                    num_agents=num_agents,
                    fire_propagation_interval=3,
                    congestion_k=0.1,
                    fire_seed=fire_seed,
                    max_turns=500
                )
                result["map"] = map_name
                result["algorithm"] = algo_name
                result["iteration"] = i
                result["fire_seed"] = fire_seed
                results.append(result)
                count += 1
                if count % 50 == 0:
                    elapsed = time.time() - start_time
                    print(f"  Progress: {count}/{total} ({elapsed:.1f}s)")
            all_results.extend(results)

            csv_path = os.path.join(RESULTS_DIR, f"{map_name}_{algo_name}.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["map", "algorithm", "iteration", "fire_seed", "survived", "turns", "agents_escaped"])
                writer.writeheader()
                writer.writerows(results)
            print(f"  Saved {csv_path}")

    summary_path = os.path.join(RESULTS_DIR, "summary.csv")
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["map", "algorithm", "survival_rate", "mean_turns", "std_turns", "min_turns", "max_turns", "n"])
        writer.writeheader()
        for map_name in MAP_NAMES:
            for algo_name in ALGORITHM_NAMES:
                algo_results = [r for r in all_results if r["map"] == map_name and r["algorithm"] == algo_name]
                survival_rates = [r["survived"] for r in algo_results]
                turns = [r["turns"] for r in algo_results if r["survived"] > 0]
                survival_rate = statistics.mean(survival_rates) if survival_rates else 0
                if turns:
                    summary = {
                        "map": map_name,
                        "algorithm": algo_name,
                        "survival_rate": round(survival_rate, 4),
                        "mean_turns": round(statistics.mean(turns), 2),
                        "std_turns": round(statistics.stdev(turns), 2) if len(turns) > 1 else 0,
                        "min_turns": min(turns),
                        "max_turns": max(turns),
                        "n": len(algo_results),
                    }
                else:
                    summary = {
                        "map": map_name,
                        "algorithm": algo_name,
                        "survival_rate": 0,
                        "mean_turns": 0,
                        "std_turns": 0,
                        "min_turns": 0,
                        "max_turns": 0,
                        "n": len(algo_results),
                    }
                writer.writerow(summary)

    elapsed = time.time() - start_time
    print(f"\nBenchmark complete in {elapsed:.1f}s. All results in {RESULTS_DIR}")
    return all_results


if __name__ == "__main__":
    run_benchmark()