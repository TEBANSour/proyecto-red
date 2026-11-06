"""Algoritmo exacto de la Parte 2 por fuerza bruta (solo para instancias pequeñas).

Sirve para conocer el óptimo y comprobar que el voraz respeta la cota (1 - 1/e).
Prueba los C(N, k) subconjuntos, así que solo es usable con N pequeño.
"""

from itertools import combinations


def seleccionar_exacto(N, k, f):
    """Devuelve (mejor_grupo, mejor_valor) probando todos los grupos de k nodos."""
    if not 0 <= k <= N:
        raise ValueError("se requiere 0 <= k <= N")
    mejor_grupo, mejor_valor = None, None
    for grupo in combinations(range(N), k):
        valor = f(frozenset(grupo))
        if mejor_valor is None or valor > mejor_valor:
            mejor_grupo, mejor_valor = list(grupo), valor
    return mejor_grupo, mejor_valor
