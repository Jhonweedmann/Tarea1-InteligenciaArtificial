# Tarea 1: Escape de la Torre

Septiembre 2026

## Integrantes

- Benjamin Jimenez

## Descripcion

Proyecto de simulacion de evacuacion en una torre en llamas. Se implementan 5 algoritmos de busqueda y optimizacion para guiar a un grupo de agentes hacia la salida de evacuacion en un entorno dinamico con propagacion de fuego, costo de congestión y capacidad finita por celda.

## Algoritmos Implementados

1. **BFS** — Busqueda en anchura (no informada). Minimiza pasos e ignora el costo de congestión (línea base).
2. **UCS** — Busqueda de costo uniforme (no informada). Minimiza el costo acumulado, que incluye la congestión.
3. **A\*** — Busqueda informada con heurística Manhattan. Es admisible porque cada paso cuesta al menos 1.
4. **Greedy Best-First** — Busqueda informada guiada solo por la heurística Manhattan, sin costo acumulado.
5. **Algoritmo Genético** — Cada individuo es una secuencia de acciones (arriba, abajo, izquierda, derecha, esperar). Una accion que choca con muro, fuego o borde se interpreta como esperar, por lo que toda ruta respeta el movimiento ortogonal. Selección por torneo (tamaño 3), cruce de un punto, mutación por gen (20%), elitismo (20%). Población de 15 durante 20 generaciones; 60% de la población inicial se siembra con la ruta de A\* y 40% es aleatoria. Fitness: `200 - pasos - 0.05·costo` si llega a la salida; `-distancia_Manhattan - 2·costo` si no.

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

- Russell, S. & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson. - Algoritmos BFS, UCS, A\*, Greedy.
- Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning. Addison-Wesley. - Algoritmo Genético.
- Heurística Manhattan: concepto estándar de inteligencia artificial.

## Uso de IA Generativa

Se utilizó Claude Code (Anthropic) como asistente para corregir errores del entorno y la simulación (capacidad por celda, conteo de ocupación, métrica de tiempo de despeje), para reescribir la representación del algoritmo genético como secuencia de acciones, para rediseñar los tres mapas según las topologías del enunciado, para implementar los scripts de métricas de mapas y de análisis de sensibilidad, y para redactar el informe.

## Requisitos

- Python 3.8+
- numpy
- matplotlib
