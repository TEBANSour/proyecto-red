"""Generador de instancias sintéticas (con semilla fija) y lectura/escritura de casos."""

import json
import math
import random

from .repartir import repartir


class UtilidadConPresupuesto:
    """Utilidad conjunta f(S) = lo que rinden los nodos de S al aplicarles el presupuesto B.

    Es la utilidad total del reparto óptimo de la Parte 1 sobre el grupo S, es decir
    f(S) = max sum_{i en S} u_i(x_i) con sum x_i <= B. Así la calidad de un grupo es lo
    que realmente producen sus nodos con el presupuesto (esa es la definición dada por
    el monitor). Une las dos partes: elegir bien un grupo es elegir el que mejor rinde
    una vez repartido el presupuesto.

    Monótona: agregar un nodo no baja f, porque u_i(0) = 0 y el nodo puede recibir 0.
    Submodular: por concavidad, f(S) es la suma de las B mayores ganancias marginales
    del conjunto de listas de los nodos de S; la suma de las B mayores de una unión es
    submodular (es el rango ponderado de una matroide uniforme).
    Costo de una evaluación: tau = O(|S| + B log |S|) (un reparto con montículo).
    """

    def __init__(self, u, B):
        self.u = u
        self.B = B

    def __call__(self, grupo):
        indices = sorted(grupo)
        if not indices:
            return 0.0
        tablas = [self.u[i] for i in indices]
        x, _ = repartir(tablas, self.B)
        return sum(tablas[j][x[j]] for j in range(len(indices)))


class Cobertura:
    """Utilidad conjunta f(S) = cuántos elementos distintos cubre el grupo S.

    Es monótona y submodular (ver informe, sección de NP-dureza).
    Costo de una evaluación: tau = O(|S| * tamaño medio de un subconjunto).
    """

    def __init__(self, cubre):
        self.cubre = [frozenset(c) for c in cubre]

    def __call__(self, grupo):
        cubiertos = set()
        for n in grupo:
            cubiertos |= self.cubre[n]
        return len(cubiertos)


def generar_utilidades_con_familias(N, B, rng):
    """N tablas u[i][0..B], crecientes y cóncavas, y la familia elegida para cada nodo.

    Cada nodo recibe al azar (con la semilla del generador) una de tres familias, con
    una escala a y un parámetro de forma propios, así que cada nodo queda con una
    curva única. Las tres tienen rendimientos decrecientes (cada unidad aporta menos que
    la anterior) pero de forma diferente, de modo que las curvas de dos nodos pueden
    cruzarse y repartir el presupuesto no es trivial:
      - raíz:        a * x**p            con p en [0,3; 0,8]  (decrece despacio)
      - exponencial: a * (1 - r**x)      con r en [0,5; 0,9]  (se satura rápido)
      - logaritmo:   a * ln(1 + c * x)   con c en [0,5; 2,0]  (decrece a ritmo intermedio)
    La escala a va de 5 a 20. Todas cumplen u(0) = 0.
    """
    tablas, familias = [], []
    for _ in range(N):
        familia = rng.choice(["raiz", "exponencial", "logaritmo"])
        a = rng.uniform(5.0, 20.0)
        if familia == "raiz":
            p = rng.uniform(0.3, 0.8)
            tabla = [a * x**p for x in range(B + 1)]
        elif familia == "exponencial":
            r = rng.uniform(0.5, 0.9)
            tabla = [a * (1 - r**x) for x in range(B + 1)]
        else:
            c = rng.uniform(0.5, 2.0)
            tabla = [a * math.log(1 + c * x) for x in range(B + 1)]
        tablas.append(tabla)
        familias.append(familia)
    return tablas, familias


def generar_utilidades(N, B, rng):
    """Solo las tablas de utilidad (ver generar_utilidades_con_familias)."""
    return generar_utilidades_con_familias(N, B, rng)[0]


def generar_cobertura(N, tam_universo, rng):
    """N subconjuntos aleatorios de {0, ..., tam_universo - 1} (cada uno de tamaño 1 a tam_universo/3)."""
    tope = max(1, tam_universo // 3)
    return [
        sorted(rng.sample(range(tam_universo), rng.randint(1, tope))) for _ in range(N)
    ]


def generar_caso(N, k, B, tam_universo=None, semilla=0, cobertura=False):
    """Instancia completa y reproducible: misma semilla, mismo caso.

    Por defecto el caso solo trae las tablas u de los nodos y la utilidad del grupo es
    la que rinden al aplicarles el presupuesto (UtilidadConPresupuesto). Con
    cobertura=True se agrega además una cobertura explícita ('cubre'), que se usa como
    utilidad del grupo en su lugar (es la f del ejemplo del informe)."""
    rng = random.Random(semilla)
    caso = {"N": N, "k": k, "B": B, "semilla": semilla}
    if cobertura:
        if tam_universo is None:
            tam_universo = max(10, 3 * N)
        caso["tam_universo"] = tam_universo
        caso["cubre"] = generar_cobertura(N, tam_universo, rng)
    caso["u"], caso["familias"] = generar_utilidades_con_familias(N, B, rng)
    return caso


def guardar_caso(caso, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(caso, archivo, indent=1)


def cargar_caso(ruta, semilla=0):
    """Lee un caso JSON: formato del monitor (clave 'parametros') o formato propio
    con las claves N, k, B y u, y opcionalmente cubre (ver manual técnico).

    En el formato del monitor las funciones u de los nodos no vienen en el archivo: se
    generan con la semilla dada (por defecto 0), así que el mismo archivo y la misma
    semilla dan siempre el mismo resultado."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        caso = json.load(archivo)
    from .formato_monitor import convertir, es_formato_monitor

    if es_formato_monitor(caso):
        return convertir(caso, semilla)
    for clave in ("N", "k", "B", "u"):
        if clave not in caso:
            raise ValueError(f"al caso le falta la clave '{clave}'")
    if len(caso["u"]) != caso["N"] or ("cubre" in caso and len(caso["cubre"]) != caso["N"]):
        raise ValueError("'u' (y 'cubre', si está) deben tener N elementos")
    return caso
