import os
import tempfile
import unittest

from red.ejecutar import resolver_caso
from red.instancias import cargar_caso, generar_caso, guardar_caso


class TestEjecutar(unittest.TestCase):
    def test_misma_semilla_mismo_caso(self):
        self.assertEqual(generar_caso(8, 3, 10, semilla=4), generar_caso(8, 3, 10, semilla=4))
        self.assertNotEqual(generar_caso(8, 3, 10, semilla=4), generar_caso(8, 3, 10, semilla=5))

    def test_resolver_caso_cumple_restricciones(self):
        for semilla in range(20):
            resultado = resolver_caso(generar_caso(15, 4, 25, semilla=semilla))
            self.assertTrue(resultado["restricciones_ok"])
            self.assertEqual(len(resultado["seleccion"]), 4)
            self.assertLessEqual(sum(resultado["reparto"].values()), 25)

    def test_guardar_y_cargar_caso(self):
        caso = generar_caso(6, 2, 8, semilla=1)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "caso.json")
            guardar_caso(caso, ruta)
            self.assertEqual(resolver_caso(cargar_caso(ruta))["seleccion"], resolver_caso(caso)["seleccion"])

    def test_ejemplo_pequeno_del_repositorio(self):
        resultado = resolver_caso(cargar_caso(os.path.join("ejemplos", "ejemplo_pequeno.json")))
        self.assertEqual(resultado["seleccion"], [0, 2])
        self.assertEqual(resultado["f_seleccion"], 6)
        self.assertEqual(resultado["reparto"], {"0": 2, "2": 3})
        self.assertAlmostEqual(resultado["utilidad_reparto"], 35)
        # la traza del reparto nombra los nodos reales (0 y 2), no posiciones dentro del grupo
        self.assertEqual([p["nodo"] for p in resultado["traza_reparto"]], [0, 2, 0, 2, 2])


if __name__ == "__main__":
    unittest.main()
