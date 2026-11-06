import copy
import json
import math
import os
import tempfile
import unittest

from red.ejecutar import resolver_caso
from red.exacto import seleccionar_exacto
from red.formato_monitor import convertir
from red.instancias import UtilidadConPresupuesto, cargar_caso
from red.seleccionar import seleccionar

RUTA = os.path.join("ejemplos", "entrada_G2_red_15_nodos.json")


def datos_monitor():
    with open(RUTA, encoding="utf-8") as archivo:
        return json.load(archivo)


class TestFormatoMonitor(unittest.TestCase):
    def setUp(self):
        self.caso = cargar_caso(RUTA)

    def test_lee_los_parametros_del_caso_base(self):
        self.assertEqual((self.caso["N"], self.caso["k"], self.caso["B"]), (15, 5, 30))
        self.assertEqual(self.caso["ids"][0], "N01")
        self.assertEqual(self.caso["ids"][-1], "N15")
        self.assertEqual(len(self.caso["u"]), 15)
        self.assertEqual(len(self.caso["u"][0]), 31)  # posiciones 0..B

    def test_cada_nodo_tiene_una_funcion_de_utilidad_y_hay_variedad(self):
        familias = self.caso["familias"]
        self.assertEqual(len(familias), 15)
        self.assertTrue(set(familias) <= {"raiz", "exponencial", "logaritmo"})
        self.assertGreaterEqual(len(set(familias)), 2)

    def test_resuelve_y_cumple_restricciones(self):
        r = resolver_caso(self.caso)
        self.assertTrue(r["restricciones_ok"])
        self.assertEqual(len(r["seleccion_ids"]), 5)
        self.assertTrue(all(i.startswith("N") for i in r["seleccion_ids"]))
        self.assertEqual(sum(r["reparto"].values()), 30)
        self.assertEqual(set(r["reparto"]), set(r["seleccion_ids"]))
        self.assertEqual(set(r["familias_utilidad"]), set(r["seleccion_ids"]))

    def test_misma_semilla_mismo_resultado_y_otra_semilla_otra_instancia(self):
        a, b = resolver_caso(cargar_caso(RUTA, semilla=3)), resolver_caso(cargar_caso(RUTA, semilla=3))
        self.assertEqual(a["seleccion"], b["seleccion"])
        self.assertEqual(a["reparto"], b["reparto"])
        self.assertNotEqual(cargar_caso(RUTA, semilla=3)["u"], cargar_caso(RUTA, semilla=4)["u"])

    def test_voraz_respeta_la_cota_frente_al_exacto(self):
        f = UtilidadConPresupuesto(self.caso["u"], self.caso["B"])
        _, voraz, _ = seleccionar(self.caso["N"], self.caso["k"], f)
        _, optimo = seleccionar_exacto(self.caso["N"], self.caso["k"], f)  # C(15,5) = 3003 grupos
        self.assertLessEqual(voraz, optimo + 1e-9)
        self.assertGreaterEqual(voraz, (1 - 1 / math.e) * optimo)
        print(f"\n  caso del monitor (semilla 0): voraz = {voraz:.4f}, óptimo = {optimo:.4f}, razón = {voraz / optimo:.4f}")

    def test_cada_nodo_tiene_una_curva_unica(self):
        tablas = [tuple(t) for t in self.caso["u"]]
        self.assertEqual(len(set(tablas)), len(tablas))

    def test_la_utilidad_de_la_seleccion_es_la_del_reparto(self):
        r = resolver_caso(self.caso)
        self.assertAlmostEqual(r["f_seleccion"], r["utilidad_reparto"], places=6)
        self.assertTrue(r["verificaciones"]["f_igual_utilidad_del_reparto"])

    def test_ignora_los_campos_de_variantes(self):
        datos = datos_monitor()
        modificado = copy.deepcopy(datos)
        modificado["parametros"]["numero_rondas"] = 99
        modificado["parametros"]["presupuesto_costos_participacion_por_ronda"] = 1
        modificado["grafo"] = []
        for nodo in modificado["nodos"]:
            nodo["costo_participacion"] = 1000
            nodo["presupuesto_total_nodo"] = 1
            nodo["coeficiente_utilidad"] = 0.0
        a, b = resolver_caso(convertir(datos)), resolver_caso(convertir(modificado))
        self.assertEqual(a["seleccion"], b["seleccion"])
        self.assertEqual(a["reparto"], b["reparto"])

    def test_funciona_sin_el_grafo(self):
        datos = datos_monitor()
        del datos["grafo"]
        self.assertTrue(resolver_caso(convertir(datos))["restricciones_ok"])

    def test_rechaza_casos_mal_formados(self):
        datos = datos_monitor()
        malo = copy.deepcopy(datos)
        malo["parametros"]["cupo_participantes_por_ronda_k"] = 16
        with self.assertRaises(ValueError):
            convertir(malo)
        malo = copy.deepcopy(datos)
        del malo["parametros"]["presupuesto_ruido_por_ronda_B"]
        with self.assertRaises(ValueError):
            convertir(malo)
        malo = copy.deepcopy(datos)
        malo["nodos"][1]["id"] = malo["nodos"][0]["id"]
        with self.assertRaises(ValueError):
            convertir(malo)

    def test_carga_desde_archivo_temporal(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "otro.json")
            with open(ruta, "w", encoding="utf-8") as salida:
                json.dump(datos_monitor(), salida)
            self.assertEqual(cargar_caso(ruta)["N"], 15)


if __name__ == "__main__":
    unittest.main()
