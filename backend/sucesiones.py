"""
@file sucesiones.py
@brief Reune toda la matematica del proyecto "Sucesiones y Series" (Calculo III).
@details
Este archivo contiene los calculos del proyecto: la sucesion de areas del
triangulo, las tres recurrencias que se comparan, sus polinomios
caracteristicos, la serie infinita, las areas descartadas y la matriz companera.
No depende de la interfaz: lo usan por igual la pagina web, los scripts y la
generacion del informe.

El problema parte de un triangulo equilatero de area T0 = 1. En cada paso se une
el baricentro con los tres vertices, con lo que el triangulo queda dividido en
tres triangulos iguales de area 1/3 del anterior; se conserva uno de ellos y se
repite el proceso indefinidamente. La sucesion de areas es entonces:

    T_n = 3^(-n)        (n = 0, 1, 2, ...)

La idea central del proyecto es que esta sucesion se puede generar de tres formas
distintas (las tres recurrencias del enunciado). En aritmetica exacta las tres
deberian dar exactamente lo mismo, pero al calcularlas con numeros decimales se
comportan de forma muy diferente: unas siguen a T_n y otras se disparan. La razon
esta en las raices de sus polinomios caracteristicos, y ese es el analisis que
hace este archivo.

@par Organizacion del archivo
- termino general exacto: T_n, T_float
- las tres recurrencias: seq_r, seq_p, seq_q
- polinomios caracteristicos, raices y radio espectral: espectro_r, espectro_p,
  espectro_q (y la clase Espectro)
- matriz companera B y su analisis: matriz_B, analisis_B
- serie y areas descartadas: sumas_parciales, areas_descartadas,
  sumas_descartadas
- tabla resumen y deteccion de la divergencia: tabla, indice_minimo,
  primer_crecimiento, primer_error_relativo_100, n_teorico
- coeficientes de la forma cerrada: forma_cerrada_p, forma_cerrada_q

@note Todas las funciones devuelven datos puros (listas, numeros, diccionarios o
arreglos de numpy), de modo que se pueden usar desde cualquier interfaz.
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
    @brief Calcula el termino general de la sucesion de areas como fraccion exacta.
    @details
    En cada paso el area se multiplica por 1/3, de modo que el termino n-esimo es
    T_n = 3^(-n). Se usa la clase Fraction (en lugar de un numero decimal) para
    que el resultado sea exacto: asi, cuando mas adelante se compara esta sucesion
    con los algoritmos numericos, el error que se mide proviene solo del algoritmo
    y no de la propia referencia. Si la referencia se calculara tambien con
    decimales, su propio redondeo se sumaria al error y ensuciaria la comparacion.
    @param n Indice del termino. Debe ser un entero mayor o igual que 0 (n = 0
    devuelve 1, que es el area del triangulo original).
    @return Una fraccion exacta equivalente a 1 / 3^n.
    """
    return Fraction(1, 3) ** n


def T_float(n: int) -> float:
    """
    @brief Devuelve el mismo termino general T_n, pero como numero decimal.
    @details
    Es la version de T_n en coma flotante. Se usa sobre todo para graficar y para
    rellenar las tablas, porque matplotlib y las tablas trabajan con numeros
    decimales. Para comparar errores conviene usar T_n (la fraccion exacta).
    @param n Indice del termino (entero mayor o igual que 0).
    @return El valor de 3^(-n) como float.
    """
    return float(T_n(n))


# ----------------------------------------------------------------------------
# 2) Las tres recurrencias
# ----------------------------------------------------------------------------

def seq_r(N: int, r0: float = R0) -> list[float]:
    """
    @brief Genera la recurrencia (i): ``r_n = (1/3) * r_(n-1)``.
    @details
    Es la recurrencia mas sencilla de las tres. Cada termino es un tercio del
    anterior, igual que la sucesion de areas, por lo que sigue a T_n sin
    problemas. Su unico valor inicial es r_0 = 0.99997, que se aparta de 1 en
    3*10^(-5); pero como esta recurrencia no tiene ninguna raiz parosita, ese
    pequeno error se mantiene proporcional y no crece. Por eso este algoritmo es
    estable: la diferencia con T_n decrece como 3^(-n).

    En el analisis critico esto se justifica diciendo que su polinomio
    caracteristico es ``l - 1/3 = 0``, y su unica raiz (1/3) tiene modulo menor
    que 1, de modo que el error no se amplifica.
    @param N Indice maximo a calcular. La funcion devuelve los terminos desde
    n = 0 hasta n = N.
    @param r0 Valor inicial r_0 (por defecto 0.99997, el que da el enunciado).
    @return Lista con los terminos r_0, r_1, ..., r_N.
    """
    r = [0.0] * (N + 1)
    r[0] = r0
    for n in range(1, N + 1):
        r[n] = r[n - 1] / 3.0
    return r


def seq_p(N: int, p0: float = P0, p1: float = P1) -> list[float]:
    """
    @brief Genera la recurrencia (ii): ``p_n = (10/3) * p_(n-1) - p_(n-2)``.
    @details
    Esta recurrencia deberia producir la misma sucesion T_n, pero su polinomio
    caracteristico es ``l^2 - (10/3)l + 1 = 0``, cuyas raices son 3 y 1/3. La
    raiz 1/3 es la "buena" (la que reproduce la sucesion), pero la raiz 3 es una
    raiz parosita: cualquier pequeno error inicial se amplifica como 3^n.

    El valor p_1 = 0.33334 se aparta de 1/3 en 6.7*10^(-6); ese error, aunque
    parece minimo, activa el termino 3^n y hace que la sucesion se separe de T_n
    a partir de n aproximadamente 6. Su solucion exacta se puede escribir como
    ``p_n = A*3^n + B*3^(-n)``, con A aproximadamente 2.5*10^(-6).
    @param N Indice maximo a calcular (se devuelven n = 0..N).
    @param p0 Valor inicial p_0 (por defecto 1).
    @param p1 Valor inicial p_1 (por defecto 0.33334).
    @return Lista con los terminos p_0, p_1, ..., p_N.
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
    @details
    Es una recurrencia de tercer orden. Permite trabajar con dos juegos de
    coeficientes:
      - los impresos en el enunciado (c2 = -27 y c3 = 18), cuyo polinomio es
        ``l^3 - (28/3)l^2 + 27l - 18 = 0`` y tiene raices 4.195 +/- 1.22i y 0.943;
      - los corregidos (c2 = -21 y c3 = 6), cuyo polinomio es
        ``l^3 - (28/3)l^2 + 21l - 6 = 0``, con raices 1/3, 3 y 6.

    La version impresa no es equivalente a T_n = 3^(-n), porque 1/3 no es raiz de
    su polinomio (evaluando P(1/3) se obtiene -10). La version corregida si
    reproduce la sucesion y ademas muestra con claridad como la raiz 6 hace que el
    error crezca como 6^n. El programa permite comparar las dos versiones.
    @param N Indice maximo a calcular (se devuelven n = 0..N).
    @param q0 Valor inicial q_0 (por defecto 1).
    @param q1 Valor inicial q_1 (por defecto 1/3).
    @param q2 Valor inicial q_2 (por defecto 0.11112).
    @param c2 Coeficiente que multiplica a q_(n-2). Por defecto -27 (lo impreso).
    @param c3 Coeficiente que multiplica a q_(n-3). Por defecto 18 (lo impreso).
    @return Lista con los terminos q_0, q_1, ..., q_N.
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
    @brief Reune el polinomio caracteristico de una recurrencia, sus raices y su radio espectral.
    @details
    Es una estructura sencilla que guarda, para una recurrencia dada, las tres
    cosas que hacen falta para analizarla:
      - el polinomio caracteristico (como coeficientes, de mayor a menor grado);
      - sus raices complejas, que se obtienen con numpy.roots;
      - el radio espectral, que es el mayor de los modulos de las raices y que
        indica si la recurrencia es estable (menor que 1) o divergente (mayor
        que 1).
    Tambien incluye un pequeno texto con el nombre de la recurrencia, para
    etiquetar tablas y figuras.
    @var nombre Etiqueta legible de la recurrencia (por ejemplo "(ii) p_n").
    @var coeffs Coeficientes del polinomio monico, de mayor a menor grado.
    @var raices Raices complejas calculadas con numpy.roots.
    @var radio_espectral El mayor modulo entre las raices; si es mayor que 1 la
    recurrencia diverge.
    @var prefiere_menor_que_uno True si la recurrencia es estable (su error no
    crece con n).
    """

    nombre: str
    coeffs: np.ndarray        # monicos, de mayor a menor grado
    raices: np.ndarray        # complejas
    radio_espectral: float
    prefiere_menor_que_uno: bool  # True = estable

    @property
    def modulos(self) -> np.ndarray:
        """
        @brief Devuelve el modulo de cada raiz.
        @details
        El modulo de una raiz compleja lambda = a + bi es sqrt(a^2 + b^2). Sirve
        para comparar las raices entre si y para calcular el radio espectral
        (que es el maximo de estos modulos).
        @return Arreglo de numpy con los modulos de todas las raices.
        """
        return np.abs(self.raices)

    def latex_pol(self) -> str:
        """
        @brief Devuelve el polinomio caracteristico escrito como texto legible.
        @details
        Solo es una ayuda de presentacion: convierte los coeficientes en una
        cadena como "l^3 -(28/3)l^2 +27l -18" para poder mostrarla en tablas,
        figuras o por consola sin usar LaTeX.
        @return Cadena con el polinomio monico.
        """
        return polinomio_a_texto(self.coeffs)


def polinomio_a_texto(c: np.ndarray) -> str:
    """
    @brief Convierte un polinomio (sus coeficientes) en texto legible.
    @details
    Toma los coeficientes de mayor a menor grado y arma una cadena con potencias
    de l. Cuando un coeficiente es una fraccion sencilla (como 28/3 o 10/3) se
    escribe como fraccion, y cuando es entero se escribe sin decimales. Se usa
    para etiquetar las figuras y para el informe, de modo que el polinomio se
    lea igual que en el papel.
    @param c Coeficientes del polinomio, de mayor a menor grado.
    @return Cadena tipo "l^3 -(28/3)l^2 +27l -18".
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
    @brief Calcula el polinomio caracteristico, las raices y el radio espectral de (ii).
    @details
    El polinomio de la recurrencia (ii) es ``l^2 - (10/3)l + 1 = 0``, cuyas raices
    son 3 y 1/3. El radio espectral es 3, mayor que 1, lo que confirma que el
    algoritmo es inestable: el error se amplifica como 3^n.
    @return Instancia de :class:`Espectro` con el polinomio y sus raices.
    """
    c = np.array([1.0, -10.0 / 3.0, 1.0])
    r = np.roots(c)
    return Espectro("(ii) p_n", c, r, float(np.max(np.abs(r))), True)


def espectro_q(impreso: bool = True) -> Espectro:
    """
    @brief Calcula el polinomio, las raices y el radio espectral de (iii).
    @details
    Permite analizar las dos versiones de la recurrencia (iii):
      - la impresa en el enunciado: ``l^3 - (28/3)l^2 + 27l - 18 = 0``, con
        raices 4.195 +/- 1.22i y 0.943, y radio espectral 4.369;
      - la corregida: ``l^3 - (28/3)l^2 + 21l - 6 = 0``, con raices 1/3, 3 y 6,
        y radio espectral 6.
    El radio espectral mayor que 1 (en ambas) explica por que la sucesion
    diverge numericamente.
    @param impreso True usa la version impresa; False usa la corregida.
    @return Instancia de :class:`Espectro`.
    """
    c = (np.array([1.0, -28.0 / 3.0, 27.0, -18.0]) if impreso
         else np.array([1.0, -28.0 / 3.0, 21.0, -6.0]))
    r = np.roots(c)
    return Espectro("(iii) q_n", c, r, float(np.max(np.abs(r))), True)


def espectro_r() -> Espectro:
    """
    @brief Calcula el polinomio, la raiz y el radio espectral de (i).
    @details
    La recurrencia (i) es de primer orden y su polinomio es ``l - 1/3 = 0``, con
    una unica raiz (1/3) de modulo menor que 1. Al no tener raices parositas, es
    la unica de las tres que es estable.
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
    @brief Construye la matriz companera B del sistema X_n = B X_(n-1).
    @details
    La recurrencia (iii) es de tercer orden, pero se puede escribir como un
    sistema de primer orden agrupando tres terminos consecutivos en un vector:
    X_n = [q_n, q_(n-1), q_(n-2)]^T. Con ese vector, la recurrencia se convierte
    en X_n = B X_(n-1), donde B es la llamada matriz companera:

        B = [[28/3, -a2, a3],
             [1,      0,   0],
             [0,      1,   0]]

    La primera fila guarda los coeficientes de la recurrencia; las otras dos
    solo "desplazan" los terminos anteriores. Tiene la propiedad de que su
    polinomio caracteristico det(lI - B) coincide con el de la recurrencia.
    @param impreso True usa los coeficientes impresos (-27 y +18); False usa los
    corregidos (-21 y +6).
    @return Matriz de 3x3 de numpy.
    """
    a2 = 27.0 if impreso else 21.0
    a3 = 18.0 if impreso else 6.0
    return np.array([[28.0 / 3.0, -a2, a3],
                     [1.0, 0.0, 0.0],
                     [0.0, 1.0, 0.0]])


def analisis_B(impreso: bool = True) -> dict:
    """
    @brief Analiza la matriz companera B y comprueba que coincide con la recurrencia.
    @details
    Calcula los autovalores de B (con numpy.linalg.eig), sus modulos, el radio
    espectral (el mayor modulo), la traza y el determinante. Ademas construye el
    polinomio caracteristico de B, det(lI - B), y lo compara con el de la
    recurrencia para verificar que son el mismo; el resultado de esa comparacion
    se guarda en la clave "coincide".

    De este modo queda cubierto el punto 5 del enunciado: la matriz reproduce la
    recurrencia, y su radio espectral mayor que 1 justifica la divergencia.
    @param impreso True usa los coeficientes impresos; False los corregidos.
    @return Diccionario con las claves B, autovalores, modulos, radio_espectral,
    polinomio_B, polinomio_recurrencia, coincide, traza y determinante.
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
    @brief Devuelve el valor exacto de la serie de las areas conservadas.
    @details
    Es la suma infinita S = sum_{n>=1} 3^(-n), que es una serie geometrica de
    razon 1/3 y primer termino 1/3. Su valor exacto es 1/2. Se devuelve como
    fraccion para no arrastrar redondeo.
    @return La fraccion 1/2.
    """
    return Fraction(1, 2)


def sumas_parciales(N: int) -> list[float]:
    """
    @brief Calcula las sumas parciales de las areas conservadas.
    @details
    Para cada n, suma los primeros n terminos de T_n. La lista empieza en
    S_0 = 0 y termina en S_N; sirve para dibujar como la suma se acerca a 1/2.
    @param N Indice maximo (se devuelven S_0, S_1, ..., S_N).
    @return Lista con las sumas parciales.
    """
    acc, out = 0.0, [0.0]
    for n in range(1, N + 1):
        acc += T_float(n)
        out.append(acc)
    return out


def areas_descartadas(N: int) -> list[float]:
    """
    @brief Calcula las areas que se descartan en cada paso.
    @details
    En cada paso el triangulo se parte en tres partes iguales y se conserva una,
    asi que se descartan dos. Por eso el area descartada en el paso n es
    D_n = 2 * T_n = 2 * 3^(-n). La lista empieza en D_0 = 0 (aun no se descarta
    nada) y sigue con D_1, ..., D_N.
    @param N Indice maximo.
    @return Lista con las areas descartadas en cada paso.
    """
    return [0.0] + [2.0 * T_float(n) for n in range(1, N + 1)]


def sumas_descartadas(N: int) -> list[float]:
    """
    @brief Calcula la suma acumulada de las areas descartadas.
    @details
    Suma las areas descartadas desde el paso 1 hasta cada n. El resultado es
    1 - 3^(-n), que tiende a 1 = T_0: es decir, lo que se descarta acaba sumando
    exactamente el area del triangulo original.
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
    @brief Encuentra el primer indice en que la sucesion deja de decrecer.
    @details
    Recorre la lista desde n = 2 y devuelve el primer n en que el valor absoluto
    de x_n es mayor que el del termino anterior. Ese es el momento en que el
    error (o la raiz parosita) empieza a dominar y la sucesion comienza a crecer.
    @param x Lista de valores de la sucesion.
    @return El indice n encontrado, o None si nunca crece (sucesion estable).
    """
    for n in range(2, len(x)):
        if abs(x[n]) > abs(x[n - 1]):
            return n
    return None


def indice_minimo(x: list[float], desde: int = 1) -> int:
    """
    @brief Encuentra el indice donde el valor absoluto es minimo (el "fondo").
    @details
    Recorre la sucesion y devuelve la posicion del menor valor absoluto. En estas
    sucesiones ese punto es el "fondo": el momento en que la perturbacion iguala
    al modo bueno antes de empezar a crecer. Se usa para estimar n0 de forma
    empirica y compararlo con el valor teorico.
    @param x Lista de valores de la sucesion.
    @param desde Indice desde el que se empieza a buscar (por defecto 1).
    @return El indice del minimo de |x_n|.
    """
    mejor, idx = None, desde
    for n in range(desde, len(x)):
        v = abs(x[n])
        if np.isfinite(v) and (mejor is None or v < mejor):
            mejor, idx = v, n
    return idx


def primer_error_relativo_100(T: list[float], x: list[float]) -> int | None:
    """
    @brief Encuentra el primer indice con error relativo mayor que el 100 %.
    @details
    Compara cada termino con la referencia y devuelve el primer n en que
    |T_n - x_n| supera a T_n, es decir, en que la sucesion se aleja mas que la
    propia area de referencia. Sirve como otro criterio para medir cuando
    arranca la divergencia.
    @param T Sucesion de referencia (T_n).
    @param x Sucesion a comparar (r_n, p_n o q_n).
    @return El indice n encontrado, o None si nunca ocurre.
    """
    for n in range(min(len(T), len(x))):
        t = T[n]
        if t != 0 and abs(t - x[n]) > t:
            return n
    return None


def n_teorico(amplitud_modo_malo: float, amplitud_modo_bueno: float,
              rho: float, base: float = 3.0) -> float:
    """
    @brief Calcula el indice de cruce teorico entre el modo parosito y el verdadero.
    @details
    En una sucesion con una raiz parosita, la solucion es la suma de dos modos:
    uno bueno (que decrece como base^(-n), con base = 3) y uno malo o parosito
    (que crece o decrece como rho^n). El cruce ocurre cuando las dos amplitudes
    se igualan:

        |A_malo| rho^n = |A_bueno| base^(-n)

    Despejando n se obtiene el indice n* a partir del cual el modo malo domina:
    n* = ln(|A_bueno/A_malo|) / ln(base*rho). Este valor teorico se compara con
    el n0 que se observa en la tabla.
    @param amplitud_modo_malo Amplitud del modo parosito (A_malo).
    @param amplitud_modo_bueno Amplitud del modo verdadero (A_bueno).
    @param rho Modulo de la raiz parosita.
    @param base Base del modo verdadero (3, porque T_n = 3^(-n)).
    @return El indice de cruce n* (infinito si A_malo es 0).
    """
    if amplitud_modo_malo == 0:
        return float("inf")
    return float(np.log(abs(amplitud_modo_bueno / amplitud_modo_malo))
                 / np.log(base * rho))


def tabla(N: int, impreso: bool = True) -> dict:
    """
    @brief Reune en un solo diccionario todos los resultados hasta n = N.
    @details
    Es la funcion principal que usa la interfaz web (y los scripts) para rellenar
    tablas, tarjetas y graficas sin recalcular nada. Calcula las cuatro
    sucesiones (T, r, p y q), sus errores absolutos y relativos, las sumas
    parciales de la serie, las areas descartadas y los indices de divergencia
    (n0 por minimo, n0 por crecimiento y el primer n con error relativo > 100 %).
    @param N Indice maximo a calcular.
    @param impreso True para la recurrencia (iii) tal como esta en el PDF;
    False para la version corregida.
    @return Diccionario con, entre otras claves: n, T, r, p, q (listas), err_*
    (errores absolutos), rel_* (errores relativos), n0_min_*, n0_crece_*,
    n100_* (indices de divergencia), S (sumas parciales de T_n), D (areas
    descartadas) y SD (suma acumulada de D).
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
    @brief Calcula los coeficientes de la solucion cerrada de la recurrencia (ii).
    @details
    La solucion general de la recurrencia (ii) es p_n = A*3^n + B*3^(-n), porque
    sus raices son 3 y 1/3. Para encontrar A y B se plantea un sistema con las
    condiciones iniciales p_0 = 1 y p_1 = 0.33334, y se resuelve con numpy
    (linalg.solve). El coeficiente A (aproximadamente 2.5*10^(-6)) mide la
    amplitud del modo parosito; con el se puede calcular el n* teorico.
    @return Tupla (A, B) con las dos amplitudes.
    """
    M = np.array([[1.0, 1.0], [3.0, 1.0 / 3.0]])
    A, B = np.linalg.solve(M, np.array([P0, P1]))
    return float(A), float(B)


def forma_cerrada_q(impreso: bool = True) -> dict[str, complex]:
    """
    @brief Calcula los coeficientes de la solucion cerrada de la recurrencia (iii).
    @details
    Con las tres raices lambda_1, lambda_2 y lambda_3 del polinomio caracteristico,
    la solucion general se escribe como
    q_n = c1*lambda_1^n + c2*lambda_2^n + c3*lambda_3^n.
    Para encontrar c1, c2 y c3 se plantea un sistema de Vandermonde con las
    condiciones iniciales q0, q1 y q2, y se resuelve con numpy. Los coeficientes
    de los modos con modulo mayor que 1 (los parositos) son los que determinan la
    divergencia.
    @param impreso True usa el polinomio impreso; False el corregido.
    @return Diccionario con las claves lam_1, lam_2, lam_3 (raices) y coef_1,
    coef_2, coef_3 (amplitudes de cada modo).
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
