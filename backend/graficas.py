"""
@file graficas.py
@brief Figuras del proyecto (solo matplotlib).
@details Cada funcion devuelve un objeto Figure que la interfaz web convierte a
PNG y que los scripts pueden guardar como archivo.

@par Convencion de colores (la misma en todas las figuras)
- T_n  negro, continua, gruesa (referencia exacta)
- r_n  azul, discontinua
- p_n  naranja, raya-punto
- q_n  rojo, continua
"""

from __future__ import annotations

import math

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": ":",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "mathtext.fontset": "dejavusans",
    "figure.autolayout": False,
})

C_T = "#111111"
C_R = "#1f77b4"
C_P = "#e07b00"
C_Q = "#c1121f"


def _titulo(ax, texto: str) -> None:
    """
    @brief Titulo de panel, en negrita y alineado a la izquierda.
    @param ax Ejes de matplotlib donde se escribe el titulo.
    @param texto Texto del titulo.
    @return None.
    """
    ax.set_title(texto, fontweight="bold", loc="left")


# ---------------------------------------------------------------------------
# Figura 1: las cuatro sucesiones
# ---------------------------------------------------------------------------

def fig_sucesiones(d: dict, modelo: str = "impreso") -> Figure:
    """
    @brief Paneles comparativos: escala lineal y escala logaritmica.
    @param d Diccionario de :func:`backend.sucesiones.tabla`.
    @param modelo "impreso" o "corregido" (solo etiqueta la figura).
    @return Objeto Figure con dos paneles.
    """
    n = np.array(d["n"])
    T = np.array(d["T"])
    r = np.array(d["r"])
    p = np.array(d["p"])
    q = np.array(d["q"])

    fig = plt.figure(figsize=(9.2, 5.6), dpi=110)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    # --- izquierda: escala lineal, ventana acotada ---
    ax1.plot(n, T, color=C_T, lw=2.4, label=r"$T_n=3^{-n}$")
    ax1.plot(n, r, color=C_R, ls="--", lw=1.5, label=r"$r_n$")
    ax1.plot(n, p, color=C_P, ls="-.", lw=1.5, label=r"$p_n$")
    ax1.plot(n, q, color=C_Q, ls="-", lw=1.3, label=r"$q_n$")
    ax1.set_xlabel("$n$")
    ax1.set_ylabel("valor")
    ax1.set_ylim(-0.35, 1.15)
    ax1.set_xlim(-0.4, n[-1] + 0.4)
    ax1.legend(loc="upper right", fontsize=8, framealpha=0.9)
    _titulo(ax1, "(a) Escala lineal: p y q se salen de la ventana")

    # --- derecha: semilog, valor absoluto ---
    ax2.semilogy(n, np.abs(T), color=C_T, lw=2.4, label=r"$T_n$")
    ax2.semilogy(n, np.abs(r), color=C_R, ls="--", lw=1.5, label=r"$|r_n|$")
    ax2.semilogy(n, np.abs(p), color=C_P, ls="-.", lw=1.5, label=r"$|p_n|$")
    ax2.semilogy(n, np.abs(q), color=C_Q, ls="-", lw=1.3, label=r"$|q_n|$")
    ax2.set_xlabel("$n$")
    ax2.set_ylabel(r"$|x_n|$  (escala log)")
    ax2.legend(loc="lower left", fontsize=8, framealpha=0.9)
    _titulo(ax2, "(b) Escala logarítmica: quién decae y quién explota")

    fig.tight_layout()
    return fig


def fig_sucesiones_detalle(d: dict, modelo: str = "impreso") -> Figure:
    """
    @brief Un panel por recurrencia, con la referencia T_n encima.
    @param d Diccionario de :func:`backend.sucesiones.tabla`.
    @param modelo "impreso" o "corregido".
    @return Objeto Figure con cuatro paneles.
    """
    n = np.array(d["n"])
    T = np.array(d["T"])
    r = np.array(d["r"])
    p = np.array(d["p"])
    q = np.array(d["q"])
    fig = plt.figure(figsize=(9.2, 6.4), dpi=110)
    casos = [
        (r, C_R, "--", r"(i) $r_n=\frac{1}{3}r_{n-1}$   —  sin raíz parásita",
         r"$r_n$"),
        (p, C_P, "-.", r"(ii) raíz parásita $\lambda=3$", r"$p_n$"),
        (q, C_Q, "-", r"(iii) recurrencia de orden 3", r"$q_n$"),
    ]
    for k, (x, color, ls, tit, lab) in enumerate(casos, start=1):
        ax = fig.add_subplot(2, 2, k)
        ax.semilogy(n, np.abs(T), color=C_T, lw=2.2, label=r"$T_n$ exacta")
        ax.semilogy(n, np.abs(np.array(x)), color=color, ls=ls, lw=1.5,
                    label=f"$|{lab.strip('$')}|$")
        ax.set_xlabel("$n$")
        ax.set_ylabel("escala log")
        ax.legend(fontsize=7.5, loc="upper left")
        _titulo(ax, tit)

    # panel resumen
    ax = fig.add_subplot(2, 2, 4)
    ax.semilogy(n, np.abs(np.array(d["T"]) - np.array(r)), color=C_R,
                ls="--", lw=1.6, label=r"$|T_n-r_n|$")
    ax.semilogy(n, np.abs(np.array(d["T"]) - np.array(p)), color=C_P,
                ls="-.", lw=1.6, label=r"$|T_n-p_n|$")
    ax.semilogy(n, np.abs(np.array(d["T"]) - np.array(q)), color=C_Q,
                ls="-", lw=1.6, label=r"$|T_n-q_n|$")
    ax.set_xlabel("$n$")
    ax.set_ylabel("escala log")
    ax.legend(fontsize=7.5, loc="lower right")
    _titulo(ax, "Error absoluto: ¿decrece, se estanca o crece?")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figura 2: diferencias
# ---------------------------------------------------------------------------

def fig_diferencias(d: dict, relativa: bool = False) -> Figure:
    """
    @brief Figura de errores: (a) |T_n - x_n| y (b) su raiz n-esima -> |lambda|.
    @param d Diccionario de :func:`backend.sucesiones.tabla`.
    @param relativa True para usar el error relativo en el panel (a).
    @return Objeto Figure con dos paneles.
    """
    n = np.array(d["n"])
    fig = plt.figure(figsize=(9.2, 4.4), dpi=110)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    clave = "rel_" if relativa else "err_"
    etiqueta = "error relativo" if relativa else "error absoluto"

    for suf, color, ls, lab in (
        ("r", C_R, "--", r"$|T_n-r_n|$"),
        ("p", C_P, "-.", r"$|T_n-p_n|$"),
        ("q", C_Q, "-", r"$|T_n-q_n|$"),
    ):
        serie = np.abs(np.array(d[clave + suf]))
        serie[serie == 0] = np.nan
        if relativa:
            ax1.semilogx(n, serie, color=color, ls=ls, lw=1.6,
                         marker="o", ms=2.4, label=lab)
            ax1.set_ylabel(r"$|T_n-x_n|/T_n$")
        else:
            ax1.semilogy(n, serie, color=color, ls=ls, lw=1.6,
                         marker="o", ms=2.4, label=lab)
            ax1.set_ylabel(r"$|T_n-x_n|$")
        ax1.set_xlabel("$n$")
    if relativa:
        ax1.axhline(1.0, color="gray", lw=1, ls=":", label="100 % de error")
    ax1.legend(fontsize=7.5, loc="best")
    _titulo(ax1, f"(a) {etiqueta.capitalize()} en escala log")

    # (b) raiz n-esima del error -> converge al autovalor dominante |lambda_max|
    refs = [
        ("r", C_R, "--", 1.0 / 3.0, r"$|\lambda|=1/3$"),
        ("p", C_P, "-.", 3.0, r"$|\lambda|=3$"),
        ("q", C_Q, "-", None, r"$|\lambda|=\rho$"),
    ]
    for suf, color, ls, valor, lab in refs:
        err = np.abs(np.array(d["err_" + suf], dtype=float))
        nn = np.arange(len(err), dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            raiz = np.where((err > 0) & (nn > 0), err ** (1.0 / np.maximum(nn, 1)), np.nan)
        ax2.semilogy(nn[1:], raiz[1:], color=color, ls=ls, lw=1.7, label=lab)
        if valor is not None:
            ax2.axhline(valor, color=color, lw=0.9, ls=":", alpha=0.7)
    ax2.axhline(1.0, color="gray", lw=1.0, ls="--", label="frontera de estabilidad")
    ax2.set_xlabel("$n$")
    ax2.set_ylabel(r"$|T_n-x_n|^{1/n}$")
    ax2.legend(fontsize=7.5, loc="center left")
    _titulo(ax2, r"(b) $|T_n-x_n|^{1/n}\to|\lambda_{\max}|$")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figura 3: serie infinita y areas descartadas
# ---------------------------------------------------------------------------

def fig_serie(d: dict) -> Figure:
    """
    @brief Serie S_N -> 1/2 y areas descartadas D_n cuya suma tiende a 1.
    @param d Diccionario de :func:`backend.sucesiones.tabla`.
    @return Objeto Figure con dos paneles.
    """
    n = np.array(d["n"])
    S = np.array(d["S"])
    SD = np.array(d["SD"])
    D = np.array(d["D"])

    fig = plt.figure(figsize=(9.2, 4.4), dpi=110)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    ax1.plot(n, S, "o-", color=C_Q, ms=3, lw=1.5, label=r"$S_N=\sum_{n=1}^{N}T_n$")
    ax1.axhline(0.5, color=C_T, ls="--", lw=1.4, label=r"límite $S=1/2$")
    ax1.set_ylim(0, 0.6)
    ax1.set_xlabel("$N$")
    ax1.set_ylabel("suma parcial")
    ax1.legend(fontsize=8, loc="lower right")
    _titulo(ax1, "(a) $S_N\\to 1/2$: la mitad del área original")

    ax2.bar(n[1:], D[1:], color=C_P, alpha=0.85,
            label=r"$D_n=2\,T_n$ por paso")
    ax2.plot(n, SD, "o-", color=C_T, ms=3, lw=1.5,
             label=r"acumulada $\sum_{k\leq n}D_k \to 1$")
    ax2.set_xlabel("$n$")
    ax2.set_ylabel("área")
    ax2.set_ylim(0, 1.15)
    ax2.legend(fontsize=8, loc="center right")
    _titulo(ax2, "(b) Áreas descartadas: total $=T_0=1$")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figura 4: la subdivision geometrica
# ---------------------------------------------------------------------------

def _hijos(v1, v2, v3):
    """
    @brief Divide el triangulo (v1, v2, v3) por el baricentro en 3 triangulos.
    @param v1 Primer vertice (array 2D de numpy).
    @param v2 Segundo vertice.
    @param v3 Tercer vertice.
    @return Tupla (lista de los 3 triangulos hijos, baricentro G).
    """
    G = (v1 + v2 + v3) / 3.0
    return [(v1, v2, G), (v2, v3, G), (v3, v1, G)], G


def fig_triangulos(niveles: int = 3) -> Figure:
    """
    @brief Dibuja la cadena de triangulos T_0 > T_1 > ... y las zonas descartadas.
    @param niveles Numero de niveles de subdivision a dibujar (por defecto 3).
    @return Objeto Figure con dos paneles.
    """
    sq3 = math.sqrt(3) / 2
    v1 = np.array([0.0, 0.0])
    v2 = np.array([1.0, 0.0])
    v3 = np.array([0.5, sq3])

    fig = plt.figure(figsize=(9.2, 4.3), dpi=110)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    def poly(ax, tri, **kw):
        pts = np.vstack([tri[0], tri[1], tri[2]])
        ax.fill(pts[:, 0], pts[:, 1], **kw)

    # (a) cadena T0, T1, T2, T3
    tri = (v1, v2, v3)
    poly(ax1, tri, facecolor="#eef3fa", edgecolor=C_T, lw=1.4, zorder=1)
    ax1.text(0.5, 0.72 * sq3, r"$T_0=1$", ha="center", fontsize=10)
    colores = ["#bcd4ec", "#8fb7de", "#5f93cb"]
    seleccion = [0, 1, 2]          # giro para que la cadena se vea escalonada
    centros = [(0.5, sq3 / 3)]
    for k in range(niveles):
        hijos, G = _hijos(*tri)
        tri = hijos[seleccion[k % len(seleccion)]]
        poly(ax1, tri, facecolor=colores[k % len(colores)],
             edgecolor=C_T, lw=1.2, zorder=2 + k)
        cx = float(np.mean([p[0] for p in tri]))
        cy = float(np.mean([p[1] for p in tri]))
        centros.append((cx, cy))
        ax1.text(cx, cy, rf"$T_{{{k+1}}}$", ha="center", va="center",
                 fontsize=9, zorder=20,
                 bbox=dict(boxstyle="round,pad=0.18", fc="white",
                           ec=colores[k % len(colores)], alpha=0.92))
    ax1.plot(*zip(*centros), color=C_T, lw=0.9, ls="--", zorder=15)
    ax1.set_aspect("equal")
    ax1.set_xlim(-0.06, 1.06)
    ax1.set_ylim(-0.06, sq3 + 0.06)
    ax1.axis("off")
    _titulo(ax1, "(a) Cadena de triángulos: $T_{n+1}=T_n/3$")

    # (b) una particion: 1 se conserva, 2 se descartan
    hijos, G = _hijos(v1, v2, v3)
    poly(ax2, hijos[0], facecolor="#9dc0e4", edgecolor=C_T, lw=1.2,
         label=r"se conserva: $T_1=1/3$")
    poly(ax2, hijos[1], facecolor="#f6c9a8", edgecolor=C_T, lw=1.2,
         label=r"se descarta: $2/3$")
    poly(ax2, hijos[2], facecolor="#f6c9a8", edgecolor=C_T, lw=1.2)
    ax2.plot([G[0], G[0]], [G[1], v3[1]], color=C_T, lw=1.0, ls=":")
    ax2.set_aspect("equal")
    ax2.set_xlim(-0.06, 1.06)
    ax2.set_ylim(-0.06, sq3 + 0.06)
    ax2.axis("off")
    ax2.legend(fontsize=8, loc="lower center", framealpha=0.95)
    _titulo(ax2, "(b) Cada paso: 1 parte se queda, 2 se descartan")

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figura 5: autovalores de B en el plano complejo
# ---------------------------------------------------------------------------

def fig_autovalores(info: dict, titulo: str = "") -> Figure:
    """
    @brief Autovalores de B en el plano complejo, con el circulo unitario y rho.
    @param info Diccionario de :func:`backend.sucesiones.analisis_B`.
    @param titulo Titulo opcional del panel.
    @return Objeto Figure.
    """
    auto = info["autovalores"]
    rho = info["radio_espectral"]

    fig = plt.figure(figsize=(4.6, 4.2), dpi=110)
    ax = fig.add_subplot(1, 1, 1)

    theta = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(theta), np.sin(theta), color="gray", lw=1.0, ls="--",
            label=r"círculo unitario $|\lambda|=1$")
    ax.plot(np.cos(theta) * rho, np.sin(theta) * rho, color=C_Q, lw=1.0,
            ls=":", label=rf"$|\lambda|=\rho(B)={rho:.3f}$")
    ax.scatter(auto.real, auto.imag, s=70, color=C_P, zorder=5,
               edgecolor=C_T, linewidth=0.8, label=r"autovalores $\lambda_i$")
    for lam in auto:
        ax.annotate(f"{lam:.3g}", (lam.real, lam.imag),
                    textcoords="offset points", xytext=(7, 6), fontsize=8)
    lim = max(rho, 1.0) * 1.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.axhline(0, color="black", lw=0.6)
    ax.axvline(0, color="black", lw=0.6)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$\mathrm{Re}(\lambda)$")
    ax.set_ylabel(r"$\mathrm{Im}(\lambda)$")
    ax.legend(fontsize=7.5, loc="upper left")
    _titulo(ax, titulo or r"Autovalores de $B$ y radio espectral")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Exportacion rapida de todas las figuras
# ---------------------------------------------------------------------------

def guardar_todas(d: dict, info_B: dict, carpeta: str, sufijo: str = "") -> list[str]:
    """
    @brief Genera las 7 figuras como PNG y devuelve las rutas.
    @param d Diccionario de :func:`backend.sucesiones.tabla`.
    @param info_B Diccionario de :func:`backend.sucesiones.analisis_B`.
    @param carpeta Directorio de salida (se crea si no existe).
    @param sufijo Texto opcional para distinguir variantes (p. ej. "_variante").
    @return Lista de rutas de los archivos PNG generados.
    """
    import os
    os.makedirs(carpeta, exist_ok=True)
    rutas = []
    pares = [
        (fig_sucesiones(d), f"01_sucesiones{sufijo}.png"),
        (fig_sucesiones_detalle(d), f"02_sucesiones_detalle{sufijo}.png"),
        (fig_diferencias(d, False), f"03_diferencias_abs{sufijo}.png"),
        (fig_diferencias(d, True), f"04_diferencias_rel{sufijo}.png"),
        (fig_serie(d), f"05_serie_y_descartes{sufijo}.png"),
        (fig_triangulos(), f"06_subdivision_geometrica{sufijo}.png"),
        (fig_autovalores(info_B), f"07_autovalores{sufijo}.png"),
    ]
    for fig, nombre in pares:
        ruta = os.path.join(carpeta, nombre)
        fig.savefig(ruta, dpi=140, bbox_inches="tight", facecolor="white")
        rutas.append(ruta)
        plt.close(fig)  # liberar la figura de pyplot (evita acumular estado)
    return rutas
