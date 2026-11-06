# Manual técnico — Proyecto Red, solución base

Este manual describe cómo está construida la solución base del Subproyecto 2 y cómo reproducir su ejecución. Cubre solo el **caso base**: las variantes no están implementadas.

## 1. Entorno

- Lenguaje: Python 3.8 o superior. Desarrollado y probado con Python 3.13.
- Sistema: cualquiera con Python (probado en Linux).
- Dependencias: ninguna. Solo se usan módulos de la biblioteca estándar (`heapq`, `itertools`, `random`, `json`, `argparse`, `time`, `math`, `unittest`).
- Instalación: no hay. Basta con clonar o descomprimir el repositorio y ejecutar los comandos desde su carpeta raíz.

## 2. Arquitectura

```
proyecto-red/
├── red/
│   ├── __init__.py      exporta repartir, seleccionar, seleccionar_exacto
│   ├── repartir.py      Parte 1: reparto óptimo del presupuesto
│   ├── seleccionar.py   Parte 2: selección voraz de k nodos
│   ├── exacto.py        Parte 2: fuerza bruta, para conocer el óptimo
│   ├── instancias.py    utilidades de grupo (f), generador sintético, guardar/cargar casos
│   ├── formato_monitor.py  lee los casos en el formato del monitor (entrada_G2_red_*.json)
│   ├── verificar.py     comprueba que las salidas respetan las restricciones
│   └── ejecutar.py      programa principal: encadena las dos partes, mide tiempos
├── tests/               pruebas unitarias (unittest)
├── ejemplos/            ejemplo_pequeno.json y entrada_G2_red_15_nodos.json (caso del monitor)
├── README.md
└── manual_tecnico.md
```

| Módulo | Responsabilidad |
|---|---|
| `repartir.py` | Recibe las tablas de utilidad de los nodos ya elegidos y el presupuesto B; devuelve cuántas unidades recibe cada nodo y la traza. |
| `seleccionar.py` | Recibe N, k y la función f; devuelve los k nodos elegidos, f del grupo y la traza de ganancias marginales. |
| `exacto.py` | Prueba los C(N, k) grupos para dar el óptimo exacto. Solo para N pequeño. |
| `instancias.py` | Define las dos utilidades de grupo f (`UtilidadConPresupuesto`, por defecto, y `Cobertura`), genera casos sintéticos con semilla fija y lee/escribe casos en JSON. |
| `formato_monitor.py` | Lee N, k, B e ids del JSON del monitor, valida que esté bien formado y completa el caso con funciones u y f generadas con semilla (ver sección 3). |
| `verificar.py` | Valida restricciones (k nodos distintos, reparto entero con suma ≤ B, u creciente y cóncava). |
| `ejecutar.py` | Corre selección y luego reparto sobre un caso, verifica, mide tiempos y entrega resultados y trazas. |

## 3. Funcionamiento

### Flujo del programa

```
caso (N, k, B, u)   [más 'cubre' si el caso trae una cobertura explícita]
   │
   ├─ Parte 2: seleccionar(N, k, f)  ──►  S = k nodos elegidos
   │
   ├─ u_S = tablas de utilidad solo de los nodos de S
   │
   ├─ Parte 1: repartir(u_S, B)      ──►  x = unidades por nodo
   │
   └─ verificar restricciones, medir tiempos, entregar resultados y trazas
```

### Parte 2 — `seleccionar` (voraz submodular)

1. Empieza con el grupo vacío.
2. Repite k veces: para cada nodo que aún no está en el grupo calcula la **ganancia marginal** `f(grupo ∪ {n}) − f(grupo)`; agrega el de mayor ganancia (con empate, el de índice menor).
3. Devuelve el grupo, su valor y la traza.

- Estructuras de datos: un `set` con los elegidos, una lista con el orden de elección y un diccionario nodo → ganancia por paso.
- Condición de parada: se agregan exactamente k nodos.
- Eficiencia: en el paso j se evalúan N − j + 1 nodos, así que son O(N · k) evaluaciones de f; con τ el costo de una evaluación, T(N, k) = O(N · k · τ). Para la f por defecto (`UtilidadConPresupuesto`) τ = O(|S| + B log |S|), porque cada evaluación hace un reparto con montículo sobre el grupo; entonces T(N, k) = O(N · k · (k + B log k)). Para la f de cobertura τ = O(|S| · tamaño medio de un subconjunto).
- Garantía: si f es monótona y submodular, el valor es al menos (1 − 1/e) ≈ 63 % del óptimo (Nemhauser, Wolsey y Fisher, 1978). El problema es NP-difícil, por eso no se resuelve de forma exacta.

### Parte 1 — `repartir` (voraz con montículo)

1. Para cada nodo se calcula la ganancia de su primera unidad, `u[i][1] − u[i][0]`, y se arma un montículo (`heapq`) con `(−ganancia, nodo)`. Costo O(N).
2. Repite B veces: saca del montículo el nodo de mayor ganancia, le suma una unidad, y vuelve a meter el nodo con la ganancia de su siguiente unidad. Costo O(log N) por vez.
3. Devuelve `x` y la traza.

- Estructuras de datos: montículo binario de mínimos (se guarda la ganancia con signo negativo) y una lista `x`.
- Condiciones de parada: se asignaron B unidades, o el montículo quedó vacío (todos los nodos llegaron al final de su tabla).
- Eficiencia: T(N, B) = O(N + B log N). Es pseudo-polinomial: B cuenta como valor y no como longitud en bits.
- Optimalidad: por el argumento de intercambio del informe (concavidad de cada u). Las pruebas lo contrastan con programación dinámica.

### La función f y las funciones u

- **f** tiene dos implementaciones, ambas monótonas y submodulares. Por defecto es `UtilidadConPresupuesto`: `f(S)` es lo que rinden los nodos de S al repartirles el presupuesto B de forma óptima (sección siguiente). `Cobertura` se usa cuando el caso trae una lista `cubre`: cada nodo cubre un conjunto de elementos y `f(S)` es cuántos elementos distintos cubre el grupo S; es la f del ejemplo del informe y de la reducción de NP-dureza.
- **u** se guarda como tabla: `u[i][x]` es la utilidad del nodo i con x unidades, para x = 0..B. El generador usa tres familias cóncavas y crecientes con parámetros propios por nodo (sección siguiente).

### Casos del monitor: de dónde salen u y f

El archivo `entrada_G2_red_15_nodos.json` no trae las funciones de utilidad: trae, por nodo, un `coeficiente_utilidad`, costos, un presupuesto total y un grafo con `peso_influencia`. Según el monitor, el coeficiente y el grafo corresponden a una de las variantes (lo dijo de memoria, por lo que conviene reconfirmarlo), y las rondas, los costos y el presupuesto por nodo también. **La solución base solo toma del archivo N (por la lista de nodos), k y B**, y construye las funciones con una semilla (`--semilla`, por defecto 0).

**u (Parte 1): una función distinta por nodo.** El monitor indicó que se pueden definir varias funciones, siempre que tengan rendimientos decrecientes, y hacerlas un poco aleatorias para que cada nodo sea único; también pidió justificarlo en este manual. Cada nodo recibe una de tres familias, con una escala `a` entre 5 y 20 y un parámetro de forma propio:

| Familia | Fórmula | Parámetro | Comportamiento |
|---|---|---|---|
| raíz | `a·xᵖ` | p entre 0,3 y 0,8 | los rendimientos decrecen despacio |
| exponencial | `a·(1 − rˣ)` | r entre 0,5 y 0,9 | el nodo se satura rápido |
| logaritmo | `a·ln(1 + c·x)` | c entre 0,5 y 2,0 | decrecen a ritmo intermedio |

Las tres son crecientes, cóncavas (cada unidad aporta menos que la anterior) y cumplen u(0) = 0. Se justifica variar la familia porque, si todos los nodos tuvieran la misma forma de curva y solo cambiara la escala, las curvas de utilidad nunca se cruzarían: siempre iría arriba la del nodo de mayor escala. Con formas distintas, la curva de un nodo puede empezar por encima de la de otro y quedar por debajo más adelante (por ejemplo, una exponencial arranca fuerte y se agota, mientras una raíz sigue aportando), así que la decisión depende de la ganancia marginal en cada momento y se pone a prueba el voraz. Los parámetros de forma y la escala hacen que cada nodo tenga una curva única. La semilla fija hace repetible el sorteo.

**f (Parte 2): lo que rinden los nodos con el presupuesto.** El monitor indicó que la utilidad del grupo se basa en los nodos seleccionados: al aplicarles el presupuesto, la utilidad es lo que den esos nodos. Se implementa así: `f(S)` es la utilidad total del reparto óptimo de la Parte 1 sobre el grupo S, es decir, el máximo de Σ uᵢ(xᵢ) con Σ xᵢ ≤ B. Consecuencias:

- La utilidad con la que se elige el grupo coincide con la utilidad del reparto final; cada ejecución lo verifica.
- f es monótona: agregar un nodo no baja el valor, porque uᵢ(0) = 0 y el nodo puede recibir cero unidades.
- f es submodular: por la concavidad, f(S) es la suma de las B mayores ganancias marginales entre las listas de los nodos de S, y la suma de las B mayores de una unión de listas es submodular (es el rango ponderado de una matroide uniforme). Por eso se aplica la garantía de 1 − 1/e. Las pruebas lo comprueban en instancias aleatorias.
- Costo de una evaluación: τ = O(|S| + B log |S|).

**Cobertura.** La f de cobertura (cada nodo cubre un conjunto de elementos) sigue disponible para casos que traigan la lista `cubre`, como `ejemplos/ejemplo_pequeno.json`. Es la f del ejemplo del informe y de la reducción de NP-dureza.

**Nota sobre la dureza.** La prueba de NP-dureza del informe es para el problema con una f monótona y submodular cualquiera; la cobertura es un caso de esa familia y la f por presupuesto es otro. Con la f por presupuesto el voraz dio siempre el óptimo en las pruebas (peor razón 1,0000 en 200 instancias pequeñas), mientras que con cobertura la peor razón fue 0,75. Por eso no se afirma que los casos con la f por presupuesto sean difíciles por sí solos; los ejemplos que muestran la dificultad usan cobertura.

Como las funciones dependen de la semilla, el resultado de un mismo archivo cambia con `--semilla`, pero el mismo archivo con la misma semilla da siempre lo mismo. La salida con `--traza` muestra la familia asignada a cada nodo elegido.

## 4. Uso paso a paso

1. Abrir una terminal en la carpeta raíz del repositorio.
2. Ejecutar el ejemplo pequeño:
   ```bash
   python -m red.ejecutar --caso ejemplos/ejemplo_pequeno.json --traza
   ```
3. Generar un caso propio (la semilla fija lo hace repetible):
   ```bash
   python -m red.ejecutar --N 20 --k 5 --B 30 --semilla 1
   ```
4. Guardar resultados y trazas en JSON: añadir `--salida resultado.json`. Guardar la instancia generada: añadir `--guardar-caso caso.json`.

### Opciones

| Opción | Significado | Por defecto |
|---|---|---|
| `--caso RUTA` | Lee el caso de un JSON (ignora N, k, B, semilla) | genera uno |
| `--N`, `--k`, `--B` | Nodos candidatos, nodos a elegir, presupuesto | 10, 3, 20 |
| `--semilla` | Semilla del generador | 0 |
| `--guardar-caso RUTA` | Guarda el caso generado | — |
| `--salida RUTA` | Guarda resultados, trazas y tiempos | — |
| `--traza` | Imprime la traza completa | no |

### Formatos de entrada (JSON)

**Formato del monitor.** Se detecta solo por la clave `parametros`. Ejemplo: `ejemplos/entrada_G2_red_15_nodos.json`, que se ejecuta con `python -m red.ejecutar --caso ejemplos/entrada_G2_red_15_nodos.json --traza`. Los nodos se identifican por su `id` (por ejemplo `N01`) y la salida usa esos mismos ids. Las utilidades se generan con `--semilla` (ver sección 3).

**Formato propio.** Para casos pequeños con cobertura explícita:

```json
{
 "N": 4, "k": 2, "B": 5,
 "cubre": [[1, 2, 3], [3, 4], [4, 5, 6], [1, 2]],
 "u": [[0, 10, 16, 19, 21, 22], [0, 8, 14, 18, 20, 21],
       [0, 9, 15, 19, 22, 24], [0, 5, 9, 12, 14, 15]]
}
```

- `cubre[i]` (opcional): elementos que cubre el nodo i. Si está, define la f de la selección (cobertura); si no está, f es lo que rinden los nodos al aplicarles el presupuesto B.
- `u[i]`: tabla de utilidad del nodo i, con B + 1 valores (posiciones 0..B), creciente y cóncava.
- Los nodos se numeran 0..N−1.

### Ejemplo y significado de la salida

Con `ejemplos/ejemplo_pequeno.json`:

```
Nodos seleccionados (en orden): [0, 2]  ->  f = 6
Reparto del presupuesto (nodo: unidades): {'0': 2, '2': 3}
Utilidad total del reparto: 35.000000
```

- Se eligieron los nodos 0 y 2 (el 0 primero), que juntos cubren 6 elementos.
- Del presupuesto B = 5, el nodo 0 recibe 2 unidades y el nodo 2 recibe 3; la utilidad es u₀(2) + u₂(3) = 16 + 19 = 35.
- **Traza de la selección:** por paso, la ganancia marginal de cada candidato y el elegido. En el paso 2 el nodo 3 tiene ganancia 0 porque el nodo 0 ya cubre sus elementos.
- **Traza del reparto:** una línea por unidad, con el nodo que la recibe, la ganancia que aportó y cuántas unidades lleva. Las ganancias salen en orden no creciente.
- **Verificación de restricciones:** comprueba que hay exactamente k nodos distintos con índices válidos, que el reparto son N enteros ≥ 0 con suma ≤ B, y que cada u es creciente y cóncava.
- **Tiempos:** segundos medidos con `time.perf_counter` para la selección, el reparto y el total.

El archivo de `--salida` contiene: `seleccion`, `f_seleccion`, `reparto`, `utilidad_reparto`, `traza_seleccion`, `traza_reparto`, `verificaciones`, `restricciones_ok` y `tiempos_s`.

## 5. Validación y límites

### Pruebas disponibles

```bash
python -m unittest discover -s tests -t . -v
```

| Prueba | Qué comprueba |
|---|---|
| `test_ejemplo_a_mano` | El reparto de un caso calculado a mano (B = 5, dos nodos) da [2, 3] y utilidad 34. |
| `test_es_optimo_contra_programacion_dinamica` | En 200 instancias aleatorias el reparto voraz iguala el óptimo exacto. |
| `test_ejemplo_del_informe` | La selección del ejemplo del informe da {A, C} con f = 6 y las ganancias esperadas. |
| `test_voraz_respeta_la_cota_1_menos_1_sobre_e` | En 300 instancias pequeñas el voraz está entre (1 − 1/e)·óptimo y el óptimo (peor razón observada: 0,75). |
| `test_f_es_monotona_y_submodular` | La f de cobertura cumple las dos propiedades en instancias aleatorias. |
| `test_respeta_restricciones` (ambas partes) | Toda salida cumple las restricciones del problema. |
| `test_ejemplo_pequeno_del_repositorio` | El ejemplo de `ejemplos/` da los resultados documentados en este manual. |
| `test_misma_semilla_mismo_caso` | Reproducibilidad del generador. |
| `test_voraz_respeta_la_cota_frente_al_exacto` (caso del monitor) | Con los 15 nodos y semilla 0, el voraz queda entre (1 − 1/e)·óptimo y el óptimo (en este caso lo iguala, razón 1,0000). |
| `test_la_utilidad_de_la_seleccion_es_la_del_reparto` | La utilidad con la que se eligió el grupo es la utilidad del reparto final. |
| `test_cada_nodo_tiene_una_curva_unica` | Ningún par de nodos tiene la misma tabla de utilidad. |
| `test_es_monotona_y_submodular` (utilidad con presupuesto) | La f por defecto cumple las dos propiedades en 300 instancias aleatorias. |
| `test_coincide_con_el_reparto_optimo` y `test_ejemplo_a_mano` (utilidad con presupuesto) | f de un grupo es el valor del reparto óptimo sobre él, y coincide con un caso calculado a mano. |
| `test_el_voraz_de_seleccion_respeta_la_cota_con_esta_f` | En 200 instancias con la f por defecto el voraz respeta la cota (peor razón observada: 1,0000). |
| `test_ignora_los_campos_de_variantes` | Cambiar rondas, costos, coeficientes, presupuesto por nodo o quitar el grafo no altera el resultado del caso base. |
| `test_cada_nodo_tiene_una_funcion_de_utilidad_y_hay_variedad` | Cada nodo tiene una de las tres familias y se usan al menos dos distintas. |
| `test_rechaza_casos_mal_formados` | k > N, un parámetro faltante o ids repetidos dan un error claro. |

### Límites y componentes aún no desarrollados

- **Variantes no implementadas:** costos de participación distintos, rondas con fallas y nodos relacionados entre sí.
- **Coeficiente de utilidad y grafo:** el monitor dijo, de memoria, que corresponden a una variante, y por eso no se usan. Si resulta que el caso base debe usarlos, hay que cambiar la generación en `formato_monitor.py` e `instancias.py`.
- **Casos finales:** los casos del monitor y la profesora no se conocen; el programa espera que usen el formato del archivo de ejemplo.
- **Presupuesto total por nodo:** el campo `presupuesto_total_nodo` (para las T rondas) no se aplica en el caso base, que resuelve una sola ronda.
- **Mediciones de tiempo:** solo se mide una ejecución por caso. Falta el estudio con varios tamaños y la comparación contra la curva teórica.
- **Función f:** hay dos implementadas (con presupuesto, por defecto, y de cobertura). Otra f debe ser monótona y submodular para conservar la garantía.
- **Velocidad de la selección:** con la f por defecto cada evaluación hace un reparto, así que el tiempo de `seleccionar` crece con B; con N y B muy grandes puede ser lento en Python (no se ha optimizado).
- **Tablas u:** deben tener al menos B + 1 valores. Si una tabla es más corta, el nodo deja de recibir presupuesto al llegar a su tope.
- **Fuerza bruta:** `seleccionar_exacto` es exponencial; solo sirve para N pequeño (las pruebas usan N ≤ 10).
- **Números reales:** las utilidades son de punto flotante; las comparaciones de las pruebas usan tolerancia de 1e-9.
- **Empates:** se resuelven siempre a favor del nodo de menor índice, así el resultado es determinista.
