"""Lectura de casos en el formato del monitor (entrada_G2_red_*.json).

Qué usa la solución base del archivo:
    parametros.cupo_participantes_por_ronda_k   -> k
    parametros.presupuesto_ruido_por_ronda_B    -> B
    nodos[].id                                  -> nombres de los nodos (N = cantidad de nodos)

Qué se ignora (no se valida ni se usa en el caso base):
    parametros.numero_rondas, parametros.presupuesto_costos_participacion_por_ronda,
    nodos[].coeficiente_utilidad, nodos[].presupuesto_total_nodo,
    nodos[].costo_participacion, grafo[]
  Según el monitor, el coeficiente y el grafo corresponden a una variante; las rondas,
  los costos y el presupuesto por nodo también son de variantes.

Las funciones de utilidad (u de cada nodo y f del grupo) no vienen en el archivo. Siguiendo
la recomendación del monitor, las u se generan de forma sintética y reproducible con una
semilla: cada nodo recibe al azar una de varias funciones cóncavas y con parámetros propios
(ver instancias.py). La utilidad de un grupo f no se lee del archivo: es lo que rinden los
nodos del grupo al aplicarles el presupuesto B (UtilidadConPresupuesto).
"""

from .instancias import generar_caso


def es_formato_monitor(datos):
    return isinstance(datos, dict) and "parametros" in datos and "nodos" in datos


def convertir(datos, semilla=0):
    """Convierte el JSON del monitor al caso interno (N, k, B, ids, u, familias)."""
    try:
        p = datos["parametros"]
        k = int(p["cupo_participantes_por_ronda_k"])
        B = int(p["presupuesto_ruido_por_ronda_B"])
        ids = [n["id"] for n in datos["nodos"]]
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"caso del monitor mal formado: falta o es inválido {error}") from error

    N = len(ids)
    if len(set(ids)) != N:
        raise ValueError("hay ids de nodo repetidos")
    if "numero_nodos" in p and int(p["numero_nodos"]) != N:
        raise ValueError(f"numero_nodos = {p['numero_nodos']} pero hay {N} nodos")
    if not 0 <= k <= N:
        raise ValueError(f"k = {k} debe estar entre 0 y N = {N}")
    if B < 0:
        raise ValueError("B debe ser >= 0")

    caso = generar_caso(N, k, B, semilla=semilla)
    caso["ids"] = ids
    return caso
