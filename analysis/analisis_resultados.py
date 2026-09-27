import os
import sys
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "benchmark", "results")
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

ALGORITHMS = ["bfs", "ucs", "astar", "greedy", "genetic"]
MAPS = ["map1", "map2", "map3"]


def load_results():
    all_data = {}
    for map_name in MAPS:
        all_data[map_name] = {}
        for algo in ALGORITHMS:
            csv_path = os.path.join(RESULTS_DIR, f"{map_name}_{algo}.csv")
            if not os.path.exists(csv_path):
                print(f"Warning: {csv_path} not found")
                all_data[map_name][algo] = {"survived": [], "turns": []}
                continue
            with open(csv_path) as f:
                reader = csv.DictReader(f)
                survived = []
                turns = []
                for row in reader:
                    s = row["survived"].strip()
                    survived.append(float(s) if s else 0.0)
                    t = row["turns"].strip()
                    turns.append(int(t) if t else 0)
                all_data[map_name][algo] = {"survived": survived, "turns": turns}
    return all_data


def print_summary_table(data):
    print(f"\n{'='*80}")
    print(f"{'RESUMEN DE RESULTADOS':^80}")
    print(f"{'='*80}")
    header = f"{'Mapa':<8} {'Algoritmo':<12} {'Superv.':>8} {'Media':>8} {'Std':>8} {'Min':>8} {'Max':>8}"
    print(header)
    print("-" * 80)
    for map_name in MAPS:
        for algo in ALGORITHMS:
            d = data[map_name][algo]
            turns = [t for t, s in zip(d["turns"], d["survived"]) if s > 0]
            rate = np.mean(d["survived"]) if d["survived"] else 0
            if turns:
                print(f"{map_name:<8} {algo:<12} {rate:>8.2f} {np.mean(turns):>8.1f} {np.std(turns):>8.1f} {min(turns):>8} {max(turns):>8}")
            else:
                print(f"{map_name:<8} {algo:<12} {rate:>8.2f} {'N/A':>8} {'N/A':>8} {'N/A':>8} {'N/A':>8}")
    print(f"{'='*80}\n")


def plot_boxplots(data):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for idx, map_name in enumerate(MAPS):
        turns_data = []
        labels = []
        for algo in ALGORITHMS:
            turns = [t for t, s in zip(data[map_name][algo]["turns"], data[map_name][algo]["survived"]) if s > 0]
            if turns:
                turns_data.append(turns)
                labels.append(algo)
        axes[idx].boxplot(turns_data)
        axes[idx].set_xticklabels(labels)
        axes[idx].set_title(f"{map_name}")
        axes[idx].set_ylabel("Turnos")
        axes[idx].tick_params(axis='x', rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "boxplot_turnos_por_algoritmo.png"), dpi=150)
    plt.close()
    print(f"Boxplot guardado en {os.path.join(RESULTS_DIR, 'boxplot_turnos_por_algoritmo.png')}")


def plot_survival_rates(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(ALGORITHMS))
    width = 0.25
    for idx, map_name in enumerate(MAPS):
        rates = []
        for algo in ALGORITHMS:
            rate = np.mean(data[map_name][algo]["survived"]) if data[map_name][algo]["survived"] else 0
            rates.append(rate)
        ax.bar(x + idx * width, rates, width, label=map_name)
    ax.set_xlabel("Algoritmo")
    ax.set_ylabel("Tasa de Supervivencia")
    ax.set_title("Tasa de Supervivencia por Algoritmo y Mapa")
    ax.set_xticks(x + width)
    ax.set_xticklabels(ALGORITHMS)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "tasa_supervivencia.png"), dpi=150)
    plt.close()
    print(f"Grafico de supervivencia guardado en {os.path.join(RESULTS_DIR, 'tasa_supervivencia.png')}")


def plot_mean_turns(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(ALGORITHMS))
    width = 0.25
    for idx, map_name in enumerate(MAPS):
        means = []
        for algo in ALGORITHMS:
            turns = [t for t, s in zip(data[map_name][algo]["turns"], data[map_name][algo]["survived"]) if s > 0]
            means.append(np.mean(turns) if turns else 0)
        ax.bar(x + idx * width, means, width, label=map_name)
    ax.set_xlabel("Algoritmo")
    ax.set_ylabel("Media de Turnos (sobrevivientes)")
    ax.set_title("Media de Turnos por Algoritmo y Mapa")
    ax.set_xticks(x + width)
    ax.set_xticklabels(ALGORITHMS)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "media_turnos.png"), dpi=150)
    plt.close()
    print(f"Grafico de media de turnos guardado en {os.path.join(RESULTS_DIR, 'media_turnos.png')}")


def plot_heatmap(data):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for idx, map_name in enumerate(MAPS):
        matrix = np.zeros((3, 5))
        for algo_idx, algo in enumerate(ALGORITHMS):
            turns = [t for t, s in zip(data[map_name][algo]["turns"], data[map_name][algo]["survived"]) if s > 0]
            if turns:
                matrix[0, algo_idx] = np.mean(turns)
                matrix[1, algo_idx] = np.std(turns)
                matrix[2, algo_idx] = np.mean(data[map_name][algo]["survived"])
        im = axes[idx].imshow(matrix, aspect='auto', cmap='RdYlGn_r')
        axes[idx].set_title(map_name)
        axes[idx].set_xticks(range(5))
        axes[idx].set_xticklabels(ALGORITHMS, rotation=45)
        axes[idx].set_yticks(range(3))
        axes[idx].set_yticklabels(["Media", "Std", "Superv."])
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "heatmap_comparativo.png"), dpi=150)
    plt.close()
    print(f"Heatmap guardado en {os.path.join(RESULTS_DIR, 'heatmap_comparativo.png')}")


def main():
    print("Cargando resultados...")
    data = load_results()
    print_summary_table(data)
    plot_boxplots(data)
    plot_survival_rates(data)
    plot_mean_turns(data)
    plot_heatmap(data)
    print("\nAnalisis completo. Todos los graficos generados en results/")


if __name__ == "__main__":
    main()
