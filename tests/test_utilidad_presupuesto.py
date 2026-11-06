import math
import random
import unittest

from red.exacto import seleccionar_exacto
from red.instancias import UtilidadConPresupuesto, generar_utilidades
from red.repartir import repartir
from red.seleccionar import seleccionar

TOL = 1e-9


class TestUtilidadConPresupuesto(unittest.TestCase):
    def test_grupo_vacio_vale_cero(self):
        f = UtilidadConPresupuesto([[0, 5, 8]], 2)
        self.assertEqual(f(frozenset()), 0.0)

    def test_ejemplo_a_mano(self):
        # nodo 0: ganancias 10, 6, 3 ; nodo 1: ganancias 8, 6, 4 ; B = 3
        u = [[0, 10, 16, 19], [0, 8, 14, 18]]
        f = UtilidadConPresupuesto(u, 3)
        self.assertEqual(f(frozenset({0})), 19)  # las 3 unidades al nodo 0: 10 + 6 + 3
        self.assertEqual(f(frozenset({1})), 18)  # 8 + 6 + 4
        self.assertEqual(f(frozenset({0, 1})), 24)  # tres mejores: 10, 8, 6

    def test_coincide_con_el_reparto_optimo(self):
        rng = random.Random(2)
        for _ in range(100):
            N, B = rng.randint(1, 6), rng.randint(0, 12)
            u = generar_utilidades(N, B, rng)
            x, _ = repartir(u, B)
            esperado = sum(u[i][x[i]] for i in range(N))
            self.assertAlmostEqual(UtilidadConPresupuesto(u, B)(frozenset(range(N))), esperado, places=9)

    def test_es_monotona_y_submodular(self):
        rng = random.Random(8)
        for _ in range(300):
            N, B = rng.randint(3, 9), rng.randint(1, 15)
            f = UtilidadConPresupuesto(generar_utilidades(N, B, rng), B)
            grande = frozenset(rng.sample(range(N), rng.randint(1, N - 1)))
            chico = frozenset(rng.sample(sorted(grande), rng.randint(0, len(grande))))
            n = rng.choice([x for x in range(N) if x not in grande])
            self.assertLessEqual(f(chico), f(grande) + TOL)  # monótona
            self.assertGreaterEqual(f(chico | {n}) - f(chico), f(grande | {n}) - f(grande) - TOL)  # submodular


    def test_el_voraz_de_seleccion_respeta_la_cota_con_esta_f(self):
        rng = random.Random(15)
        cota = 1 - 1 / math.e
        peor = 1.0
        for _ in range(200):
            N, B = rng.randint(3, 9), rng.randint(1, 20)
            k = rng.randint(1, min(4, N - 1))
            f = UtilidadConPresupuesto(generar_utilidades(N, B, rng), B)
            _, voraz, _ = seleccionar(N, k, f)
            _, optimo = seleccionar_exacto(N, k, f)
            self.assertLessEqual(voraz, optimo + TOL)
            self.assertGreaterEqual(voraz, cota * optimo - TOL)
            peor = min(peor, voraz / optimo)
        print(f"\n  con f = utilidad con presupuesto, peor razón voraz/óptimo: {peor:.4f} (cota {cota:.3f})")


if __name__ == "__main__":
    unittest.main()
