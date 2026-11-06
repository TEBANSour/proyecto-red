"""Parte 1: reparto óptimo del presupuesto (voraz por ganancia marginal)."""

import heapq


def repartir(u, B):
    """Reparte B unidades enteras de presupuesto entre N nodos.

    Parámetros
    ----------
    u : lista de N listas. u[i][x] es la utilidad del nodo i si recibe x unidades.
        Cada u[i] debe ser creciente y cóncava, y tener al menos B + 1 valores
        (posiciones 0..B) para que cualquier nodo pueda recibir todo el presupuesto.
    B : presupuesto total, entero >= 0.

    Devuelve
    --------
    x     : lista de N enteros, x[i] = unidades que recibe el nodo i (suma <= B).
    traza : una entrada por unidad asignada, con el paso, el nodo, la ganancia
            marginal que tenía y cuántas unidades lleva el nodo después.

    Algoritmo: en cada uno de los B pasos se entrega la siguiente unidad al nodo con
    mayor ganancia marginal. Con empate gana el nodo de índice menor.
    Eficiencia: O(N) para construir el montículo + O(B log N) para las B unidades.
    """
    if B < 0:
        raise ValueError("B debe ser >= 0")
    N = len(u)
    x = [0] * N
    traza = []

    # Montículo de mínimos: se guarda (-ganancia, nodo) para sacar la mayor ganancia.
    monticulo = [(-(u[i][1] - u[i][0]), i) for i in range(N) if len(u[i]) > 1]
    heapq.heapify(monticulo)  # O(N)

    for paso in range(1, B + 1):  # B veces
        if not monticulo:  # todos los nodos están en su tope de la tabla
            break
        neg_ganancia, i = heapq.heappop(monticulo)  # O(log N)
        x[i] += 1
        traza.append({"paso": paso, "nodo": i, "ganancia": -neg_ganancia, "x_nodo": x[i]})
        if x[i] + 1 < len(u[i]):
            siguiente = u[i][x[i] + 1] - u[i][x[i]]
            heapq.heappush(monticulo, (-siguiente, i))  # O(log N)

    return x, traza
