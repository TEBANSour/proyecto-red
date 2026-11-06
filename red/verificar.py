"""Verificación de restricciones: comprueba que una salida es una solución válida."""

TOL = 1e-9


def es_creciente_y_concava(tabla):
    """True si tabla[x] es creciente y cada unidad aporta no más que la anterior."""
    ganancias = [tabla[x + 1] - tabla[x] for x in range(len(tabla) - 1)]
    creciente = all(g >= -TOL for g in ganancias)
    concava = all(ganancias[i + 1] <= ganancias[i] + TOL for i in range(len(ganancias) - 1))
    return creciente and concava


def verificar_reparto(x, N, B):
    """Restricciones de la Parte 1: N enteros >= 0 cuya suma no supera B."""
    return {
        "longitud_N": len(x) == N,
        "enteros_no_negativos": all(isinstance(v, int) and v >= 0 for v in x),
        "suma_no_supera_B": sum(x) <= B,
    }


def verificar_seleccion(S, N, k):
    """Restricciones de la Parte 2: exactamente k nodos distintos de 0..N-1."""
    return {
        "exactamente_k": len(S) == k,
        "sin_repetidos": len(set(S)) == len(S),
        "indices_validos": all(isinstance(n, int) and 0 <= n < N for n in S),
    }
