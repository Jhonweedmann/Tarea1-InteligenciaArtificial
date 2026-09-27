# Informe: Escape de la Torre
Septiembre 2026

## 1. Introducción

Este informe presenta la simulación de evacuación de un piso de una torre en llamas y compara cinco algoritmos de navegación: dos de búsqueda no informada (BFS, UCS), dos de búsqueda informada (A*, Greedy Best-First) y un algoritmo genético. El entorno es dinámico: el fuego avanza de forma irreversible, los pasillos tienen capacidad limitada y los agentes deben replanificar sus rutas. El desempeño se mide mediante un benchmark de 200 iteraciones por combinación de mapa y algoritmo.

## 2. Descripción del Entorno

### 2.1 Grilla

Se usan tres mapas de 7×7, 8×8 y 9×9. Cada celda puede ser libre, muro, fuego o salida, y cada piso tiene una única salida.

- **Mapa 1** (alta densidad / cuello de botella): pasillos angostos que convergen hacia la salida.
- **Mapa 2** (densidad media / laberinto corporativo): salas conectadas por intersecciones y cruces ciegos.
- **Mapa 3** (baja densidad / dispersión abierta): entorno semiabierto con varias rutas alternativas.

### 2.2 Congestión: costo y capacidad

La congestión se modela en dos niveles:

1. **Costo de planificación.** Entrar a una celda cuesta `costo(celda) = 1 + k·(ocupación)²`, con k = 0.1. El modelo cuadrático penaliza fuertemente las celdas con varios agentes. UCS, A* y el algoritmo genético usan este costo; BFS y Greedy no.
2. **Capacidad física.** Cada celda admite como máximo 3 agentes simultáneos. Si la celda siguiente de la ruta está llena, el agente espera en su lugar. En la salida, los agentes evacuados se retiran al final del turno, por lo que evacúan como máximo 3 agentes por turno. Esto reproduce el embotellamiento que retrasa el flujo.

### 2.3 Propagación del fuego

Cada mapa tiene dos focos fijos. Además, en cada iteración se enciende al azar ~5% de las celdas libres según la semilla, cuidando que la salida siga conectada. Cada k = 3 turnos el fuego se expande a las celdas ortogonales adyacentes. Las celdas quemadas quedan intransitables para el resto de la simulación y la celda de salida está protegida. Un agente alcanzado por el fuego es una baja.

### 2.4 Movimiento y replanificación

Los agentes solo se desplazan en forma ortogonal (arriba, abajo, izquierda, derecha) o esperan. Cualquier paso que no sea a una celda vecina transitable se rechaza. Cada vez que el fuego se propaga, todos los agentes vivos recalculan su ruta con el algoritmo en evaluación, considerando la ocupación actual.

### 2.5 Orden de un turno

1. Cada agente vivo intenta avanzar un paso de su ruta (o espera si la celda está llena).
2. Los agentes que llegaron a la salida se retiran del entorno.
3. El fuego avanza (cada 3 turnos) y los agentes en celdas quemadas mueren.
4. Si el fuego avanzó, los agentes replanifican.

## 3. Algoritmos Implementados

### 3.1 Búsqueda no informada

**BFS (Breadth-First Search).** Expande nodos por niveles con una cola FIFO y conjunto de visitados. Encuentra la ruta con menos pasos, pero ignora la congestión. Sirve como línea base.

**UCS (Uniform Cost Search).** Expande el nodo de menor costo acumulado con una cola de prioridad. Como el costo de cada celda incluye la congestión, encuentra la ruta de menor costo total considerando la ocupación al momento de planificar.

### 3.2 Búsqueda informada

**A\*.** Ordena la frontera por `f(n) = g(n) + h(n)`, donde `g(n)` es el costo acumulado con congestión y `h(n)` la distancia Manhattan a la salida. La heurística es admisible porque con movimiento ortogonal cada paso cuesta al menos 1, así que nunca sobreestima el costo real. Por lo tanto, A* es óptimo respecto del costo.

**Greedy Best-First.** Ordena la frontera solo por `h(n)` (Manhattan), sin costo acumulado. Explora menos nodos, pero no es óptimo y no considera la congestión.

### 3.3 Optimización bioinspirada: Algoritmo Genético

- **Individuo:** secuencia de acciones (arriba, abajo, izquierda, derecha, esperar). Se decodifica desde la posición del agente; una acción que choca con un muro, el fuego o el borde se interpreta como esperar. Así, toda ruta generada respeta el movimiento ortogonal de una casilla.
- **Población inicial:** 15 individuos; 60% sembrados con la ruta de A* (convertida a acciones, más una cola aleatoria de hasta 5 acciones) y 40% aleatorios, con longitud entre 20 y 150.
- **Fitness:** `200 − pasos − 0.05·costo` si la ruta llega a la salida; `−distancia_Manhattan − 2·costo` si no llega.
- **Selección:** torneo de tamaño 3.
- **Cruce:** un punto de corte.
- **Mutación:** cada gen se reemplaza por una acción aleatoria con probabilidad 0.2.
- **Elitismo:** se conserva el 20% mejor de cada generación.
- **Generaciones:** 20. Se ejecuta al inicio y en cada replanificación.

## 4. Resultados Experimentales

### 4.1 Configuración del benchmark

- 3 mapas × 5 algoritmos × 200 iteraciones = 3000 simulaciones.
- 80 agentes por simulación.
- Cada iteración usa una semilla aleatoria distinta, que determina el fuego inicial y las posiciones de los agentes.
- k = 0.1 (congestión), capacidad 3 por celda, propagación cada 3 turnos, máximo 500 turnos.

**Métricas:**
- **Tasa de supervivencia:** `N_sobrevivientes / N_total` por simulación, promediada sobre las 200 iteraciones. Se reporta el intervalo de confianza del 95% de la media (`media ± 1.96·σ/√n`).
- **Tiempo de despeje:** turno en que el último sobreviviente alcanza la salida. Se reportan media, desviación estándar, mínimo y máximo.

### 4.2 Tabla de resultados

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

Los gráficos (boxplot de turnos, supervivencia por mapa, media de turnos y heatmap comparativo) están en `benchmark/results/`.

### 4.3 Análisis: el cuello de botella de la salida

El resultado central es que **la supervivencia queda limitada principalmente por el entorno y no por el algoritmo**. Dos mecanismos lo explican:

1. **Capacidad de la salida.** Como solo evacúan 3 agentes por turno, el número de sobrevivientes no puede superar `3 × T`, donde T es el tiempo de despeje. En promedio, los agentes evacuados alcanzan entre el 86% y el 91% de esa cota, es decir, la salida trabaja casi siempre a plena capacidad.
2. **Sellado de la salida por el fuego.** Aunque la celda de salida está protegida, el fuego termina ocupando todas sus celdas vecinas. Esto ocurrió en el 100% de las semillas, en promedio en el turno 29.7 (map1), 14.2 (map2) y 11.3 (map3). Por eso el máximo de turnos es idéntico para todos los algoritmos (28, 14 y 15).

Con la salida saturada y un tiempo disponible fijado por el fuego, cualquier algoritmo que lleve agentes a la salida de forma continua obtiene una supervivencia similar.

### 4.4 Análisis por algoritmo

- **A\*** obtiene la mayor supervivencia en map1 (0.583) y es el único caso con diferencia estadísticamente clara: su IC 95% no se solapa con el de Greedy (0.515). Al sumar el costo de congestión a la heurística, reparte mejor a los agentes en los pasillos angostos del mapa 1.
- **Greedy** tiene la menor supervivencia en map1 y map2. Al ignorar el costo acumulado, probablemente concentra más agentes en las mismas celdas.
- **BFS y UCS** quedan en posiciones intermedias. UCS no supera claramente a BFS: la congestión solo se conoce en el momento de planificar y cambia en cuanto los agentes se mueven.
- **El algoritmo genético** rinde a la par de los métodos de búsqueda (el mejor valor en map3, 0.371, dentro del margen de error de BFS). Su siembra con A* le entrega rutas válidas desde el inicio, y con 15 individuos y 20 generaciones la evolución las modifica poco. Es además el más costoso computacionalmente: ~3 s por simulación, frente a <0.1 s de los demás.

### 4.5 Análisis por mapa

- **Mapa 1** (cuello de botella): mayor supervivencia (0.52–0.58) y mayor variabilidad (std ~8 turnos), porque el fuego tarda más en sellar la salida y ese tiempo varía mucho según la semilla. Es el único mapa donde el algoritmo marca una diferencia.
- **Mapa 2** (laberinto): supervivencia ~0.42 para todos, con muy poca dispersión. La salida se sella cerca del turno 14 en casi todas las semillas, lo que limita la evacuación a unos 42 agentes (3 × 14).
- **Mapa 3** (abierto): la menor supervivencia (0.35–0.37), pese a ser el mapa con más rutas. Uno de los focos iniciales está en la misma fila que la salida y la alcanza rápido. Muestra que la posición del fuego respecto de la salida pesa más que la densidad de muros.

### 4.6 Conclusiones

- Con 80 agentes y una salida de capacidad 3, el cuello de botella común domina el resultado: la supervivencia depende sobre todo de cuánto tarda el fuego en sellar la salida.
- A* es el algoritmo más robusto: tiene la mejor supervivencia en el único mapa con diferencias significativas y en los demás mapas no es significativamente peor que ningún otro.
- Greedy es el más débil cuando hay congestión, porque no considera el costo del camino.
- El algoritmo genético es competitivo pero no mejora a A*, del que depende su población inicial, y su costo computacional es mucho mayor.
- Para que el benchmark distinga mejor a los algoritmos se necesitaría más holgura temporal: por ejemplo, más distancia entre el fuego y la salida, mapas más grandes, o menos agentes en relación con la capacidad de la salida.

### 4.7 Limitaciones

- La congestión que ven los algoritmos es la del instante de planificación; los agentes no se coordinan ni reservan celdas.
- Los agentes esperan solo cuando la celda siguiente está llena; la acción de esperar no forma parte del espacio de búsqueda de BFS, UCS, A* ni Greedy (sí del algoritmo genético).
- Cada algoritmo se evaluó con semillas aleatorias independientes; usar las mismas 200 semillas para todos permitiría comparaciones pareadas.

## 5. Fuentes y Citas

- Russell, S. & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson. — BFS, UCS, A*, Greedy Best-First.
- Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning. Addison-Wesley. — Algoritmo genético.
- La heurística Manhattan es un concepto estándar de inteligencia artificial.
- No se utilizaron repositorios externos para los algoritmos de búsqueda.

### Uso de IA generativa

Se utilizó Claude Code (Anthropic) como asistente para corregir errores del entorno y la simulación (capacidad por celda, conteo de ocupación, métrica de tiempo de despeje), para reescribir la representación del algoritmo genético como secuencia de acciones y para redactar este informe a partir de los resultados del benchmark.

## 6. Trabajo Futuro

- Planificación cooperativa con reserva de celdas en el tiempo (por ejemplo, Cooperative A*) para coordinar a los agentes.
- Incluir la acción de esperar y la predicción del avance del fuego en la búsqueda.
- Heurísticas que consideren la distancia al frente de fuego.
- Evaluar escenarios con más holgura temporal para diferenciar mejor los algoritmos.
- Visualización gráfica del entorno multiagente.
