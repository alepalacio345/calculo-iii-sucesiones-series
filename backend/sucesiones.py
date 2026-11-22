"""
@file sucesiones.py
@brief Backend matematico del proyecto "Sucesiones y Series" (Calculo III).
@details
Triangulo equilatero de area T0 = 1. En cada paso se une el baricentro con
los tres vertices: el triangulo queda partido en tres triangulos congruentes
de area 1/3 del anterior, se conserva uno y se repite indefinidamente.

    T_n = 3^(-n)        (n = 0, 1, 2, ...)

Este modulo NO depende de la interfaz: lo usan la app (frontend), los scripts y
el informe. Solo produce datos puros (listas, floats, dicts, numpy.ndarray).

@par Contenido
- termino general exacto (T_n, T_float)
- las tres recurrencias (seq_r, seq_p, seq_q)
- polinomios caracteristicos, raices y radio espectral (espectro_*)
- matriz companera B y su analisis (matriz_B, analisis_B)
- serie y areas descartadas (sumas_parciales, areas_descartadas, ...)
- tabla resumen y deteccion del indice de divergencia (tabla, n_teorico)
- coeficientes de la forma cerrada (forma_cerrada_p, forma_cerrada_q)
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import numpy as np

# ----------------------------------------------------------------------------
# Parametros por defecto del enunciado
# ----------------------------------------------------------------------------

R0 = 0.99997          # (i)  r_0
P0, P1 = 1.0, 0.33334  # (ii) p_0, p_1
Q0, Q1, Q2 = 1.0, 1.0 / 3.0, 0.11112  # (iii) q_0, q_1, q_2

# (iii) tal como esta impreso en el PDF:  q_n = (28/3)q_{n-1} - 27q_{n-2} + 18q_{n-3}
Q_A1_IMPRESO, Q_C2_IMPRESO, Q_C3_IMPRESO = 28.0 / 3.0, -27.0, 18.0
# (iii) coherente con q_n -> 3^(-n):  q_n = (28/3)q_{n-1} - 21q_{n-2} + 6q_{n-3}
#       (raices 1/3, 3 y 6 -> mismo patron que (ii) pero con divergencia 6^n)
Q_A1_FIX, Q_C2_FIX, Q_C3_FIX = 28.0 / 3.0, -21.0, 6.0


# ----------------------------------------------------------------------------
# 1) Termino general exacto
# ----------------------------------------------------------------------------

def T_n(n: int) -> Fraction:
    """
    @brief Termino general exacto T_n = 3^(-n) como fraccion.
    @details Usa :class:`~fractions.Fraction` para que la *referencia* no arrastre
    su propio error de redondeo cuando se compara contra las recurrencias.
    @param n Indice del termino (n >= 0).
    @return :class:`~fractions.Fraction` igual a ``1 / 3**n``.
    """
    return Fraction(1, 3) ** n


def T_float(n: int) -> float:
    """
    @brief Version en coma flotante de :func:`T_n` (para graficar/tabular).
    @param n Indice del termino.
    @return ``1 / 3**n`` como float.
    """
    return float(T_n(n))


# ----------------------------------------------------------------------------
# 2) Las tres recurrencias
# ----------------------------------------------------------------------------

def seq_r(N: int, r0: float = R0) -> list[float]:
    """
    @brief Genera la recurrencia (i): ``r_n = (1/3) r_(n-1)``.
    @param N Indice maximo a calcular.
    @param r0 Valor inicial ``r_0`` (por defecto 0.99997).
    @return Lista ``r[0..N]``.
    """
    r = [0.0] * (N + 1)
    r[0] = r0
    for n in range(1, N + 1):
        r[n] = r[n - 1] / 3.0
    return r


def seq_p(N: int, p0: float = P0, p1: float = P1) -> list[float]:
    """
    @brief Genera la recurrencia (ii): ``p_n = (10/3) p_(n-1) - p_(n-2)``.
    @param N Indice maximo a calcular.
    @param p0 Valor inicial ``p_0`` (por defecto 1).
    @param p1 Valor inicial ``p_1`` (por defecto 0.33334).
    @return Lista ``p[0..N]``.
    """
    p = [0.0] * (N + 1)
    p[0] = p0
    if N >= 1:
        p[1] = p1
    for n in range(2, N + 1):
        p[n] = (10.0 / 3.0) * p[n - 1] - p[n - 2]
    return p


def seq_q(N: int, q0: float = Q0, q1: float = Q1, q2: float = Q2,
          c2: float = Q_C2_IMPRESO, c3: float = Q_C3_IMPRESO) -> list[float]:
    """
    @brief Genera la recurrencia (iii):
           ``q_n = (28/3) q_(n-1) + c2 q_(n-2) + c3 q_(n-3)``.
    @param N Indice maximo a calcular (devuelve n = 0..N).
    @param q0 Valor inicial ``q_0`` (por defecto 1).
    @param q1 Valor inicial ``q_1`` (por defecto 1/3).
    @param q2 Valor inicial ``q_2`` (por defecto 0.11112).
    @param c2 Coeficiente de ``q_(n-2)`` (por defecto -27, lo impreso).
    @param c3 Coeficiente de ``q_(n-3)`` (por defecto 18, lo impreso).
    @return Lista ``q[0..N]`` con los terminos de la recurrencia.
    """
    a1 = 28.0 / 3.0
    q = [0.0] * (N + 1)
    q[0] = q0
    if N >= 1:
        q[1] = q1
    if N >= 2:
        q[2] = q2
    for n in range(3, N + 1):
        q[n] = a1 * q[n - 1] + c2 * q[n - 2] + c3 * q[n - 3]
    return q


# ----------------------------------------------------------------------------
# 3) Polinomios caracteristicos, raices y radio espectral
# ----------------------------------------------------------------------------

@dataclass
class Espectro:
    """
    @brief Espectro de una recurrencia: polinomio caracteristico, raices y rho.
    @details Agrupa el polinomio monico, sus raices complejas y el radio
    espectral (max |raiz|), que determina si la recurrencia es estable.
    @var nombre Etiqueta legible de la recurrencia (p. ej. "(ii) p_n").
    @var coeffs Coeficientes del polinomio monico, de mayor a menor grado.
    @var raices Raices complejas (numpy.roots).
    @var radio_espectral max |raiz|; si es > 1 la recurrencia diverge.
    @var prefiere_menor_que_uno True si la recurrencia es estable.
    """

    nombre: str
    coeffs: np.ndarray        # monicos, de mayor a menor grado
    raices: np.ndarray        # complejas
    radio_espectral: float
    prefiere_menor_que_uno: bool  # True = estable

    @property
    def modulos(self) -> np.ndarray:
        """
        @brief Modulos |raiz| de todas las raices.
        @return Arreglo numpy con los modulos de las raices.
        """
        return np.abs(self.raices)

    def latex_pol(self) -> str:
        """
        @brief Polinomio caracteristico como texto legible.
        @return Cadena que representa el polinomio monico.
        """
        return polinomio_a_texto(self.coeffs)


def polinomio_a_texto(c: np.ndarray) -> str:
    """
    @brief Devuelve el polinomio monico como texto legible.
    @param c Coeficientes del polinomio, de mayor a menor grado.
    @return Cadena tipo "l^3 - (28/3)l^2 + 27l - 18".
    """
    grados = len(c) - 1
    partes = []
    for i, coef in enumerate(c):
        g = grados - i
        if abs(coef) < 1e-14:
            continue
        signo = "-" if coef < 0 else ("+" if partes else "")
        mag = abs(coef)
        frac = Fraction(mag).limit_denominator(1000)
        if frac.denominator == 1:
            txt = f"{int(frac)}"
        else:
            txt = f"({frac.numerator}/{frac.denominator})"
        if g == 0:
            cuerpo = txt
        elif g == 1:
            cuerpo = f"{'' if txt == '1' else txt}l"
        else:
            cuerpo = f"{'' if txt == '1' else txt}l^{g}"
        partes.append(f"{signo}{cuerpo}")
    return " ".join(partes).strip()


def espectro_p() -> Espectro:
    """
    @brief Espectro de (ii): ``l^2 - (10/3) l + 1 = 0``, raices 3 y 1/3.
    @return Instancia de :class:`Espectro` con el polinomio y sus raices.
    """
    c = np.array([1.0, -10.0 / 3.0, 1.0])
    r = np.roots(c)
    return Espectro("(ii) p_n", c, r, float(np.max(np.abs(r))), True)


def espectro_q(impreso: bool = True) -> Espectro:
    """
    @brief Espectro de (iii).
    @details Version impresa: ``l^3 - (28/3)l^2 + 27l - 18 = 0``.
    Version corregida: ``l^3 - (28/3)l^2 + 21l - 6 = 0`` (raices 1/3, 3, 6).
    @param impreso True usa la version impresa; False la corregida.
    @return Instancia de :class:`Espectro`.
    """
    c = (np.array([1.0, -28.0 / 3.0, 27.0, -18.0]) if impreso
         else np.array([1.0, -28.0 / 3.0, 21.0, -6.0]))
    r = np.roots(c)
    return Espectro("(iii) q_n", c, r, float(np.max(np.abs(r))), True)


def espectro_r() -> Espectro:
    """
    @brief Espectro de (i): ``l - 1/3 = 0`` (primer orden, sin raiz parasita).
    @return Instancia de :class:`Espectro`.
    """
    c = np.array([1.0, -1.0 / 3.0])
    r = np.roots(c)
    return Espectro("(i) r_n", c, r, float(np.max(np.abs(r))), True)


# ----------------------------------------------------------------------------
# 4) Matriz companera (punto 5)
# ----------------------------------------------------------------------------

def matriz_B(impreso: bool = True) -> np.ndarray:
    """
    @brief Construye la matriz companera B (X_n = B X_(n-1)).
    @details El vector de estado es X_n = [q_n, q_(n-1), q_(n-2)]^T.
    @param impreso True usa los coeficientes impresos (-27, +18); False los
    corregidos (-21, +6).
    @return Matriz 3x3 de numpy.
    """
    a2 = 27.0 if impreso else 21.0
    a3 = 18.0 if impreso else 6.0
    return np.array([[28.0 / 3.0, -a2, a3],
                     [1.0, 0.0, 0.0],
                     [0.0, 1.0, 0.0]])


def analisis_B(impreso: bool = True) -> dict:
    """
    @brief Analisis espectral de la matriz companera B (punto 5 del enunciado).
    @param impreso True usa los coeficientes impresos (-27, +18); False los
    corregidos (-21, +6).
    @return Diccionario con: ``B`` (matriz 3x3), ``autovalores``, ``modulos``,
    ``radio_espectral``, ``polinomio_B`` (``det(lI - B)``),
    ``polinomio_recurrencia``, ``coincide`` (booleano que indica si ambos
    polinomios coinciden), ``traza`` y ``determinante``.
    """
    B = matriz_B(impreso)
    auto = np.linalg.eigvals(B)
    pol_B = np.poly(B)                       # coeficientes de det(lI - B)
    pol_rec = espectro_q(impreso).coeffs      # polinomio de la recurrencia
    return {
        "B": B,
        "autovalores": auto,
        "modulos": np.abs(auto),
        "radio_espectral": float(np.max(np.abs(auto))),
        "polinomio_B": pol_B,
        "polinomio_recurrencia": pol_rec,
        "coincide": bool(np.allclose(pol_B, pol_rec, atol=1e-10)),
        "traza": float(np.trace(B)),
        "determinante": float(np.linalg.det(B)),
    }


# ----------------------------------------------------------------------------
# 5) Serie, sumas parciales y areas descartadas (puntos 3 y 4)
# ----------------------------------------------------------------------------

def S_exacta() -> Fraction:
    """
    @brief Valor exacto de la serie: ``sum_{n>=1} 3^(-n) = 1/2``.
    @return Fraccion 1/2.
    """
    return Fraction(1, 2)


def sumas_parciales(N: int) -> list[float]:
    """
    @brief Sumas parciales ``S_N = sum_{n=1}^{N} T_n``.
    @param N Indice maximo.
    @return Lista con S_0 = 0 y S_1 .. S_N.
    """
    acc, out = 0.0, [0.0]
    for n in range(1, N + 1):
        acc += T_float(n)
        out.append(acc)
    return out


def areas_descartadas(N: int) -> list[float]:
    """
    @brief Area descartada en cada paso: ``D_n = 2 * T_n``.
    @details En cada paso se descartan dos de las tres partes iguales.
    @param N Indice maximo.
    @return Lista con D_0 = 0 y D_1 .. D_N.
    """
    return [0.0] + [2.0 * T_float(n) for n in range(1, N + 1)]


def sumas_descartadas(N: int) -> list[float]:
    """
    @brief Suma acumulada de las areas descartadas.
    @details ``sum_{k=1}^{n} D_k = 1 - 3^(-n)``, que tiende a 1 = T_0.
    @param N Indice maximo.
    @return Lista con la suma acumulada hasta cada n.
    """
    acc, out = 0.0, [0.0]
    for n in range(1, N + 1):
        acc += 2.0 * T_float(n)
        out.append(acc)
    return out


# ----------------------------------------------------------------------------
# 6) Tablas y deteccion de divergencia
# ----------------------------------------------------------------------------

def primer_crecimiento(x: list[float]) -> int | None:
    """
    @brief Primer n >= 2 con |x_n| > |x_(n-1)| (la sucesion deja de decrecer).
    @param x Lista de valores de la sucesion.
    @return Indice n, o None si nunca crece.
    """
    for n in range(2, len(x)):
        if abs(x[n]) > abs(x[n - 1]):
            return n
    return None


def indice_minimo(x: list[float], desde: int = 1) -> int:
    """
    @brief Indice donde |x_n| es minimo ("fondo" de la sucesion).
    @details Es el punto en que la perturbacion empieza a dominar al modo bueno.
    @param x Lista de valores.
    @param desde Indice desde el que se busca (por defecto 1).
    @return Indice del minimo de |x_n|.
    """
    mejor, idx = None, desde
    for n in range(desde, len(x)):
        v = abs(x[n])
        if np.isfinite(v) and (mejor is None or v < mejor):
            mejor, idx = v, n
    return idx


def primer_error_relativo_100(T: list[float], x: list[float]) -> int | None:
    """
    @brief Primer n con |T_n - x_n| > T_n (error relativo > 100 %).
    @param T Sucesion de referencia.
    @param x Sucesion a comparar.
    @return Indice n, o None si nunca ocurre.
    """
    for n in range(min(len(T), len(x))):
        t = T[n]
        if t != 0 and abs(t - x[n]) > t:
            return n
    return None


def n_teorico(amplitud_modo_malo: float, amplitud_modo_bueno: float,
              rho: float, base: float = 3.0) -> float:
    """
    @brief Indice de cruce teorico entre el modo parasito y el verdadero.
    @details Resuelve ``|A_malo| rho^n = |A_bueno| base^(-n)``, es decir
    ``n* = ln(|A_bueno/A_malo|) / ln(base*rho)``.
    @param amplitud_modo_malo Amplitud del modo espurio (A_malo).
    @param amplitud_modo_bueno Amplitud del modo verdadero (A_bueno).
    @param rho Radio espectral del modo espurio.
    @param base Base del modo verdadero (3, por T_n = 3^(-n)).
    @return Indice de cruce n* (o infinito si A_malo es 0).
    """
    if amplitud_modo_malo == 0:
        return float("inf")
    return float(np.log(abs(amplitud_modo_bueno / amplitud_modo_malo))
                 / np.log(base * rho))


def tabla(N: int, impreso: bool = True) -> dict:
    """
    @brief Resumen completo para n = 0..N: sucesiones, errores, series e indices.
    @details Es la funcion que consume la interfaz (y los scripts) para rellenar
    tablas, metricas y graficas sin rehacer los calculos.
    @param N Indice maximo a calcular.
    @param impreso True para la recurrencia (iii) tal como esta en el PDF;
    False para la version corregida.
    @return Diccionario con, entre otras claves: ``n``, ``T``, ``r``, ``p``,
    ``q`` (listas), ``err_*`` (errores absolutos), ``rel_*`` (errores
    relativos), ``n0_min_*``/``n0_crece_*``/``n100_*`` (indices de divergencia),
    ``S`` (sumas parciales de T_n), ``D`` (areas descartadas) y ``SD`` (suma
    acumulada de D).
    """
    T = [T_float(n) for n in range(N + 1)]
    r = seq_r(N)
    p = seq_p(N)
    c2, c3 = (Q_C2_IMPRESO, Q_C3_IMPRESO) if impreso else (Q_C2_FIX, Q_C3_FIX)
    q = seq_q(N, c2=c2, c3=c3)
    return {
        "n": list(range(N + 1)),
        "T": T,
        "r": r, "p": p, "q": q,
        "err_r": [abs(T[i] - r[i]) for i in range(N + 1)],
        "err_p": [abs(T[i] - p[i]) for i in range(N + 1)],
        "err_q": [abs(T[i] - q[i]) for i in range(N + 1)],
        "rel_r": [abs(T[i] - r[i]) / T[i] if T[i] else 0.0 for i in range(N + 1)],
        "rel_p": [abs(T[i] - p[i]) / T[i] if T[i] else 0.0 for i in range(N + 1)],
        "rel_q": [abs(T[i] - q[i]) / T[i] if T[i] else 0.0 for i in range(N + 1)],
        # --- indices de divergencia ---
        "n0_crece_r": primer_crecimiento(r),
        "n0_crece_p": primer_crecimiento(p),
        "n0_crece_q": primer_crecimiento(q),
        "n0_min_r": indice_minimo(r),
        "n0_min_p": indice_minimo(p),
        "n0_min_q": indice_minimo(q),
        "n100_r": primer_error_relativo_100(T, r),
        "n100_p": primer_error_relativo_100(T, p),
        "n100_q": primer_error_relativo_100(T, q),
        "S": sumas_parciales(N),
        "D": areas_descartadas(N),
        "SD": sumas_descartadas(N),
    }


# ----------------------------------------------------------------------------
# 7) Coeficientes de la forma cerrada (para el analisis critico)
# ----------------------------------------------------------------------------

def forma_cerrada_p() -> tuple[float, float]:
    """
    @brief Coeficientes de la forma cerrada ``p_n = A*3^n + B*3^(-n)``.
    @details Se obtienen de las condiciones iniciales p_0 = 1, p_1 = 0.33334.
    @return Tupla (A, B).
    """
    M = np.array([[1.0, 1.0], [3.0, 1.0 / 3.0]])
    A, B = np.linalg.solve(M, np.array([P0, P1]))
    return float(A), float(B)


def forma_cerrada_q(impreso: bool = True) -> dict[str, complex]:
    """
    @brief Coeficientes de la forma cerrada ``q_n = sum(coef_i * lam_i**n)``.
    @details Resuelve el sistema de Vandermonde formado por las tres raices del
    polinomio caracteristico y las condiciones iniciales (q0, q1, q2).
    @param impreso True usa el polinomio impreso; False el corregido.
    @return Diccionario ``{"lam_1", "lam_2", "lam_3", "coef_1", "coef_2",
    "coef_3"}`` con raices y amplitudes (complejas) de cada modo.
    """
    e = espectro_q(impreso)
    lam = e.raices
    # M[k, j] = lam_j ** k  ->  M @ coef = [q_0, q_1, q_2]
    M = np.array([[l ** k for l in lam] for k in range(3)], dtype=complex)
    coef = np.linalg.solve(M, np.array([Q0, Q1, Q2], dtype=complex))
    return {f"lam_{i+1}": lam[i] for i in range(3)} | {
        f"coef_{i+1}": complex(coef[i]) for i in range(3)
    }


if __name__ == "__main__":
    d = tabla(12)
    print("n      T_n          r_n          p_n          q_n")
    for i in range(13):
        print(f"{i:2d} {d['T'][i]:12.6e} {d['r'][i]:12.6e} "
              f"{d['p'][i]:12.6e} {d['q'][i]:12.6e}")
    print()
    for e in (espectro_r(), espectro_p(), espectro_q(True), espectro_q(False)):
        raices = ", ".join(f"{z:.6g}" for z in e.raices)
        print(f"{e.nombre:10s} P(l) = {e.latex_pol():35s} "
              f"raices: {raices:45s} rho = {e.radio_espectral:.6f}")
    print()
    print("n0 (minimo):", d["n0_min_r"], d["n0_min_p"], d["n0_min_q"])
    print("n0 (crece) :", d["n0_crece_r"], d["n0_crece_p"], d["n0_crece_q"])
    print("A, B de p:", forma_cerrada_p())
