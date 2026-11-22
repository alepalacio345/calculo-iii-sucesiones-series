# Explicación del código y sus módulos (guía para la defensa)

Esta guía explica **qué hace cada archivo y cada función**, y cómo traducir las
preguntas del proyecto al código, para que puedas explicarlo el lunes.

La interfaz es **web**: HTML + CSS para lo visual y **Python (FastAPI)** para la
lógica. No hay JavaScript.

---

## 1. Estructura del proyecto

```
proyecto/
├── run_web.cmd                ← lanzador (arranca el servidor web)
├── setup.cmd                  ← instalador: crea el entorno y las dependencias
├── requirements.txt           ← dependencias (numpy, matplotlib, fastapi, uvicorn, jinja2)
├── backend/                   ← TODA la matemática (no depende de la interfaz)
│   ├── sucesiones.py          ← sucesiones, raíces, series, matriz B
│   └── graficas.py            ← las 7 figuras (solo matplotlib)
├── web/                       ← TODA la interfaz (HTML + CSS + servidor Python)
│   ├── web_app.py             ← servidor FastAPI (la "lógica" de la página)
│   ├── templates/index.html   ← la plantilla HTML (Jinja2)
│   └── static/style.css       ← la hoja de estilos
├── scripts/
│   ├── generar_figuras.py     ← exporta las figuras a PNG
│   ├── numeros_clave.py       ← imprime raíces, ρ, formas cerradas
│   └── verificar_matematica.py← verificación independiente
├── tests/test_backend.py      ← pruebas del back-end y las figuras
├── salidas/                   ← 14 figuras PNG ya generadas
├── INFORME.md                 ← el informe del proyecto
└── COMO_EJECUTAR.md           ← guía rápida para ejecutar
```

**Idea clave para la defensa:** separamos la *matemática* (`backend/`) de la
*interfaz* (`web/`). Así las figuras se generan igual por consola (para el informe)
que dentro de la página web.

---

## 2. `backend/sucesiones.py` — la matemática

Este módulo solo produce **datos** (listas, floats, dicts, numpy). No sabe nada de la
interfaz.

| Función | Qué hace | Punto del PDF |
|---|---|---|
| `T_n(n)` | Término general **exacto** `3⁻ⁿ` como `Fraction` | 1 |
| `T_float(n)` | El mismo en coma flotante | 1 |
| `seq_r(N)` | Recurrencia (i) `rₙ = (1/3)rₙ₋₁` | 2 |
| `seq_p(N)` | Recurrencia (ii) `pₙ = (10/3)pₙ₋₁ − pₙ₋₂` | 2 |
| `seq_q(N, c2, c3)` | Recurrencia (iii), con coeficientes configurables | 2 |
| `espectro_r/p/q()` | Raíces del polinomio característico + radio espectral | 2 (análisis crítico) |
| `matriz_B()` | Matriz compañera `B` (3×3) | 5 |
| `analisis_B()` | Autovalores, `ρ(B)`, `det(B−λI)`, verifica coincidencia | 5 |
| `S_exacta()` | `S = 1/2` | 3 |
| `sumas_parciales(N)` | Sumas parciales de `Tₙ` | 3 |
| `areas_descartadas(N)` | `Dₙ = 2·3⁻ⁿ` | 4 |
| `sumas_descartadas(N)` | `Σ Dₖ = 1 − 3⁻ᴺ` | 4 |
| `tabla(N, impreso)` | Todo junto: sucesiones, errores, `n₀`, series | — |
| `forma_cerrada_p/q()` | Coeficientes de la solución cerrada (A·3ⁿ+B·3⁻ⁿ, etc.) | 2 (análisis crítico) |

### 2.1 Detalles que impresionan en la defensa

* **`T_n` se calcula con `Fraction` (exacto), no con float.** Así la "referencia" no
  arrastra su propio error de redondeo, y el error que medimos es *solo* el del
  algoritmo numérico.

* **`n₀` se calcula de varias formas**: `indice_minimo(x)` (el `n` donde `|xₙ|` es
  mínimo), `primer_crecimiento(x)` (primer `n` donde deja de decrecer) y
  `n_teorico(...)` (cruce teórico `|A_malo|ρⁿ = |A_bueno|3⁻ⁿ`).

* **La recurrencia (iii) tiene DOS versiones** (`impreso=True/False`): la impresa
  (`−27, +18`) y la corregida (`−21, +6`), por el hallazgo de §3.6 del informe (la
  impresa no genera `3⁻ⁿ`).

---

## 3. `backend/graficas.py` — las figuras

Cada función devuelve un objeto `Figure` de matplotlib (sin dibujarlo). La web lo
convierte a PNG; los scripts lo guardan como archivo.

| Función | Qué dibuja |
|---|---|
| `fig_sucesiones(d)` | Las 4 sucesiones: escala lineal + logarítmica |
| `fig_sucesiones_detalle(d)` | Un panel por recurrencia + resumen de errores |
| `fig_diferencias(d, relativa)` | `\|Tₙ−xₙ\|` y su raíz n-ésima `\|Tₙ−xₙ\|^(1/n)` |
| `fig_serie(d)` | `S_N → 1/2` y `ΣDₖ → 1` |
| `fig_triangulos()` | La subdivisión geométrica (cadena `T₀>T₁>T₂>T₃`) |
| `fig_autovalores(info)` | Autovalores de `B` en el plano complejo, con `ρ` |
| `guardar_todas(...)` | Genera las 7 figuras como PNG en `salidas/` |

**Figura estrella para la defensa:** `03_diferencias_abs.png` panel (b): muestra que
`|Tₙ−xₙ|^(1/n)` tiende a `1/3`, `3` y `4.37` — es decir, **al autovalor dominante** de
cada recurrencia. Une los puntos 2 (diferencias) y 5 (radio espectral) en una imagen.

---

## 4. `web/web_app.py` — el servidor (FastAPI)

Es el "cerebro" de la página. En una única ruta (`/`) hace todo:

1. Lee los parámetros de la URL: `N` (iteraciones), `modelo` (impresa/corregida) y
   `seccion` (qué pestaña mostrar).
2. Llama a `su.tabla(N, impreso)` y `su.analisis_B(impreso)` del back-end.
3. Según la sección, genera las figuras correspondientes y las pasa a PNG base64 con
   la función `fig64(fig)`.
4. Formatea las tablas y métricas, y devuelve la plantilla renderizada.

```python
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    N = int(request.query_params.get("N", 30))
    modelo = request.query_params.get("modelo", "impreso")
    seccion = request.query_params.get("seccion", "resumen")
    d = su.tabla(N, impreso)         # ← la matemática, reutilizada
    ...
    return templates.TemplateResponse(request, "index.html", ctx)
```

**Detalle clave:** `matplotlib.use("Agg")` al inicio (backend sin ventana, apropiado
para un servidor) y `fig64()` convierte cada figura a una cadena base64 que se incrusta
directamente en el HTML como `<img src="data:image/png;base64,...">`.

---

## 5. `web/templates/index.html` y `web/static/style.css` — lo visual

* **`index.html`** es una plantilla Jinja2 con:
  * una **barra lateral** (navegación entre las 6 secciones mediante enlaces),
  * un **formulario** con `<input type="number">` (iteraciones) y `<select>` (modelo),
  * y un **bloque de contenido** por sección (`{% if seccion == '...' %}`).

* **`style.css`** da el diseño: barra lateral oscura con degradado, tarjetas de
  métricas en cuadrícula, tablas estilizadas y figuras responsivas.

* **Sin JavaScript:** toda la interactividad es HTML puro. Al pulsar "Actualizar" se
  envía el formulario y se **recarga la página** con los nuevos datos. La navegación
  usa enlaces normales (`?seccion=...&N=...&modelo=...`).

---

## 6. `scripts/` y `tests/`

* `generar_figuras.py` → produce las 14 PNG de `salidas/` (las del informe).
* `numeros_clave.py` → imprime raíces, `ρ`, `n₀`, formas cerradas (verificar a mano).
* `verificar_matematica.py` → verificación **independiente** de todo el cálculo.
* `tests/test_backend.py` → comprueba el back-end (tabla, espectros, matriz, serie) y
  que las 7 figuras se generan; si sale `FALLOS: 0`, todo está bien.

---

## 7. Cómo explicar el proyecto en la defensa (hilo lógico)

1. **El problema:** subdividir un triángulo por el baricentro da `Tₙ = 3⁻ⁿ`.
2. **Los 3 algoritmos:** son la *misma* sucesión escrita de 3 formas; las de orden 2 y
   3 añaden **raíces parásitas** (`3`, `6`) con módulo > 1.
3. **Evidencia numérica:** la tabla y las gráficas muestran que `rₙ` sigue a `Tₙ`,
   mientras `pₙ` se despega en `n₀≈6` y `qₙ` en `n₀≈5`.
4. **El porqué:** raíces del polinomio característico; si `|λ| > 1`, el error crece
   como `|λ|ⁿ`.
5. **Serie y áreas:** `S = 1/2` (mitad conservada) y `ΣDₙ = 1 = T₀` (mitad descartada).
6. **Matriz:** `Xₙ = B Xₙ₋₁` con `B` matriz compañera; `ρ(B) > 1` justifica la
   divergencia, porque `‖Xₙ‖ ~ ρⁿ`.

### Preguntas probables y respuestas rápidas

* **¿Por qué diverge `pₙ` si la fórmula es "correcta"?** Porque en coma flotante el
  redondeo introduce la componente `3ⁿ`, que crece sin control.
* **¿Cómo definiste `n₀`?** Índice donde el modo parásito iguala al verdadero;
  coincide con el mínimo de `|xₙ|` (6 para `pₙ`, 5 para `qₙ`).
* **¿Por qué `S = 1/2` y no 1?** Se conserva *una* de cada tres partes; la otra mitad
  se descarta (`ΣDₙ = 1`).
* **¿Por qué `Fraction` para `Tₙ`?** Para que la referencia sea exacta y el error
  medido refleje solo el algoritmo.
* **¿Qué es el radio espectral?** El mayor módulo de los autovalores; si es > 1, el
  error se amplifica en cada iteración.
* **¿Por qué no usaste JavaScript?** Para mantener todo el front-end en HTML/CSS puro;
  la interactividad se resuelve con formularios y recarga de página.
