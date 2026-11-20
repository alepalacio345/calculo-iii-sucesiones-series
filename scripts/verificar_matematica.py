"""Verificacion numerica del proyecto Sucesiones y Series."""
import numpy as np
from fractions import Fraction as F

np.set_printoptions(precision=10, suppress=False)

N = 20

def T(n):  return F(1, 3) ** n

print("=" * 70)
print("1) Tn = 3^-n")
print("=" * 70)
for n in range(0, 8):
    print(f"  T_{n} = {T(n)} = {float(T(n)):.10e}")

# --- (i) r_n = (1/3) r_{n-1}, r0 = 0.99997 ---
r = [0.0] * (N + 1)
r[0] = 0.99997
for n in range(1, N + 1):
    r[n] = r[n - 1] / 3.0

# --- (ii) p_n = (10/3) p_{n-1} - p_{n-2} ---
p = [0.0] * (N + 1)
p[0], p[1] = 1.0, 0.33334
for n in range(2, N + 1):
    p[n] = (10.0 / 3.0) * p[n - 1] - p[n - 2]

# --- (iii) q_n = (28/3) q_{n-1} - 27 q_{n-2} + 18 q_{n-3}  (AS PRINTED) ---
q = [0.0] * (N + 1)
q[0], q[1], q[2] = 1.0, 1.0 / 3.0, 0.11112
for n in range(3, N + 1):
    q[n] = (28.0 / 3.0) * q[n - 1] - 27.0 * q[n - 2] + 18.0 * q[n - 3]

# --- (iii') q_n = (28/3) q_{n-1} - 21 q_{n-2} + 6 q_{n-3}  (candidate fix) ---
q2 = [0.0] * (N + 1)
q2[0], q2[1], q2[2] = 1.0, 1.0 / 3.0, 0.11112
for n in range(3, N + 1):
    q2[n] = (28.0 / 3.0) * q2[n - 1] - 21.0 * q2[n - 2] + 6.0 * q2[n - 3]

print()
print("=" * 70)
print("2) Tabla comparativa")
print("=" * 70)
hdr = f"{'n':>3} {'T_n':>14} {'r_n':>14} {'p_n':>14} {'q_n(impreso)':>16} {'q_n(21,6)':>14}"
print(hdr)
print("-" * len(hdr))
for n in range(0, N + 1):
    print(f"{n:3d} {float(T(n)):14.6e} {r[n]:14.6e} {p[n]:14.6e} "
          f"{q[n]:16.6e} {q2[n]:14.6e}")

print()
print("=" * 70)
print("3) Diferencias absolutas |T_n - x_n|")
print("=" * 70)
hdr = f"{'n':>3} {'|T-r|':>13} {'|T-p|':>13} {'|T-q|':>13} {'|T-q2|':>13}"
print(hdr)
print("-" * len(hdr))
for n in range(0, N + 1):
    t = float(T(n))
    print(f"{n:3d} {abs(t-r[n]):13.4e} {abs(t-p[n]):13.4e} "
          f"{abs(t-q[n]):13.4e} {abs(t-q2[n]):13.4e}")

print()
print("=" * 70)
print("4) Polinomios caracteristicos y raices")
print("=" * 70)

polys = {
    "(ii)  L^2 - (10/3)L + 1": np.array([1.0, -10.0 / 3.0, 1.0]),
    "(iii) printed L^3 - (28/3)L^2 + 27L - 18": np.array([1.0, -28.0 / 3.0, 27.0, -18.0]),
    "(iii) alt     L^3 - (28/3)L^2 + 21L - 6 ": np.array([1.0, -28.0 / 3.0, 21.0, -6.0]),
}
for name, c in polys.items():
    roots = np.roots(c)
    print(f"\n  {name}")
    print(f"    raices = {np.array2string(roots, precision=8)}")
    print(f"    |raices| = {np.array2string(np.abs(roots), precision=8)}")
    print(f"    radio espectral = {np.max(np.abs(roots)):.8f}")

print()
print("  Test exacto de L=1/3 en el polinomio impreso:")
c = np.array([1.0, -28.0 / 3.0, 27.0, -18.0])
print("    P(1/3) =", np.polyval(c, 1.0 / 3.0), "  <-- debe ser 0 si 1/3 es raiz")

print()
print("=" * 70)
print("5) Matriz companera B (segun enunciado)")
print("=" * 70)
B = np.array([[28.0 / 3.0, -27.0, 18.0],
              [1.0, 0.0, 0.0],
              [0.0, 1.0, 0.0]])
print(B)
print("  det(B - L I) expandido ->", np.poly(B))
print("  coef. esperados [1, -28/3, 27, -18] =", [1.0, -28.0 / 3.0, 27.0, -18.0])
ev = np.linalg.eigvals(B)
print("  eig(B) =", np.array2string(ev, precision=8))
print("  |eig(B)| =", np.array2string(np.abs(ev), precision=8))
print("  rho(B) =", np.max(np.abs(ev)))

print()
print("=" * 70)
print("6) Serie S = sum Tn (n >= 1) y areas descartadas Dn = 2*Tn")
print("=" * 70)
S = sum(T(n) for n in range(1, 200))
print("  S =", S, "=", float(S), "  (exacto: 1/2)")
D = sum(2 * T(n) for n in range(1, 200))
print("  sumD_n (n>=1) =", D, "=", float(D), "  (exacto: 1)")

print()
print("=" * 70)
print("7) Indice de cruce / divergencia (primer n con |T-p| > |T|)")
print("=" * 70)
for label, seq in (("p", p), ("q impreso", q), ("q 21,6", q2)):
    for n in range(0, N + 1):
        if abs(float(T(n)) - seq[n]) > float(T(n)):
            print(f"  {label}: primer n = {n}  (|T_n - x_n| = {abs(float(T(n))-seq[n]):.3e} > T_n = {float(T(n)):.3e})")
            break
    else:
        print(f"  {label}: no cruza en n<= {N}")

print()
print("  r: |T_n - r_n| / T_n =", abs(float(T(10)) - r[10]) / float(T(10)), "(constante, error relativo)")
