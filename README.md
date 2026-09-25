# Tarea 1: Escape de la Torre
Septiembre 2026

## Integrantes
- Sebastian Vargas
- Maria Garcia
- Carlos Lopez

## Descripcion

Proyecto de simulacion de evacuacion en una torre en llamas. Se implementan 5 algoritmos de busqueda y optimizacion para guiar a un grupo de agentes hacia la salida de evacuacion en un entorno dinamico con propagacion de fuego y costo de congestión.

## Estructura del Proyecto

`
tarea1-escape-torre/
├── README.md
├── informe/
│   └── informe.md
├── src/
│   ├── __init__.py
│   ├── environment.py      # Grilla, fuego, congestión, mapas
│   ├── agent.py
│   ├── search/
│   │   ├── __init__.py
│   │   ├── bfs.py
│   │   ├── ucs.py
│   │   ├── astar.py
│   │   ├── greedy.py
│   │   └── genetic.py
│   ├── maps/
│   │   ├── __init__.py     # Importa mapas desde environment.py
│   ├── simulation.py
│   └── visualizer.py
├── benchmark/
│   ├── __init__.py
│   ├── run_experiments.py
│   └── results/
├── analysis/
│   └── analisis_resultados.py
├── requirements.txt
└── src/visualizer.py
`

## Algoritmos Implementados

1. **BFS** — Busqueda en anchura, ignora costos de congestión (línea base)
2. **UCS** — Busqueda de costo uniforme (Dijkstra), respeta el costo de congestión
3. **A*** — Heurística Manhattan (admisible), óptima para movimiento ortogonal
4. **Greedy Best-First** — Misma heurística sin costo acumulado (rápido pero subóptimo)
5. **Algoritmo Genético** — Población de rutas (coordenadas), selección torneo, cruce un punto, mutación. 60% semilla con soluciones A*, 40% aleatoria. Fitness: -turnos - 0.05*congestion + 200 si llega a salida.

## Modelo del Entorno

- **Grilla**: Matriz 2D con celdas tipo libre, muro, fuego, salida, agente
- **Costo de congestión**: costo(celda) = 1 + k × (ocupación)² donde k = 0.1
- **Propagación de fuego**: Cada k=3 turnos, fuego se expande BFS de 1 paso. Celdas quemadas son intransitables permanentemente. Salida protegida.
- **Movimiento**: Ortogonal (4 direcciones) o esperar
- **Replanificación**: Cada vez que el fuego se propaga, agentes recalculan ruta
- **Grupo**: Múltiples agentes por mapa (3-4). Métrica: turnos hasta que el último sobreviviente alcance la salida. Cada simulación usa 80 agentes.

## Mapas

- **Mapa 1**: Alta densidad / Cuello de botella (7×7, 3 agentes). Pasillos angostos convergen a la salida.
- **Mapa 2**: Densidad media / Laberinto corporativo (8×8, 3 agentes). Múltiples salas y cruces ciegos.
- **Mapa 3**: Baja densidad / Dispersión abierta (9×9, 4 agentes). Entorno semiabierto con múltiples rutas.

## Resultados del Benchmark (3 mapas × 5 algoritmos × 80 iteraciones = 1200 simulaciones (80 agentes cada una))

| Mapa | Algoritmo | Supervivencia | Media Turnos | Std | Min | Max |
|------|-----------|--------------|-------------|-----|-----|-----|
| map1 | bfs      | 0.80 | 12.0 | 0.0 | 12 | 12 |
| map1 | ucs      | 0.70 | 12.0 | 0.0 | 12 | 12 |
| map1 | astar    | 0.88 | 12.0 | 0.0 | 12 | 12 |
| map1 | greedy   | 0.81 | 12.0 | 0.0 | 12 | 12 |
| map1 | genetic  | 1.00 | 2.3 | 1.1 | 1 | 6 |
| map2 | bfs      | 0.79 | 21.0 | 8.1 | 9 | 30 |
| map2 | ucs      | 0.72 | 22.6 | 7.9 | 9 | 30 |
| map2 | astar    | 0.81 | 24.1 | 7.4 | 9 | 30 |
| map2 | greedy   | 0.46 | 15.9 | 5.9 | 9 | 24 |
| map2 | genetic  | 1.00 | 2.4 | 1.5 | 1 | 9 |
| map3 | bfs      | 0.69 | 8.9 | 1.3 | 8 | 12 |
| map3 | ucs      | 0.51 | 8.8 | 1.5 | 8 | 15 |
| map3 | astar    | 0.59 | 8.7 | 1.6 | 8 | 15 |
| map3 | greedy   | 0.57 | 8.7 | 1.8 | 8 | 15 |
| map3 | genetic  | 1.00 | 3.4 | 1.2 | 1 | 7 |

### Conclusiones clave

- **Algoritmo Genético** es el más rápido y tiene 100% de supervivencia en todos los mapas. La semilla con soluciones A* permite convergencia rápida en pocas generaciones.
- **A*** y **BFS** compiten en los mejores resultados para map1 y map2.
- **Greedy** sufre en el laberinto (map2, 0.46 supervivencia) al quedar atrapado en cruces ciegos.
- **UCS** es más lento pero respeta congestión.
- El costo de congestión afecta la calidad de las rutas cuando hay muchos agentes.

## Instalación

`ash
pip install -r requirements.txt
`

## Uso

### Ejecutar simulación individual
`python
import sys; sys.path.insert(0, 'src')
from simulation import run_simulation
result = run_simulation('map1', 'astar', num_agents=3, fire_seed=42)
print(result)
`

### Ejecutar benchmark completo
`ash
python benchmark/run_experiments.py
`

### Ejecutar análisis
`ash
python analysis/analisis_resultados.py
`

### Ver simulación visual en terminal
`python
import sys; sys.path.insert(0, 'src')
from visualizer import run_visual
run_visual('map1', 'astar', fire_seed=100, delay=0.1, max_turns=50)
`

## Citas y Fuentes

- Russell, S. & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson. - Algoritmos BFS, UCS, A*, Greedy.
- Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning. Addison-Wesley. - Algoritmo Genético.
- Heurística Manhattan: concepto estándar de inteligencia artificial.

## Requisitos
- Python 3.8+
- numpy
- matplotlib
