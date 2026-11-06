"""Parte 2: selección de k participantes (voraz submodular, aproximado)."""


def seleccionar(N, k, f):
    """Elige k nodos de los N candidatos usando el voraz por ganancia marginal.

    Parámetros
    ----------
    N : número de nodos candidatos (identificados como 0..N-1).
    k : cuántos nodos se pueden seleccionar, 0 <= k <= N.
    f : función de utilidad conjunta. Recibe un frozenset de índices de nodos y
        devuelve un número. Debe ser monótona y submodular.

    Devuelve
    --------
    S     : lista con los k nodos elegidos, en el orden en que se eligieron.
    valor : f(S).
    traza : una entrada por paso, con las ganancias marginales de todos los
            candidatos, el nodo elegido y el valor del grupo después de agregarlo.

    En cada uno de los k pasos se calcula, para cada nodo que aún no está,
    f(grupo + nodo) - f(grupo), y se agrega el de mayor ganancia (con empate, el de
    índice menor). Garantiza al menos (1 - 1/e) ~ 63% del óptimo (Nemhauser,
    Wolsey y Fisher, 1978). Eficiencia: O(N * k) evaluaciones de f.
    """
    if not 0 <= k <= N:
        raise ValueError("se requiere 0 <= k <= N")

    elegidos = []
    en_grupo = set()
    valor = f(frozenset())
    traza = []

    for paso in range(1, k + 1):
        ganancias = {}
        for n in range(N):
            if n not in en_grupo:
                ganancias[n] = f(frozenset(en_grupo | {n})) - valor
        mejor = max(ganancias, key=lambda n: (ganancias[n], -n))
        elegidos.append(mejor)
        en_grupo.add(mejor)
        valor += ganancias[mejor]
        traza.append(
            {
                "paso": paso,
                "ganancias": ganancias,
                "elegido": mejor,
                "valor_grupo": valor,
            }
        )

    return elegidos, valor, traza
