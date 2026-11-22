"""
@file numeros_clave.py
@brief Imprime por consola los numeros clave del proyecto.
@details Muestra raices, radio espectral, indices n0, formas cerradas y la
matriz B para la recurrencia (iii) impresa y la corregida.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import sucesiones as su

for impreso in (True, False):
    et = "IMPRESO" if impreso else "CORREGIDO"
    d = su.tabla(40, impreso)
    e = su.espectro_q(impreso)
    info = su.analisis_B(impreso)
    print("=" * 60)
    print(et)
    print("  P(l) =", e.latex_pol())
    print("  raices:", [f"{z:.6f}" for z in e.raices])
    print("  rho =", f"{e.radio_espectral:.6f}")
    print("  n0_min =", d["n0_min_q"], " n0_crece =", d["n0_crece_q"],
          " n100 =", d["n100_q"])
    print("  q_3 =", f"{d['q'][3]:.6f}", " T_3 =", f"{d['T'][3]:.6f}")
    print("  q_6 =", f"{d['q'][6]:.6f}", " T_6 =", f"{d['T'][6]:.6f}")
    print("  q_20 =", f"{d['q'][20]:.6e}")
    print("  det(B) =", f"{info['determinante']:.6f}",
          " tr(B) =", f"{info['traza']:.6f}",
          " coincide =", info["coincide"])

print()
print("p_n: A, B =", su.forma_cerrada_p())
print("n* teorico p =", f"{su.n_teorico(su.forma_cerrada_p()[0], su.forma_cerrada_p()[1], 3.0):.4f}")

fc = su.forma_cerrada_q(False)
print()
print("q corregida, forma cerrada:")
for k, v in fc.items():
    print("  ", k, f"{v:.6e}")

amp_malo = max(abs(fc["coef_1"]), abs(fc["coef_2"]))
print("  amplitud modo 6^n =", f"{amp_malo:.6e}")
print("  n* teorico q =", f"{su.n_teorico(amp_malo, abs(fc['coef_3']), 6.0):.4f}")

print()
print("S =", float(su.S_exacta()), " sumD(inf) =", float(sum(2 * su.T_n(k) for k in range(1, 400))))
