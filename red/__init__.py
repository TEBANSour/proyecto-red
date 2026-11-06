"""Proyecto Red (Subproyecto 2): reparto de presupuesto y selección de participantes.

Solución base:
  - Parte 2: seleccionar(N, k, f)  -> qué nodos participan (voraz, aproximado)
  - Parte 1: repartir(u, B)        -> cuánto presupuesto recibe cada uno (voraz, óptimo)
"""

from .repartir import repartir
from .seleccionar import seleccionar
from .exacto import seleccionar_exacto

__all__ = ["repartir", "seleccionar", "seleccionar_exacto"]
