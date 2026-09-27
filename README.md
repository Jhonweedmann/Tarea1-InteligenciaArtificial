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
│   └── informe.md
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
    └── analisis_resultados.py
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
- **Fuego inicial**: dos focos fijos por mapa más ~5% de celdas libres encendidas al azar según la semilla de cada iteración (manteniendo la salida conectada).
- **Movimiento**: ortogonal (4 direcciones) o esperar.
- **Replanificación**: cada vez que el fuego se propaga, todos los agentes vivos recalculan su ruta.
- **Grupo**: 80 agentes por simulación, con posiciones iniciales aleatorias según la semilla.

## Mapas

- **Mapa 1**: Alta densidad / Cuello de botella (7×7). Pasillos angostos convergen a la salida.
- **Mapa 2**: Densidad media / Laberinto corporativo (8×8). Múltiples salas y cruces ciegos.
- **Mapa 3**: Baja densidad / Dispersión abierta (9×9). Entorno semiabierto con múltiples rutas.

## Métricas

- **Tasa de supervivencia**: `N_sobrevivientes / N_total` por simulación, promediada sobre las iteraciones.
- **Tiempo de despeje**: turno en que el **último sobreviviente** alcanza la salida. Se reporta media, desviación estándar, mínimo y máximo sobre las iteraciones con al menos un sobreviviente.

## Resultados del Benchmark

3 mapas × 5 algoritmos × 200 iteraciones = 3000 simulaciones, 80 agentes cada una. Datos en `benchmark/results/summary.csv`; gráficos en `benchmark/results/`.

| Mapa | Algoritmo | Supervivencia (IC 95%) | Media turnos | Std | Min | Max |
|------|-----------|------------------------|-------------|-----|-----|-----|
| map1 | bfs     | 0.545 [0.508, 0.582] | 16.93 | 8.23 | 1 | 28 |
| map1 | ucs     | 0.558 [0.522, 0.593] | 17.25 | 7.94 | 1 | 28 |
| map1 | astar   | 0.583 [0.549, 0.616] | 17.91 | 7.54 | 4 | 28 |
| map1 | greedy  | 0.515 [0.477, 0.552] | 15.86 | 8.37 | 2 | 28 |
| map1 | genetic | 0.559 [0.525, 0.594] | 17.23 | 7.74 | 1 | 28 |
| map2 | bfs     | 0.424 [0.411, 0.438] | 12.23 | 2.32 | 3 | 14 |
| map2 | ucs     | 0.425 [0.413, 0.437] | 12.29 | 2.06 | 2 | 14 |
| map2 | astar   | 0.427 [0.415, 0.438] | 12.30 | 1.89 | 1 | 14 |
| map2 | greedy  | 0.415 [0.403, 0.427] | 12.13 | 2.03 | 2 | 14 |
| map2 | genetic | 0.424 [0.412, 0.436] | 12.31 | 2.06 | 1 | 14 |
| map3 | bfs     | 0.364 [0.347, 0.382] | 10.79 | 3.54 | 3 | 15 |
| map3 | ucs     | 0.347 [0.330, 0.365] | 10.24 | 3.41 | 2 | 15 |
| map3 | astar   | 0.348 [0.331, 0.366] | 10.27 | 3.49 | 1 | 15 |
| map3 | greedy  | 0.349 [0.331, 0.367] | 10.44 | 3.45 | 3 | 15 |
| map3 | genetic | 0.371 [0.354, 0.388] | 10.91 | 3.37 | 1 | 15 |

Turnos = tiempo de despeje (turno en que el último sobreviviente alcanza la salida).

### Conclusiones clave

- **El factor dominante es el cuello de botella de la salida, no el algoritmo.** La salida admite 3 agentes por turno y el fuego termina rodeándola (sellada en el 100% de las semillas; en promedio en el turno 30 en map1, 14 en map2 y 11 en map3). Los agentes evacuados equivalen en promedio al 86–91% del máximo teórico (3 × turnos), por lo que la supervivencia queda acotada casi igual para todos los algoritmos.
- **map1**: la única diferencia estadísticamente clara es **A\* (0.583) sobre Greedy (0.515)**, cuyos IC 95% no se solapan. A* combina el costo de congestión con la heurística; Greedy ignora el costo acumulado, por lo que probablemente concentra más agentes en las mismas celdas.
- **map2 y map3**: las diferencias entre algoritmos están dentro del margen de error; la salida se sella antes de que la calidad de la ruta influya.
- **map3**, pese a ser el mapa más abierto, tiene la menor supervivencia: uno de los focos iniciales está en la misma fila que la salida y la alcanza antes.
- **El algoritmo genético** rinde a la par de los métodos de búsqueda: su semilla con A* le da rutas válidas y la evolución las ajusta poco en tan pocas generaciones.

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

Se utilizó Claude Code (Anthropic) como asistente para corregir errores del entorno y la simulación (capacidad por celda, conteo de ocupación, métrica de tiempo de despeje) y para reescribir la representación del algoritmo genético como secuencia de acciones.

## Requisitos
- Python 3.8+
- numpy
- matplotlib
