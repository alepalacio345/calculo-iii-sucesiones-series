"""
@file web_app.py
@brief Servidor web del proyecto "Sucesiones y Series" (FastAPI + HTML/CSS).
@details
Este archivo es el puente entre los calculos y la pagina: recibe la peticion del
navegador, llama al backend matematico, genera las figuras y devuelve el HTML ya
relleno. La parte visual vive en templates/index.html y static/style.css.

El recorrido de una peticion es siempre el mismo:
1) se leen N, modelo y seccion de la URL;
2) se calculan los datos con backend/sucesiones.py;
3) se generan las figuras necesarias y se convierten a PNG en base64;
4) se renderiza la plantilla con esos datos.

@par Ejecutar (desde la raiz del proyecto)
    .venv\\Scripts\\python.exe -m uvicorn web.web_app:app --port 8000

Luego abrir http://127.0.0.1:8000 en el navegador. Toda la interactividad usa
formularios HTML normales (recarga de pagina): no hay ni una linea de
JavaScript. Las graficas de matplotlib se convierten a PNG en memoria y se
incrustan como <img src="data:image/png;base64,...">.
"""

from __future__ import annotations

import base64
import io
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")  # backend sin ventana (servidor web)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# backend del proyecto (matematica + figuras), sin cambios
BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, RAIZ)

from backend import graficas as gr  # noqa: E402
from backend import sucesiones as su  # noqa: E402

app = FastAPI(title="Sucesiones y Series — Cálculo III")
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE, "templates"))

SECCIONES = [
    ("resumen", "Resumen"),
    ("sucesiones", "Sucesiones"),
    ("diferencias", "Diferencias"),
    ("serie", "Serie y áreas"),
    ("matriz", "Matriz y espectro"),
    ("informe", "Informe"),
]


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------

def fmt(v, dec: int = 4) -> str:
    """
    @brief Convierte un numero en un texto corto y legible para las tablas.
    @details
    Se adapta al tipo de valor: los numeros muy grandes o muy pequenos se
    muestran en notacion cientifica, los complejos se escriben como a + bi y los
    None se muestran como un guion. Asi las tablas de la pagina quedan ordenadas
    y son faciles de leer sin escribir formato en cada celda.
    @param v Valor a formatear (float, complex o None).
    @param dec Numero de decimales (por defecto 4).
    @return Cadena formateada.
    """
    if v is None:
        return "—"
    if isinstance(v, complex):
        if abs(v.imag) < 1e-12:
            return fmt(v.real, dec)
        return f"{v.real:.{dec}f}{'+' if v.imag >= 0 else '-'}{abs(v.imag):.{dec}f}i"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if not math.isfinite(v):
        return "∞" if v > 0 else "-∞"
    if v == 0:
        return "0"
    a = abs(v)
    if a >= 1e5 or a < 1e-3:
        return f"{v:.{dec}e}"
    return f"{v:.{max(dec, 1)}f}"


def fig64(fig) -> str:
    """
    @brief Convierte una figura de matplotlib en una imagen PNG codificada en base64.
    @details
    Guarda la figura en un buffer de memoria (no en disco), lee los bytes del PNG
    y los pasa a base64. Ese texto se pega directamente en el HTML como
    <img src="data:image/png;base64,...">, de modo que la pagina muestra la
    grafica sin necesitar archivos ni JavaScript. Despues cierra la figura para
    liberar memoria.
    @param fig Objeto Figure de matplotlib.
    @return Cadena base64 del PNG (sin el prefijo data:).
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor="white")
    import matplotlib.pyplot as plt
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------------------
# rutas
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    @brief Ruta principal: calcula todo y entrega la pagina web.
    @details
    Es la unica ruta de la aplicacion. Lee de la URL tres parametros opcionales:
    N (numero de iteraciones, por defecto 30), modelo ("impreso" o "corregido")
    y seccion (que pestana mostrar). Si algun valor llega mal, lo reemplaza por
    uno valido. Luego calcula los datos con el backend, prepara las figuras y las
    tablas de la seccion pedida y renderiza la plantilla.
    @param request Peticion HTTP (FastAPI).
    @return Respuesta HTML con la plantilla ya rellena.
    """
    N = int(request.query_params.get("N", 30))
    modelo = request.query_params.get("modelo", "impreso")
    seccion = request.query_params.get("seccion", "resumen")
    if seccion not in dict(SECCIONES):
        seccion = "resumen"
    if modelo not in ("impreso", "corregido"):
        modelo = "impreso"
    impreso = modelo == "impreso"

    d = su.tabla(N, impreso)
    info = su.analisis_B(impreso)
    n0 = min(30, N)

    ctx = {
        "seccion": seccion,
        "secciones": SECCIONES,
        "N": N,
        "modelo": modelo,
        "impreso": impreso,
        "fmt": fmt,
    }

    # ---- resumen ----
    if seccion == "resumen":
        ctx.update(
            T1=fmt(d["T"][1]), T5=fmt(d["T"][min(5, N)]),
            Tn=fmt(d["T"][n0]), n0=n0,
            fig_triangulos=fig64(gr.fig_triangulos()),
        )

    # ---- sucesiones ----
    elif seccion == "sucesiones":
        filas = [
            [n, fmt(d["T"][n]), fmt(d["r"][n]), fmt(d["p"][n]), fmt(d["q"][n])]
            for n in range(N + 1)
        ]
        ctx.update(
            fig_sucesiones=fig64(gr.fig_sucesiones(d)),
            fig_detalle=fig64(gr.fig_sucesiones_detalle(d)),
            cab_sucesiones=["n", "Tₙ", "rₙ", "pₙ", "qₙ"],
            filas_sucesiones=filas,
        )

    # ---- diferencias ----
    elif seccion == "diferencias":
        filas = [
            [n, fmt(d["err_r"][n]), fmt(d["err_p"][n]), fmt(d["err_q"][n]),
             fmt(d["rel_p"][n]), fmt(d["rel_q"][n])]
            for n in range(N + 1)
        ]
        ctx.update(
            n0r="no diverge", n0p=str(d["n0_min_p"]), n0q=str(d["n0_min_q"]),
            n100p=str(d["n100_p"]), n100q=str(d["n100_q"]),
            fig_dif_abs=fig64(gr.fig_diferencias(d, relativa=False)),
            fig_dif_rel=fig64(gr.fig_diferencias(d, relativa=True)),
            cab_dif=["n", "|Tₙ−rₙ|", "|Tₙ−pₙ|", "|Tₙ−qₙ|", "rel. pₙ", "rel. qₙ"],
            filas_dif=filas,
        )

    # ---- serie ----
    elif seccion == "serie":
        filas = [
            [k, fmt(d["T"][k]), fmt(d["D"][k]), fmt(d["SD"][k])]
            for k in range(1, N + 1)
        ]
        ctx.update(
            S_N=fmt(d["S"][N]), SD_N=fmt(d["SD"][N]),
            fig_serie=fig64(gr.fig_serie(d)),
            cab_serie=["n", "Tₙ", "Dₙ = 2·Tₙ", "Σ Dₖ"],
            filas_serie=filas,
        )

    # ---- matriz ----
    elif seccion == "matriz":
        B = info["B"]
        filas_B = [[fmt(B[i, j], 6) for j in range(3)] for i in range(3)]
        autos = [[fmt(z, 6), fmt(abs(z), 6)] for z in info["autovalores"]]
        ctx.update(
            filas_B=filas_B,
            autos=autos,
            rho=fmt(info["radio_espectral"], 6),
            traza=fmt(info["traza"], 6),
            det=fmt(info["determinante"], 6),
            polinomio=su.espectro_q(impreso).latex_pol(),
            coincide=info["coincide"],
            fig_autovalores=fig64(gr.fig_autovalores(info)),
        )

    # ---- informe ----
    elif seccion == "informe":
        ctx.update(informe_html=_informe_html(impreso, info))

    return templates.TemplateResponse(request, "index.html", ctx)


def _informe_html(impreso: bool, info: dict) -> str:
    """
    @brief Arma el texto del informe (analisis) en HTML.
    @details
    Genera un borrador del analisis que se muestra en la pestana "Informe": un
    resumen del polinomio caracteristico, las raices, el radio espectral y la
    conclusion sobre la convergencia. Se construye como HTML sencillo (sin LaTeX)
    para que se lea directamente en el navegador.
    @param impreso True para la version impresa de (iii); False la corregida.
    @param info Diccionario de :func:`backend.sucesiones.analisis_B`.
    @return Cadena HTML con el texto del informe.
    """
    rho = info["radio_espectral"]
    et = "impresa (−27, +18)" if impreso else "corregida (−21, +6)"
    return f"""
<h3>1. Término general</h3>
<p>En cada paso el área se divide entre 3 y se conserva una parte, así que la
sucesión es geométrica de razón 1/3: <code>Tₙ = 3⁻ⁿ</code>, con <code>T₀ = 1</code>.
Es decreciente y converge a 0.</p>

<h3>2. Análisis numérico de los tres algoritmos</h3>
<p>Las tres recurrencias deberían reproducir <code>Tₙ</code> en aritmética exacta. La
diferencia está en las raíces de su polinomio característico:</p>
<table class="tabla">
  <thead><tr><th>Algoritmo</th><th>Polinomio característico</th><th>Raíces</th><th>ρ</th></tr></thead>
  <tbody>
    <tr><td>(i) rₙ</td><td>λ − 1/3</td><td>1/3</td><td>0.333</td></tr>
    <tr><td>(ii) pₙ</td><td>λ² − (10/3)λ + 1</td><td>3 ; 1/3</td><td><strong>3</strong></td></tr>
    <tr><td>(iii) qₙ <em>({et})</em></td><td>ver pestaña «Matriz y espectro»</td><td>—</td><td><strong>{rho:.3f}</strong></td></tr>
  </tbody>
</table>

<h4>Por qué fallan</h4>
<p><strong>(i)</strong> Solo tiene el modo bueno λ = 1/3: <code>rₙ = 0.99997·3⁻ⁿ</code> y
<code>|Tₙ − rₙ| = 3·10⁻⁵·3⁻ⁿ</code>. El error absoluto <strong>decrece</strong>; el relativo
es constante (3·10⁻⁵).</p>
<p><strong>(ii)</strong> Aparece una raíz parásita λ = 3. La solución es
<code>pₙ = A·3ⁿ + B·3⁻ⁿ</code> con <code>A = 2.5·10⁻⁶</code> (inyectado por
<code>p₁ = 0.33334 ≠ 1/3</code>). El modo 3ⁿ domina cuando
<code>2.5·10⁻⁶·3ⁿ ≈ 3⁻ⁿ</code>, es decir en <code>n ≈ 5.87</code>; por eso la divergencia se
observa en <strong>n₀ ≈ 6</strong>.</p>
<p><strong>(iii)</strong> El polinomio impreso λ³ − (28/3)λ² + 27λ − 18 <strong>no tiene a 1/3
como raíz</strong> (<code>P(1/3) = −10</code>): la recurrencia da <code>q₃ = 10.037</code> frente a
<code>T₃ = 0.037</code>. Con los coeficientes corregidos (−21 y +6) las raíces son 1/3, 3 y 6,
con el modo parásito creciendo como 6ⁿ.</p>

<h3>3. Serie infinita</h3>
<p><code>S = Σ (n≥1) 3⁻ⁿ = (1/3)/(1 − 1/3) = 1/2</code>. La suma de las áreas de <strong>todos</strong>
los triángulos conservados es media unidad: la mitad del triángulo original.</p>

<h3>4. Áreas descartadas</h3>
<p><code>Dₙ = 2·Tₙ = 2·3⁻ⁿ</code>, <code>ΣDₖ (k≤N) = 1 − 3⁻ᴺ</code>, <code>Σ (n≥1) Dₙ = 1 = T₀</code>.
En el paso N se ha descartado <code>1 − 3⁻ᴺ</code> y queda <code>T_N = 3⁻ᴺ</code>; la suma es 1 para
todo N, así que lo descartado agota el área original.</p>

<h3>5. Enfoque matricial</h3>
<p>Con <code>Xₙ = [qₙ, qₙ₋₁, qₙ₋₂]ᵀ</code> y la matriz compañera B, <code>det(B − λI)</code>
reproduce exactamente el polinomio característico de la recurrencia. Numéricamente
<code>ρ(B) = {rho:.6f} &gt; 1</code>, y como <code>‖Xₙ‖ ~ ρ(B)ⁿ</code>, cualquier error de
redondeo se multiplica por ρ en cada iteración.</p>

<h3>6. Conclusión</h3>
<p>La sucesión <code>Tₙ</code> converge a 0 y la serie converge a 1/2, pero <strong>el algoritmo
importa</strong>: la misma relación algebraica, reescrita como recurrencia de orden superior,
introduce raíces espurias de módulo mayor que 1 que destruyen la convergencia numérica. La
estabilidad queda caracterizada por el radio espectral de la matriz compañera.</p>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
