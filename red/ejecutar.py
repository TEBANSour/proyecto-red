"""Ejecuta la solución base sobre un caso: selecciona, reparte, verifica y mide tiempos.

Uso:
    python -m red.ejecutar --N 20 --k 5 --B 30 --semilla 1
    python -m red.ejecutar --caso ejemplos/ejemplo_pequeno.json --traza
    python -m red.ejecutar --N 20 --k 5 --B 30 --semilla 1 --salida resultado.json
"""

import argparse
import json
import time

from .instancias import Cobertura, UtilidadConPresupuesto, cargar_caso, generar_caso, guardar_caso
from .repartir import repartir
from .seleccionar import seleccionar
from .verificar import es_creciente_y_concava, verificar_reparto, verificar_seleccion


def resolver_caso(caso):
    """Corre Parte 2 y luego Parte 1 sobre un caso y devuelve resultados, traza y tiempos."""
    N, k, B = caso["N"], caso["k"], caso["B"]
    # Utilidad del grupo: la que rinden los nodos al aplicarles B (por defecto), o una
    # cobertura explícita si el caso trae 'cubre' (ejemplo del informe).
    usa_presupuesto = "cubre" not in caso
    f = UtilidadConPresupuesto(caso["u"], B) if usa_presupuesto else Cobertura(caso["cubre"])
    ids = caso.get("ids") or [str(i) for i in range(N)]  # nombres de los nodos para mostrar

    t0 = time.perf_counter()
    S, valor_f, traza_sel = seleccionar(N, k, f)
    t1 = time.perf_counter()

    u_elegidos = [caso["u"][n] for n in S]
    x, traza_rep = repartir(u_elegidos, B)
    t2 = time.perf_counter()
    for paso in traza_rep:  # repartir numera 0..k-1 dentro del grupo; se traduce al nodo real
        paso["nodo"] = S[paso["nodo"]]

    utilidad = sum(u_elegidos[j][x[j]] for j in range(len(S)))
    verificaciones = {
        "seleccion": verificar_seleccion(S, N, k),
        "reparto": verificar_reparto(x, len(S), B),
        "u_creciente_y_concava": all(es_creciente_y_concava(t) for t in u_elegidos),
    }
    if usa_presupuesto:
        # la utilidad que dio la selección debe ser la del reparto final
        verificaciones["f_igual_utilidad_del_reparto"] = abs(valor_f - utilidad) < 1e-6
    todo_ok = (
        all(verificaciones["seleccion"].values())
        and all(verificaciones["reparto"].values())
        and verificaciones["u_creciente_y_concava"]
        and verificaciones.get("f_igual_utilidad_del_reparto", True)
    )

    return {
        "N": N,
        "k": k,
        "B": B,
        "ids": ids,
        "seleccion": S,
        "seleccion_ids": [ids[n] for n in S],
        "f_seleccion": valor_f,
        "reparto": {ids[n]: x[j] for j, n in enumerate(S)},
        "familias_utilidad": (
            {ids[n]: caso["familias"][n] for n in S} if "familias" in caso else None
        ),
        "utilidad_reparto": utilidad,
        "traza_seleccion": traza_sel,
        "traza_reparto": traza_rep,
        "verificaciones": verificaciones,
        "restricciones_ok": todo_ok,
        "tiempos_s": {
            "seleccionar": t1 - t0,
            "repartir": t2 - t1,
            "total": t2 - t0,
        },
    }


def _fmt(valor):
    """Enteros tal cual; decimales con 4 cifras para que la salida sea legible."""
    return f"{valor:.4f}" if isinstance(valor, float) else str(valor)


def imprimir(resultado, con_traza):
    ids = resultado["ids"]
    print(f"Caso: N={resultado['N']}  k={resultado['k']}  B={resultado['B']}")
    elegidos = ", ".join(resultado["seleccion_ids"])
    print(f"Nodos seleccionados (en orden): [{elegidos}]  ->  f = {_fmt(resultado['f_seleccion'])}")
    if con_traza:
        print("\nTraza de la selección (ganancia marginal de cada candidato):")
        for paso in resultado["traza_seleccion"]:
            ganancias = ", ".join(f"{ids[n]}:{_fmt(g)}" for n, g in paso["ganancias"].items())
            print(
                f"  paso {paso['paso']}: ganancias [{ganancias}] -> elige {ids[paso['elegido']]}"
                f" (f = {_fmt(paso['valor_grupo'])})"
            )
    if resultado.get("familias_utilidad"):
        print(f"Función de utilidad de cada nodo elegido: {resultado['familias_utilidad']}")
    print(f"\nReparto del presupuesto (nodo: unidades): {resultado['reparto']}")
    print(f"Utilidad total del reparto: {resultado['utilidad_reparto']:.6f}")
    if con_traza:
        print("\nTraza del reparto (una línea por unidad):")
        for p in resultado["traza_reparto"]:
            print(f"  unidad {p['paso']}: nodo {ids[p['nodo']]} (ganancia {p['ganancia']:.6f}, lleva {p['x_nodo']})")
    print("\nVerificación de restricciones:", "OK" if resultado["restricciones_ok"] else "FALLA")
    for grupo, checks in resultado["verificaciones"].items():
        print(f"  {grupo}: {checks}")
    t = resultado["tiempos_s"]
    print(f"\nTiempos: seleccionar {t['seleccionar']:.6f} s, repartir {t['repartir']:.6f} s, total {t['total']:.6f} s")


def main():
    p = argparse.ArgumentParser(description="Proyecto Red: solución base (selección + reparto)")
    p.add_argument("--caso", help="ruta de un caso JSON (si se omite, se genera uno)")
    p.add_argument("--N", type=int, default=10)
    p.add_argument("--k", type=int, default=3)
    p.add_argument("--B", type=int, default=20)
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--guardar-caso", help="guarda el caso generado en este JSON")
    p.add_argument("--salida", help="guarda resultados y trazas en este JSON")
    p.add_argument("--traza", action="store_true", help="imprime la traza completa")
    args = p.parse_args()

    if args.caso:
        caso = cargar_caso(args.caso, semilla=args.semilla)
    else:
        caso = generar_caso(args.N, args.k, args.B, semilla=args.semilla)
        if args.guardar_caso:
            guardar_caso(caso, args.guardar_caso)

    resultado = resolver_caso(caso)
    imprimir(resultado, args.traza)
    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as archivo:
            json.dump(resultado, archivo, indent=1)
        print(f"\nResultados guardados en {args.salida}")


if __name__ == "__main__":
    main()
