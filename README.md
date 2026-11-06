# Proyecto Red — Solución base (Subproyecto 2)

Análisis y Diseño de Algoritmos 2026-B · Reparto de presupuesto y selección de participantes.

| | |
|---|---|
| **Integrante** | Esteban Ortiz Murillo |
| **Subproyecto** | 2 — Proyecto Red (Grupo 2) |
| **Versión entregada** | Primera entrega, solo **caso base** (sin variantes) |
| **Enlace al repositorio** | https://github.com/TEBANSour/proyecto-red.git |

## Qué hace

Una ronda del problema tiene dos pasos:

1. **Parte 2 – `seleccionar(N, k, f)`:** de N nodos candidatos elige k con el voraz por ganancia marginal. Es **aproximado** (garantiza al menos 1 − 1/e ≈ 63 % del óptimo) porque el problema es NP-difícil.
2. **Parte 1 – `repartir(u, B)`:** reparte B unidades enteras de presupuesto entre los nodos elegidos con un montículo. Es **óptimo**, en O(N + B log N).

Para el análisis, las demostraciones y la reducción de NP-dureza ver el informe. Para la estructura del código y el detalle del funcionamiento ver [`manual_tecnico.md`](manual_tecnico.md).

## Requisitos

- Python 3.8 o superior (desarrollado y probado con Python 3.13).
- **Sin dependencias externas**: solo biblioteca estándar.

## Ejecutar un ejemplo pequeño

Desde la carpeta raíz del repositorio:

```bash
python -m red.ejecutar --caso ejemplos/ejemplo_pequeno.json --traza
```

Resultado esperado (los tiempos varían):

```
Nodos seleccionados (en orden): [0, 2]  ->  f = 6
Reparto del presupuesto (nodo: unidades): {'0': 2, '2': 3}
Utilidad total del reparto: 35.000000
Verificación de restricciones: OK
```

Con un caso generado (reproducible gracias a la semilla):

```bash
python -m red.ejecutar --N 20 --k 5 --B 30 --semilla 1
python -m red.ejecutar --N 20 --k 5 --B 30 --semilla 1 --salida resultado.json   # guarda resultados y trazas
python -m red.ejecutar --N 20 --k 5 --B 30 --semilla 1 --guardar-caso caso.json   # guarda la instancia
```

## Casos en el formato del monitor

El programa lee directamente los archivos `entrada_G2_red_*.json` del monitor (se detectan por la clave `parametros`):

```bash
python -m red.ejecutar --caso ejemplos/entrada_G2_red_15_nodos.json --traza
```

Del archivo se usan `nodos[].id` (el número de nodos N), `cupo_participantes_por_ronda_k` (k) y `presupuesto_ruido_por_ronda_B` (B). El resto (rondas, costos de participación, `presupuesto_total_nodo`, `coeficiente_utilidad` y el grafo) corresponde a variantes y no se usa en el caso base.

Las funciones de utilidad no vienen en el archivo, así que se generan con una semilla (`--semilla`, por defecto 0): cada nodo recibe al azar una de varias funciones cóncavas con parámetros propios (raíz, exponencial saturante o logaritmo), siguiendo la recomendación del monitor. La utilidad de un grupo de nodos es lo que rinden al aplicarles el presupuesto B, también según el monitor. La justificación está en [`manual_tecnico.md`](manual_tecnico.md), sección 3. El mismo archivo con la misma semilla da siempre el mismo resultado.

## Pruebas

```bash
python -m unittest discover -s tests -t . -v
```

Hay 29 pruebas. Entre otras: el reparto coincide con el óptimo de programación dinámica en 200 instancias aleatorias, el voraz de selección respeta la cota 1 − 1/e frente a la fuerza bruta en 300 instancias, y toda salida cumple las restricciones del problema.

## Estructura

```
red/                  código fuente
  repartir.py         Parte 1 (voraz con montículo)
  seleccionar.py      Parte 2 (voraz submodular)
  exacto.py           Parte 2 exacta por fuerza bruta (solo instancias pequeñas)
  instancias.py       generador con semilla, utilidad de grupo (con presupuesto y de cobertura), lectura/escritura de casos
  formato_monitor.py  lectura de los casos en el formato del monitor
  verificar.py        verificación de restricciones
  ejecutar.py         programa principal (línea de comandos)
tests/                pruebas unitarias
ejemplos/             instancia pequeña con resultado esperado y el caso de 15 nodos del monitor
manual_tecnico.md     manual técnico
```

## Estado

Hecho: solución base de las dos partes, verificación de restricciones, trazas, pruebas.
Pendiente por confirmar con el monitor: si el coeficiente de utilidad se usa en el caso base (él lo recordaba como parte de una variante).
Pendiente (entregas posteriores): variantes, algoritmo exacto comparado a gran escala, mediciones de tiempo con varios tamaños y gráficas.
