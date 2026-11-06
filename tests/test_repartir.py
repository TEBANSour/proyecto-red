import math
import random
import unittest

from red.instancias import generar_utilidades
from red.repartir import repartir
from red.verificar import es_creciente_y_concava, verificar_reparto


def optimo_dp(u, B):
    """Referencia exacta por programación dinámica, solo para verificar en las pruebas."""
    N = len(u)
    mejor = [0.0] * (B + 1)  # mejor[b] = utilidad máxima con los nodos vistos y b unidades
    for i in range(N):
        nuevo = [-math.inf] * (B + 1)
        for b in range(B + 1):
            for x in range(b + 1):
                nuevo[b] = max(nuevo[b], mejor[b - x] + u[i][x])
        mejor = nuevo
    return max(mejor)


class TestRepartir(unittest.TestCase):
    def test_ejemplo_a_mano(self):
        # Ganancias: nodo 0 -> 10,6,3,2,1 ; nodo 1 -> 8,6,4,2,1
        u = [[0, 10, 16, 19, 21, 22], [0, 8, 14, 18, 20, 21]]
        x, traza = repartir(u, 5)
        self.assertEqual(x, [2, 3])
        self.assertEqual(u[0][x[0]] + u[1][x[1]], 34)
        self.assertEqual(len(traza), 5)
        # el orden de las ganancias entregadas es no creciente (por concavidad)
        ganancias = [p["ganancia"] for p in traza]
        self.assertEqual(ganancias, sorted(ganancias, reverse=True))

    def test_respeta_restricciones(self):
        rng = random.Random(7)
        for _ in range(100):
            N, B = rng.randint(1, 8), rng.randint(0, 15)
            u = generar_utilidades(N, B, rng)
            x, _ = repartir(u, B)
            self.assertTrue(all(verificar_reparto(x, N, B).values()))

    def test_es_optimo_contra_programacion_dinamica(self):
        rng = random.Random(11)
        for _ in range(200):
            N, B = rng.randint(1, 5), rng.randint(0, 10)
            u = generar_utilidades(N, B, rng)
            self.assertTrue(all(es_creciente_y_concava(t) for t in u))
            x, _ = repartir(u, B)
            obtenido = sum(u[i][x[i]] for i in range(N))
            self.assertAlmostEqual(obtenido, optimo_dp(u, B), places=9)

    def test_casos_borde(self):
        self.assertEqual(repartir([[0, 1, 2]], 0)[0], [0])
        self.assertEqual(repartir([], 5)[0], [])
        with self.assertRaises(ValueError):
            repartir([[0, 1]], -1)


if __name__ == "__main__":
    unittest.main()
