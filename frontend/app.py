"""
Interfaz de usuario (frontend) de la aplicacion, construida con Flet 1.x.

Contiene la clase :class:`App` (estado + construccion de cada seccion) y la
funcion :func:`main` que Flet usa como punto de entrada de la interfaz.

La logica matematica y las figuras estan separadas en `backend/`:

    backend/sucesiones.py   calculos: sucesiones, raices, series, matriz B
    backend/graficas.py     figuras de matplotlib (sin dependencias de UI)
    app.py                  punto de entrada (arranca la interfaz)

Ejecutar desde la raiz del proyecto:

    flet run app.py            (ventana nativa)
    flet run --web app.py      (navegador)
"""

from __future__ import annotations

import math

import flet as ft
import flet_charts as fch
import numpy as np

from backend import graficas as gr
from backend import sucesiones as su

# ---------------------------------------------------------------------------
# utilidades de formato
# ---------------------------------------------------------------------------

def fmt(v, dec: int = 4) -> str:
    """Numero legible: notacion cientifica solo cuando hace falta."""
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


# ---------------------------------------------------------------------------
# piezas de interfaz reutilizables
# ---------------------------------------------------------------------------

def tarjeta(contenido: ft.Control, padding: int = 16, **kw) -> ft.Container:
    """Envuelve un control en una tarjeta Material con esquinas redondeadas."""
    return ft.Container(
        content=contenido,
        padding=padding,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        **kw,
    )


def titulo(texto: str, size: int = 18, sub: str | None = None) -> ft.Control:
    """Cabecera de seccion: titulo en negrita y subtitulo opcional."""
    return ft.Column(
        spacing=2,
        controls=[
            ft.Text(texto, size=size, weight=ft.FontWeight.BOLD),
            *([ft.Text(sub, size=12, opacity=0.7)] if sub else []),
        ],
    )


def tabla(columnas: list[str], filas: list[list[str]], alto: int = 300,
          numeric_from: int = 1) -> ft.Control:
    """Tabla con scroll horizontal y vertical."""
    dt = ft.DataTable(
        columns=[
            ft.DataColumn(
                label=ft.Text(c, size=11, weight=ft.FontWeight.BOLD),
                numeric=i >= numeric_from,
            )
            for i, c in enumerate(columnas)
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(c), size=11)) for c in f])
            for f in filas
        ],
        column_spacing=16,
    )
    return ft.Container(
        height=alto,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[ft.Row([dt], scroll=ft.ScrollMode.AUTO)],
        ),
    )


def chart(fig, alto: int | None = None) -> ft.Control:
    """Envuelve una Figure de matplotlib en un control de Flet."""
    return ft.Container(
        content=fch.MatplotlibChart(figure=fig, expand=True),
        expand=True,
        height=alto,
    )


def metrica(etiqueta: str, valor: str, color: str | None = None) -> ft.Control:
    """Tarjeta pequena con una etiqueta y un valor destacado (KPI)."""
    return tarjeta(
        ft.Column(
            spacing=1,
            controls=[
                ft.Text(etiqueta, size=11, opacity=0.7),
                ft.Text(valor, size=17, weight=ft.FontWeight.BOLD,
                        color=color or ft.Colors.ON_SURFACE),
            ],
        ),
        padding=12,
    )


# ---------------------------------------------------------------------------
# la aplicacion
# ---------------------------------------------------------------------------

class App:
    """Estado y construccion de la interfaz Flet.

    Responsabilidades
        * guardar los parametros de la sesion (``N``, ``modelo``, seccion);
        * construir el menu lateral, la barra superior y el area de contenido;
        * reaccionar a los eventos (cambio de ``N`` o de modelo) reconstruyendo
          la seccion activa a partir de los datos del backend.

    La clase no contiene logica matematica: delega en
    :mod:`backend.sucesiones` (datos) y :mod:`backend.graficas` (figuras).
    """

    SECCIONES = [
        ("resumen", "Resumen", ft.Icons.HOME_OUTLINED),
        ("sucesiones", "Sucesiones", ft.Icons.SHOW_CHART),
        ("diferencias", "Diferencias", ft.Icons.COMPARE_ARROWS),
        ("serie", "Serie y áreas", ft.Icons.FUNCTIONS),
        ("matriz", "Matriz y espectro", ft.Icons.GRID_ON),
        ("informe", "Informe", ft.Icons.ARTICLE_OUTLINED),
    ]

    def __init__(self, page: ft.Page):
        self.page = page
        self.N = 30
        self.modelo = "impreso"      # "impreso" | "corregido"
        self.relativa = False
        self.seccion = "resumen"

        self.contenido = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=14)
        self.menu = ft.Column(spacing=4, width=196)
        self.lbl_n = ft.Text("30", weight=ft.FontWeight.BOLD)

        self._construir_menu()
        self._montar()
        self.refrescar()

    # -- estructura ---------------------------------------------------------
    def _construir_menu(self) -> None:
        self.menu.controls.clear()
        for clave, texto, icono in self.SECCIONES:
            activo = clave == self.seccion
            self.menu.controls.append(
                ft.Button(
                    content=ft.Text(texto, size=13),
                    icon=icono,
                    width=196,
                    on_click=lambda e, c=clave: self.ir(c),
                    bgcolor=ft.Colors.PRIMARY_CONTAINER if activo else None,
                    color=ft.Colors.ON_PRIMARY_CONTAINER if activo else None,
                )
            )

    def _barra_superior(self) -> ft.Control:
        self.dd_modelo = ft.Dropdown(
            value="impreso",
            width=250,
            label="Recurrencia (iii)",
            options=[
                ft.DropdownOption(key="impreso", text="Tal como está impresa (-27, +18)"),
                ft.DropdownOption(key="corregido", text="Corregida (-21, +6)"),
            ],
            on_select=self._cambiar_modelo,
        )
        self.slider_n = ft.Slider(
            min=5, max=60, divisions=55, value=self.N, width=220,
            label="{value}", on_change=self._cambiar_n,
        )
        return tarjeta(
            ft.Row(
                wrap=True,
                spacing=20,
                run_spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=1,
                        controls=[
                            ft.Text("Áreas de los triángulos", size=17,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("Proyecto de Cálculo III — sucesiones y series",
                                    size=11, opacity=0.7),
                        ],
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("n máx.", size=12),
                            self.slider_n,
                        ],
                    ),
                    self.dd_modelo,
                ],
            ),
            padding=14,
        )

    def _montar(self) -> None:
        self.page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    spacing=12,
                    controls=[
                        self._barra_superior(),
                        ft.Row(
                            expand=True,
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                tarjeta(self.menu, padding=10, width=216),
                                ft.Column(expand=True, controls=[self.contenido]),
                            ],
                        ),
                    ],
                ),
            )
        )

    # -- eventos ------------------------------------------------------------
    def ir(self, clave: str) -> None:
        self.seccion = clave
        self._construir_menu()
        self.refrescar()

    def _cambiar_n(self, e) -> None:
        self.N = int(e.control.value)
        self.lbl_n.value = str(self.N)
        self.refrescar()

    def _cambiar_modelo(self, e) -> None:
        self.modelo = getattr(e.control, "value", None) or "impreso"
        self.refrescar()

    # -- datos --------------------------------------------------------------
    def _datos(self) -> tuple[dict, dict]:
        impreso = self.modelo == "impreso"
        return su.tabla(self.N, impreso), su.analisis_B(impreso)

    def refrescar(self) -> None:
        d, info = self._datos()
        constructor = {
            "resumen": self._sec_resumen,
            "sucesiones": self._sec_sucesiones,
            "diferencias": self._sec_diferencias,
            "serie": self._sec_serie,
            "matriz": self._sec_matriz,
            "informe": self._sec_informe,
        }[self.seccion]
        self.contenido.controls = constructor(d, info)
        self.page.update()

    # -- secciones ----------------------------------------------------------
    def _sec_resumen(self, d, info) -> list[ft.Control]:
        n0 = 30
        return [
            titulo("El problema", sub="Triángulo equilátero de área T₀ = 1, "
                                      "subdividido indefinidamente"),
            tarjeta(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Markdown(
                            "En cada paso se une el baricentro con los tres vértices: el "
                            "triángulo queda partido en **tres triángulos congruentes de "
                            "área igual a un tercio** del anterior. Se conserva uno y se "
                            "repite el proceso.",
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        ),
                        ft.Text("Término general:   Tₙ = 3⁻ⁿ ,  T₀ = 1",
                                size=15, weight=ft.FontWeight.BOLD),
                    ],
                )
            ),
            ft.Row(
                wrap=True,
                spacing=12,
                controls=[
                    metrica("T₁", fmt(d["T"][1])),
                    metrica("T₅", fmt(d["T"][5])),
                    metrica(f"T_{n0}", fmt(d["T"][n0])),
                    metrica("Σ Tₙ  (n≥1)", "1/2  = 0.5", ft.Colors.PRIMARY),
                    metrica("Σ Dₙ  (n≥1)", "1  = T₀", ft.Colors.TERTIARY),
                ],
            ),
            tarjeta(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Qué hace esta aplicación", size=14,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "· Compara la sucesión exacta Tₙ con las tres recurrencias "
                            "propuestas (rₙ, pₙ, qₙ).\n"
                            "· Tabula valores, errores absolutos y relativos.\n"
                            "· Calcula la serie S = Σ Tₙ y las áreas descartadas Dₙ.\n"
                            "· Expone la matriz compañera B, su polinomio característico, "
                            "autovalores y radio espectral.",
                            size=12,
                        ),
                    ],
                )
            ),
            chart(gr.fig_triangulos(), alto=360),
        ]

    def _sec_sucesiones(self, d, info) -> list[ft.Control]:
        filas = [
            [str(n), fmt(d["T"][n]), fmt(d["r"][n]), fmt(d["p"][n]), fmt(d["q"][n])]
            for n in range(len(d["n"]))
        ]
        return [
            titulo("Comparación de las cuatro sucesiones",
                   sub="Tₙ exacta frente a los tres algoritmos recursivos"),
            chart(gr.fig_sucesiones(d, self.modelo)),
            chart(gr.fig_sucesiones_detalle(d, self.modelo)),
            tarjeta(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Tabla comparativa", size=14,
                                weight=ft.FontWeight.BOLD),
                        tabla(["n", "Tₙ", "rₙ", "pₙ", "qₙ"], filas, alto=340),
                    ],
                )
            ),
        ]

    def _sec_diferencias(self, d, info) -> list[ft.Control]:
        filas = [
            [str(n), fmt(d["err_r"][n]), fmt(d["err_p"][n]), fmt(d["err_q"][n]),
             fmt(d["rel_p"][n]), fmt(d["rel_q"][n])]
            for n in range(len(d["n"]))
        ]
        return [
            titulo("Diferencias respecto de Tₙ",
                   sub="$|T_n - x_n|$: quién tiende a cero y quién no"),
            ft.Row(
                wrap=True,
                spacing=12,
                controls=[
                    metrica("n₀ de rₙ", "no diverge", ft.Colors.PRIMARY),
                    metrica("n₀ de pₙ", str(d["n0_min_p"])),
                    metrica("n₀ de qₙ", str(d["n0_min_q"])),
                    metrica("|T−p| > T desde n", str(d["n100_p"])),
                    metrica("|T−q| > T desde n", str(d["n100_q"])),
                ],
            ),
            chart(gr.fig_diferencias(d, relativa=False)),
            chart(gr.fig_diferencias(d, relativa=True)),
            tarjeta(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Tabla de errores", size=14,
                                weight=ft.FontWeight.BOLD),
                        tabla(["n", "|Tₙ−rₙ|", "|Tₙ−pₙ|", "|Tₙ−qₙ|",
                               "rel. pₙ", "rel. qₙ"], filas, alto=300),
                    ],
                )
            ),
        ]

    def _sec_serie(self, d, info) -> list[ft.Control]:
        n = self.N
        filas = [
            [str(k), fmt(d["T"][k]), fmt(d["D"][k]), fmt(d["SD"][k])]
            for k in range(1, len(d["n"]))
        ]
        return [
            titulo("Serie infinita y áreas descartadas",
                   sub="S = Σ Tₙ y Dₙ = 2·Tₙ"),
            ft.Row(
                wrap=True,
                spacing=12,
                controls=[
                    metrica("Σ Tₙ (n≥1)", "1/2", ft.Colors.PRIMARY),
                    metrica(f"S_{n}", fmt(d["S"][n])),
                    metrica(f"Σ Dₖ (k≤{n})", fmt(d["SD"][n])),
                    metrica("Σ Dₙ (n≥1)", "1 = T₀", ft.Colors.TERTIARY),
                ],
            ),
            chart(gr.fig_serie(d)),
            tarjeta(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Áreas por paso y suma acumulada", size=14,
                                weight=ft.FontWeight.BOLD),
                        tabla(["n", "Tₙ", "Dₙ = 2·Tₙ", "Σ Dₖ"], filas, alto=300),
                    ],
                )
            ),
        ]

    def _sec_matriz(self, d, info) -> list[ft.Control]:
        B = info["B"]
        filas_B = [[f"fila {i+1}"] + [fmt(B[i, j], 6) for j in range(3)]
                   for i in range(3)]
        autos = [[fmt(z, 6), fmt(abs(z), 6)] for z in info["autovalores"]]
        return [
            titulo("Enfoque matricial y análisis espectral",
                   sub="Xₙ = B·Xₙ₋₁ con Xₙ = [qₙ, qₙ₋₁, qₙ₋₂]ᵀ"),
            ft.Row(
                wrap=True,
                spacing=12,
                controls=[
                    metrica("P(λ)", su.espectro_q(self.modelo == "impreso").latex_pol()),
                    metrica("ρ(B)", fmt(info["radio_espectral"], 6),
                            ft.Colors.ERROR if info["radio_espectral"] > 1
                            else ft.Colors.PRIMARY),
                    metrica("tr(B)", fmt(info["traza"], 6)),
                    metrica("det(B)", fmt(info["determinante"], 6)),
                ],
            ),
            ft.Row(
                wrap=True,
                spacing=12,
                controls=[
                    tarjeta(
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Matriz compañera B", size=13,
                                        weight=ft.FontWeight.BOLD),
                                tabla(["", "col 1", "col 2", "col 3"], filas_B,
                                      alto=170, numeric_from=1),
                            ],
                        )
                    ),
                    tarjeta(
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Autovalores y módulos", size=13,
                                        weight=ft.FontWeight.BOLD),
                                tabla(["λ", "|λ|"], autos, alto=170, numeric_from=0),
                            ],
                        )
                    ),
                    chart(gr.fig_autovalores(info), alto=300),
                ],
            ),
            tarjeta(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "det(B − λI) = " + info["polinomio_B"].round(6).__repr__()
                            + "   ·   coincide con el polinomio de la recurrencia: "
                            + ("sí" if info["coincide"] else "no"),
                            size=12,
                        ),
                        ft.Text(
                            "ρ(B) > 1 implica que el modo dominante crece como ρⁿ: "
                            "el error de redondeo se amplifica en cada paso. Esa es la "
                            "justificación numérica de la divergencia observada.",
                            size=12,
                        ),
                    ],
                )
            ),
        ]

    def _sec_informe(self, d, info) -> list[ft.Control]:
        return [
            titulo("Informe", sub="Borrador del análisis para el documento final"),
            tarjeta(
                ft.Markdown(
                    self._texto_informe(d, info),
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    selectable=True,
                )
            ),
        ]

    def _texto_informe(self, d, info) -> str:
        """Borrador del análisis, en texto plano/Unicode (el Markdown de Flet no
        procesa LaTeX). La versión con LaTeX para el PDF está en INVESTIGACION.md."""
        rho = info["radio_espectral"]
        etiqueta = "impresa" if self.modelo == "impreso" else "corregida (−21, +6)"
        return f"""
## 1. Término general

Cada paso divide el área entre 3 y se conserva una parte, así que la sucesión es
geométrica de razón 1/3:

```
Tₙ = 3⁻ⁿ = 1/3ⁿ          T₀ = 1 ,  T₁ = 1/3 ,  T₂ = 1/9 ,  T₃ = 1/27 , …
```

Es decreciente y converge a 0.

## 2. Análisis numérico de los tres algoritmos

Las tres recurrencias deberían reproducir `Tₙ` en aritmética exacta. La diferencia
está en las raíces de su polinomio característico:

| Algoritmo | Polinomio característico | Raíces | ρ |
|---|---|---|---|
| (i) rₙ | λ − 1/3 | 1/3 | 0.333 |
| (ii) pₙ | λ² − (10/3)λ + 1 | 3 ; 1/3 | **3** |
| (iii) qₙ ({etiqueta}) | ver pestaña «Matriz y espectro» | — | **{rho:.3f}** |

### Por qué fallan

**(i)** Solo tiene el modo bueno λ = 1/3:

```
rₙ = 0.99997 · 3⁻ⁿ        |Tₙ − rₙ| = 3·10⁻⁵ · 3⁻ⁿ
```

El error absoluto **decrece**; el relativo es constante e igual a 3·10⁻⁵.

**(ii)** Aparece una raíz parásita λ = 3. La solución general es
`pₙ = A·3ⁿ + B·3⁻ⁿ`. El valor `p₁ = 0.33334` (que se aparta de 1/3 en 6.7·10⁻⁶)
inyecta `A = 2.5·10⁻⁶`, de modo que

```
pₙ = 2.5·10⁻⁶ · 3ⁿ + 0.9999975 · 3⁻ⁿ
```

El modo 3ⁿ domina cuando `2.5·10⁻⁶·3ⁿ ≈ 3⁻ⁿ`, es decir en `n ≈ 5.87`. Por eso la
divergencia se observa en **n₀ ≈ 6**, y el error crece como 9ⁿ.

**(iii)** El polinomio impreso, λ³ − (28/3)λ² + 27λ − 18, **no tiene a 1/3 como
raíz**: `P(1/3) = −10`. La propia recurrencia da `q₃ = 10.037` frente a
`T₃ = 0.037`, así que no reproduce la sucesión. Con los coeficientes corregidos
(−21 y +6) las raíces son 1/3, 3 y 6: el mismo patrón que (ii) pero con el modo
parásito creciendo como 6ⁿ en vez de 3ⁿ.

## 3. Serie infinita

```
S = Σ (n≥1) 3⁻ⁿ = (1/3)/(1 − 1/3) = 1/2
```

La suma de las áreas de **todos** los triángulos conservados es media unidad: la
mitad del triángulo original.

## 4. Áreas descartadas

En el paso n se descartan dos de las tres partes iguales:

```
Dₙ = 2·Tₙ = 2·3⁻ⁿ        ΣDₖ (k≤N) = 1 − 3⁻ᴺ        Σ (n≥1) Dₙ = 1 = T₀
```

En el paso N se ha descartado `1 − 3⁻ᴺ` y queda el triángulo `T_N = 3⁻ᴺ`. La suma
es 1 para todo N, así que en el límite lo descartado agota el área original y el
triángulo límite tiene área 0.

## 5. Enfoque matricial

Con `Xₙ = [qₙ, qₙ₋₁, qₙ₋₂]ᵀ`:

```
B = ⎡ 28/3  −27   18 ⎤
    ⎢  1      0    0 ⎥
    ⎣  0      1    0 ⎦
```

`det(B − λI)` reproduce exactamente el polinomio característico de la recurrencia
(propiedad de la matriz compañera). Numéricamente `ρ(B) = {rho:.6f} > 1`, y como
`‖Xₙ‖ ~ ρ(B)ⁿ`, cualquier error de redondeo se multiplica por ρ en cada iteración.

## 6. Conclusión

La sucesión `Tₙ` converge a 0 y la serie converge a 1/2, pero **el algoritmo
importa**: la misma relación algebraica, reescrita como recurrencia de orden
superior, introduce raíces espurias de módulo mayor que 1 que destruyen la
convergencia numérica. La estabilidad queda caracterizada por el radio espectral
de la matriz compañera.
"""


def main(page: ft.Page) -> None:
    """Punto de entrada de la interfaz: configura la ventana y monta la app."""
    page.title = "Sucesiones y Series — Cálculo III"
    try:
        page.window.width = 1340
        page.window.height = 900
    except Exception:
        pass
    App(page)


if __name__ == "__main__":
    ft.run(main)
