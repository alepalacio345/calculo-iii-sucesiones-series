"""Pruebas del back-end matematico, las figuras y la app web (sin abrir navegador).

Ejecutar:
    .\\.venv\\Scripts\\python.exe tests\\test_backend.py
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")  # sin ventana

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from fractions import Fraction  # noqa: E402

from backend import graficas as gr  # noqa: E402
from backend import sucesiones as su  # noqa: E402

fallos = 0


def check(nombre: str, cond: bool, detalle: str = "") -> None:
    global fallos
    if cond:
        print(f"OK   {nombre}")
    else:
        fallos += 1
        print(f"FALLA {nombre} {detalle}")


# 1) termino general
check("T_n exacto = 1/27", su.T_n(3) == Fraction(1, 27))
check("T_float(2) = 1/9", abs(su.T_float(2) - 1.0 / 9.0) < 1e-15)

# 2) tabla para varios N y ambos modelos
for N in (5, 60):
    for impreso in (True, False):
        d = su.tabla(N, impreso)
        claves = ["n", "T", "r", "p", "q", "err_r", "err_p", "err_q",
                  "rel_r", "rel_p", "rel_q", "S", "D", "SD"]
        check(f"tabla N={N} impreso={impreso}: claves", all(k in d for k in claves))
        check(f"tabla N={N} impreso={impreso}: longitud N+1",
              len(d["T"]) == N + 1 == len(d["n"]))
        check(f"tabla N={N} impreso={impreso}: T0=1", d["T"][0] == 1.0)
        check(f"tabla N={N} impreso={impreso}: n0 en rango",
              all(0 <= (v if v is not None else 0) <= N
                  for v in (d["n0_min_p"], d["n0_min_q"])))

# 3) analisis matricial (punto 5)
for impreso in (True, False):
    info = su.analisis_B(impreso)
    check(f"analisis_B({impreso}): coincide det(B-lI)=recurrencia", info["coincide"] is True)
    check(f"analisis_B({impreso}): rho(B) > 1", info["radio_espectral"] > 1.0)
    check(f"analisis_B({impreso}): matriz 3x3", info["B"].shape == (3, 3))

# 4) espectros (raices conocidas)
check("espectro_r: raiz 1/3",
      abs(su.espectro_r().raices[0] - 1.0 / 3.0) < 1e-9)
check("espectro_p: raices 3 y 1/3",
      sorted(round(abs(r), 4) for r in su.espectro_p().raices) == [0.3333, 3.0])
check("espectro_q corregida: raices 6,3,1/3",
      sorted(round(abs(r), 4) for r in su.espectro_q(False).raices) == [0.3333, 3.0, 6.0])

# 5) serie y areas descartadas
d = su.tabla(40, True)
check("S_N -> 1/2", abs(d["S"][-1] - 0.5) < 1e-9)
check("suma D_N -> 1", abs(d["SD"][-1] - 1.0) < 1e-9)

# 6) figuras: generan Figure con ejes
d = su.tabla(10, True)
info = su.analisis_B(True)
for nombre, fig in [
    ("sucesiones", gr.fig_sucesiones(d)),
    ("detalle", gr.fig_sucesiones_detalle(d)),
    ("diferencias", gr.fig_diferencias(d, False)),
    ("diferencias rel", gr.fig_diferencias(d, True)),
    ("serie", gr.fig_serie(d)),
    ("triangulos", gr.fig_triangulos()),
    ("autovalores", gr.fig_autovalores(info)),
]:
    check(f"figura {nombre}: tiene ejes", len(fig.axes) > 0)
    gr.plt.close(fig)

# 7) la app web importa y expone la ruta
import importlib  # noqa: E402
wm = importlib.import_module("web.web_app")
check("web_app importa (app FastAPI)", wm.app is not None)

print()
print("FALLOS:", fallos)
sys.exit(1 if fallos else 0)
