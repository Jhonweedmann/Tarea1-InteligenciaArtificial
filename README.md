# Tarea 1: Escape de la Torre
Septiembre 2026

## Integrantes
- Benjamin Jimenez

## Descripcion

Proyecto de simulacion de evacuacion en una torre en llamas. Se implementan 5 algoritmos de busqueda y optimizacion para guiar a un grupo de agentes hacia la salida de evacuacion en un entorno dinamico con propagacion de fuego, costo de congestión y capacidad finita por celda.

## Estructura del Proyecto

```
Tarea1/
├── README.md
├── requirements.txt
├── informe/
│   ├── informe.md
│   ├── informe.tex
│   └── informe.pdf
├── src/
│   ├── __init__.py
│   ├── environment.py      # Grilla, fuego, congestión, capacidad, mapas
│   ├── agent.py            # Movimiento ortogonal / esperar
│   ├── simulation.py       # Bucle de simulacion multiagente
│   ├── visualizer.py       # Visualizacion en terminal
│   ├── maps/
│   │   └── __init__.py     # Importa mapas desde environment.py
│   └── search/
│       ├── __init__.py
│       ├── bfs.py
│       ├── ucs.py
│       ├── astar.py
│       ├── greedy.py
│       └── genetic.py
├── benchmark/
│   ├── run_experiments.py
│   └── results/            # CSV por experimento, summary.csv y graficos
└── analysis/
    ├── analisis_resultados.py  # Tabla y graficos del benchmark
    ├── metricas_mapas.py       # Metricas de los mapas y sellado de la salida
    └── sensibilidad.py         # Sensibilidad a velocidad del fuego y tamano del mapa
```

## Algoritmos Implementados

1. **BFS** — Busqueda en anchura (no informada). Minimiza pasos e ignora el costo de congestión (línea base).
2. **UCS** — Busqueda de costo uniforme (no informada). Minimiza el costo acumulado, que incluye la congestión.
3. **A*** — Busqueda informada con heurística Manhattan. Es admisible porque cada paso cuesta al menos 1.
4. **Greedy Best-First** — Busqueda informada guiada solo por la heurística Manhattan, sin costo acumulado.
5. **Algoritmo Genético** — Cada individuo es una secuencia de acciones (arriba, abajo, izquierda, derecha, esperar). Una accion que choca con muro, fuego o borde se interpreta como esperar, por lo que toda ruta respeta el movimiento ortogonal. Selección por torneo (tamaño 3), cruce de un punto, mutación por gen (20%), elitismo (20%). Población de 15 durante 20 generaciones; 60% de la población inicial se siembra con la ruta de A* y 40% es aleatoria. Fitness: `200 - pasos - 0.05·costo` si llega a la salida; `-distancia_Manhattan - 2·costo` si no.

## Modelo del Entorno

- **Grilla**: Matriz 2D con celdas libre, muro, fuego y salida. Una única salida por piso.
- **Costo de congestión**: `costo(celda) = 1 + k·(ocupación)²`, con k = 0.1. Lo usan UCS, A* y el GA al planificar.
- **Capacidad por celda**: cada celda admite como máximo 3 agentes simultáneos. Si la celda siguiente está llena, el agente espera en su lugar. En la salida, esto limita la evacuación a 3 agentes por turno, lo que genera el cuello de botella.
- **Propagación de fuego**: cada k = 3 turnos el fuego se expande a las celdas ortogonales adyacentes. Las celdas quemadas son intransitables de forma permanente y la salida está protegida. Un agente alcanzado por el fuego es una baja.
- **Fuego inicial**: dos focos fijos por mapa, en esquinas alejadas de la salida, más ~5% de celdas libres encendidas al azar según la semilla de cada iteración (manteniendo la salida conectada).
- **Movimiento**: ortogonal (4 direcciones) o esperar.
- **Replanificación**: cada vez que el fuego se propaga, todos los agentes vivos recalculan su ruta.
- **Grupo**: 80 agentes por simulación, con posiciones iniciales aleatorias según la semilla, solo en celdas que aún tienen capacidad.

## Mapas

Diseñados a mano para representar las tres topologías del enunciado (`#` muro, `.` libre, `E` salida, `F` foco de fuego fijo):

```
Mapa 1 (7×7)   Mapa 2 (8×8)   Mapa 3 (9×9)
F.....F        F..#...F       F........
.#.#.#.        .#...#..       .#.....#.
.......        .#.#.#..       ....#....
.#.#.#.        .#####.#       .........
.......        ...#....       ..#.E.#..
##...##        .#.#.#..       .........
###E###        ........       ....#....
               ...#..E.       .#.....#.
                              ........F
```

| | Mapa 1: Alta densidad / Cuello de botella | Mapa 2: Densidad media / Laberinto | Mapa 3: Baja densidad / Abierto |
|---|---|---|---|
| Estructura | Retícula de pasillos de ancho 1 que converge en un embudo | 4 salas con puertas de una celda y rincones ciegos | Planta abierta con pilares y salida al centro |
| Densidad de muros | 33% | 27% | 10% |
| Agentes por celda libre | 2.67 | 1.82 | 1.14 |
| Rutas independientes hacia la salida | 1 | 3 | 4 |
| Callejones sin salida | 0 | 2 | 0 |

Métricas calculadas con `python analysis/metricas_mapas.py`.

## Métricas

- **Tasa de supervivencia**: `N_sobrevivientes / N_total` por simulación, promediada sobre las iteraciones.
- **Tiempo de despeje**: turno en que el **último sobreviviente** alcanza la salida. Se reporta media, desviación estándar, mínimo y máximo sobre las iteraciones con al menos un sobreviviente.

## Resultados del Benchmark

3 mapas × 5 algoritmos × 200 iteraciones = 3000 simulaciones, 80 agentes cada una. Datos en `benchmark/results/summary.csv`; gráficos en `benchmark/results/`.

| Mapa | Algoritmo | Supervivencia (IC 95%) | Media turnos | Std | Min | Max |
|------|-----------|------------------------|-------------|-----|-----|-----|
| map1 | bfs     | 0.397 [0.367, 0.427] | 11.87 | 6.25 | 2 | 21 |
| map1 | ucs     | 0.394 [0.365, 0.423] | 12.13 | 6.17 | 3 | 21 |
| map1 | astar   | 0.402 [0.374, 0.429] | 12.33 | 5.94 | 2 | 21 |
| map1 | greedy  | 0.408 [0.382, 0.434] | 12.62 | 5.37 | 3 | 20 |
| map1 | genetic | 0.419 [0.391, 0.446] | 12.86 | 5.89 | 3 | 21 |
| map2 | bfs     | 0.454 [0.426, 0.482] | 13.28 | 5.38 | 3 | 24 |
| map2 | ucs     | 0.426 [0.396, 0.457] | 12.60 | 5.73 | 2 | 24 |
| map2 | astar   | 0.417 [0.390, 0.443] | 12.44 | 5.05 | 3 | 25 |
| map2 | greedy  | 0.402 [0.374, 0.430] | 13.02 | 5.79 | 3 | 25 |
| map2 | genetic | 0.459 [0.430, 0.489] | 13.62 | 5.54 | 3 | 25 |
| map3 | bfs     | 0.451 [0.431, 0.470] | 12.55 | 3.78 | 5 | 21 |
| map3 | ucs     | 0.448 [0.426, 0.469] | 12.36 | 4.15 | 3 | 21 |
| map3 | astar   | 0.442 [0.421, 0.464] | 12.23 | 4.10 | 3 | 21 |
| map3 | greedy  | 0.420 [0.400, 0.440] | 11.70 | 3.92 | 3 | 21 |
| map3 | genetic | 0.439 [0.417, 0.462] | 12.15 | 4.38 | 3 | 21 |

Turnos = tiempo de despeje (turno en que el último sobreviviente alcanza la salida).

### Conclusiones clave

- **El factor dominante es el cuello de botella de la salida, no el algoritmo.** La salida admite 3 agentes por turno y el fuego la sella en el 100% de las semillas (en promedio en el turno 13.9, 16.5 y 12.8 según el mapa), antes de los 27 turnos que se necesitan para evacuar a 80 agentes.
- **Ninguna diferencia entre algoritmos es significativa** tras corregir por comparaciones múltiples (prueba z por parejas con corrección de Holm).
- **Greedy es el más débil de forma consistente**: tiene la menor supervivencia en los mapas 2 y 3 del benchmark y en las 9 configuraciones del análisis de sensibilidad. En el laberinto, la distancia Manhattan es una mala guía.
- **UCS y A\*** dan resultados prácticamente idénticos (misma función de costo, ambos óptimos) y no superan a BFS: la congestión que usan al planificar deja de ser válida en cuanto los agentes se mueven.
- **Análisis de sensibilidad**: hacer más lento el fuego (cada 5 o 7 turnos) o agrandar los mapas a 25×25 no separa a los algoritmos. La similitud es una propiedad del modelo, no del tamaño de los mapas. Detalle en el informe (sección 4.7).

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar benchmark completo (3 mapas × 5 algoritmos × 200 iteraciones)
```bash
python benchmark/run_experiments.py
```

### Generar tabla y gráficos
```bash
python analysis/analisis_resultados.py
```

### Métricas de los mapas y sellado de la salida (requiere el benchmark)
```bash
python analysis/metricas_mapas.py
```

### Análisis de sensibilidad (velocidad del fuego y mapas de 25×25)
```bash
python analysis/sensibilidad.py
```

### Ejecutar una simulación individual
```python
import sys; sys.path.insert(0, 'src')
from simulation import run_simulation
result = run_simulation('map1', 'astar', num_agents=80, fire_seed=42)
print(result)
```

### Ver simulación visual en terminal (un agente)
```bash
python src/visualizer.py
```

## Citas y Fuentes

- Russell, S. & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson. - Algoritmos BFS, UCS, A*, Greedy.
- Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning. Addison-Wesley. - Algoritmo Genético.
- Heurística Manhattan: concepto estándar de inteligencia artificial.

## Uso de IA Generativa

Se utilizó Claude Code (Anthropic) como asistente para corregir errores del entorno y la simulación (capacidad por celda, conteo de ocupación, métrica de tiempo de despeje), para reescribir la representación del algoritmo genético como secuencia de acciones, para rediseñar los tres mapas según las topologías del enunciado, para implementar los scripts de métricas de mapas y de análisis de sensibilidad, y para redactar el informe.

## Requisitos
- Python 3.8+
- numpy
- matplotlib
