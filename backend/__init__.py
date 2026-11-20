"""Paquete con la logica del proyecto de Calculo III (sucesiones y series)."""

from .sucesiones import (  # noqa: F401
    T_n,
    T_float,
    seq_r,
    seq_p,
    seq_q,
    espectro_r,
    espectro_p,
    espectro_q,
    matriz_B,
    analisis_B,
    sumas_parciales,
    areas_descartadas,
    sumas_descartadas,
    tabla,
    forma_cerrada_p,
    forma_cerrada_q,
)

__all__ = [
    "T_n", "T_float", "seq_r", "seq_p", "seq_q",
    "espectro_r", "espectro_p", "espectro_q",
    "matriz_B", "analisis_B",
    "sumas_parciales", "areas_descartadas", "sumas_descartadas",
    "tabla", "forma_cerrada_p", "forma_cerrada_q",
]
