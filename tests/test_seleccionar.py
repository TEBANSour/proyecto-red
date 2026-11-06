import math
import random
import unittest

from red.exacto import seleccionar_exacto
from red.instancias import Cobertura, generar_cobertura
from red.seleccionar import seleccionar
from red.verificar import verificar_seleccion

# Ejemplo del informe: A={1,2,3}, B={3,4}, C={4,5,6}, D={1,2}
EJEMPLO = [[1, 2, 3], [3, 4], [4, 5, 6], [1, 2]]


class TestSeleccionar(unittest.TestCase):
    def test_ejemplo_del_informe(self):
        f = Cobertura(EJEMPLO)
        S, valor, traza = seleccionar(4, 2, f)
        self.assertEqual(S, [0, 2])  # A y luego C
        self.assertEqual(valor, 6)
        self.assertEqual(traza[0]["ganancias"], {0: 3, 1: 2, 2: 3, 3: 2})
        self.assertEqual(traza[1]["ganancias"], {1: 1, 2: 3, 3: 0})
        self.assertEqual(seleccionar_exacto(4, 2, f), ([0, 2], 6))

    def test_f_es_monotona_y_submodular(self):
        rng = random.Random(3)
        for _ in range(100):
            N = rng.randint(2, 7)
            f = Cobertura(generar_cobertura(N, 12, rng))
            B_ = frozenset(rng.sample(range(N), rng.randint(1, N - 1)))
            A_ = frozenset(rng.sample(sorted(B_), rng.randint(0, len(B_))))
            fuera = [n for n in range(N) if n not in B_]
            n = rng.choice(fuera)
            self.assertLessEqual(f(A_), f(B_))  # monótona
            self.assertGreaterEqual(f(A_ | {n}) - f(A_), f(B_ | {n}) - f(B_))  # submodular

    def test_respeta_restricciones(self):
        rng = random.Random(5)
        for _ in range(100):
            N = rng.randint(1, 10)
            k = rng.randint(0, N)
            f = Cobertura(generar_cobertura(N, 15, rng))
            S, _, _ = seleccionar(N, k, f)
            self.assertTrue(all(verificar_seleccion(S, N, k).values()))

    def test_voraz_respeta_la_cota_1_menos_1_sobre_e(self):
        rng = random.Random(21)
        cota = 1 - 1 / math.e
        peor = 1.0
        for _ in range(300):
            N = rng.randint(3, 10)
            k = rng.randint(1, min(4, N - 1))
            f = Cobertura(generar_cobertura(N, rng.randint(6, 25), rng))
            _, voraz, _ = seleccionar(N, k, f)
            _, optimo = seleccionar_exacto(N, k, f)
            self.assertLessEqual(voraz, optimo)
            self.assertGreaterEqual(voraz, cota * optimo)
            peor = min(peor, voraz / optimo)
        print(f"\n  peor razón voraz/óptimo observada: {peor:.3f} (cota teórica {cota:.3f})")

    def test_casos_borde(self):
        f = Cobertura(EJEMPLO)
        self.assertEqual(seleccionar(4, 0, f)[0], [])
        self.assertEqual(sorted(seleccionar(4, 4, f)[0]), [0, 1, 2, 3])
        with self.assertRaises(ValueError):
            seleccionar(4, 5, f)


if __name__ == "__main__":
    unittest.main()
