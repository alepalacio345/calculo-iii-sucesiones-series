"""
@file generar_figuras.py
@brief Genera todas las figuras del proyecto a PNG (sin interfaz).
@details
Calcula las tablas con el backend para los dos modelos (impreso y corregido) y
guarda las 7 figuras de cada uno en la carpeta salidas/. Tambien imprime por
consola los indices de divergencia y la forma cerrada, para poder revisarlos.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import sucesiones as su
from backend import graficas as gr

N = 30
d = su.tabla(N, impreso=True)
info = su.analisis_B(impreso=True)
d_fix = su.tabla(N, impreso=False)
info_fix = su.analisis_B(impreso=False)

salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "salidas")
rutas = gr.guardar_todas(d, info, salida, sufijo="")
rutas += gr.guardar_todas(d_fix, info_fix, salida, sufijo="_variante")

for r in rutas:
    print(os.path.basename(r), os.path.getsize(r))

print()
print("n0 / indices (version impresa):")
for k in ("n0_crece_r", "n0_crece_p", "n0_crece_q",
          "n0_min_r", "n0_min_p", "n0_min_q",
          "n100_r", "n100_p", "n100_q"):
    print(f"  {k:12s} = {d[k]}")
print()
print("forma cerrada p:", su.forma_cerrada_p())
print("n* teorico p :", su.n_teorico(su.forma_cerrada_p()[0],
                                    su.forma_cerrada_p()[1], 3.0))
fc = su.forma_cerrada_q(True)
print("forma cerrada q (impreso):")
for k, v in fc.items():
    print(f"  {k}: {v}")
print()
print("B impreso:")
print(info["B"])
print("autovalores:", info["autovalores"])
print("rho:", info["radio_espectral"])
print("polinomio B:", info["polinomio_B"], " coincide:", info["coincide"])
print("traza:", info["traza"], " det:", info["determinante"])
