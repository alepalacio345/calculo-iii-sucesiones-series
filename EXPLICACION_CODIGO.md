# Explicación del código y sus módulos (guía para la defensa)

Esta guía explica **qué hace cada archivo y cada función**, y cómo traducir las
preguntas del proyecto al código, para que puedas explicarlo el lunes.

---

## 1. Estructura del proyecto (back-end / front-end separados)

```
proyecto/
├── app.py                     ← PUNTO DE ENTRADA (arranca la interfaz)
├── run_app.cmd                ← lanzador de la ventana nativa
├── backend/                   ← TODA la matemática (no depende de la UI)
│   ├── sucesiones.py          ← sucesiones, raíces, series, matriz B
│   └── graficas.py            ← las 7 figuras (solo matplotlib)
├── frontend/                  ← TODA la interfaz
│   └── app.py                 ← clase App + secciones + controles Flet
├── scripts/                   ← utilidades de consola
│   ├── generar_figuras.py     ← exporta las figuras a PNG
│   ├── numeros_clave.py       ← imprime raíces, ρ, formas cerradas
│   ├── verificar_matematica.py← verificación independiente
│   └── instalar_deps.py       ← instalador de dependencias (por si pip falla)
├── tests/test_interfaz.py     ← prueba headless (sin ventana)
├── salidas/                   ← 14 figuras PNG ya generadas
├── INFORME.md                 ← el informe del proyecto
└── INVESTIGACION.md           ← investigación y comparación de frameworks
```

**Idea clave para la defensa:** separamos la *matemática* (backend) de la *interfaz*
(frontend). Así las figuras se generan igual por consola (para el informe) que dentro
de la app.

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
  algoritmo numérico. (En `seq_r/p/q` sí se usa float, como pide el enunciado.)

* **`n₀` se calcula de tres formas** (todas documentadas):
  * `indice_minimo(x)` → el `n` donde `|xₙ|` es mínimo (el "fondo" antes de crecer).
  * `primer_crecimiento(x)` → el primer `n` donde `|xₙ|` deja de decrecer.
  * `n_teorico(A_malo, A_bueno, ρ)` → el cruce teórico `|A_malo|ρⁿ = |A_bueno|3⁻ⁿ`.

* **La recurrencia (iii) tiene DOS versiones** (`impreso=True/False`): la impresa
  (`−27, +18`) y la corregida (`−21, +6`). Es la consecuencia del hallazgo de §3.6 del
  informe: la impresa **no** genera `3⁻ⁿ`.

---

## 3. `backend/graficas.py` — las figuras

Cada función devuelve un objeto `Figure` de matplotlib (sin dibujarlo). En la app se
convierte a PNG; en consola se guarda como archivo.

| Función | Qué dibuja |
|---|---|
| `fig_sucesiones(d)` | Las 4 sucesiones: escala lineal + escala logarítmica |
| `fig_sucesiones_detalle(d)` | Un panel por recurrencia + resumen de errores |
| `fig_diferencias(d, relativa)` | `\|Tₙ−xₙ\|` y su raíz n-ésima `\|Tₙ−xₙ\|^(1/n)` |
| `fig_serie(d)` | `S_N → 1/2` y `ΣDₖ → 1` |
| `fig_triangulos()` | La subdivisión geométrica (cadena `T₀>T₁>T₂>T₃` y reparto 1/3 + 2/3) |
| `fig_autovalores(info)` | Autovalores de `B` en el plano complejo, con `ρ` |
| `guardar_todas(...)` | Genera las 7 figuras como PNG en `salidas/` |

**Figura estrella para la defensa:** `03_diferencias_abs.png` panel (b): muestra que
`|Tₙ−xₙ|^(1/n)` tiende a `1/3`, `3` y `4.37` — es decir, **al autovalor dominante** de
cada recurrencia. Une los puntos 2 (diferencias) y 5 (radio espectral) en una imagen.

---

## 4. `frontend/app.py` — la interfaz

* **Helpers** (al inicio): `fmt()` (formatea números), `tarjeta()`, `titulo()`,
  `tabla()` (construye un `DataTable`), `chart()` (figura → `ft.Image`), `metrica()`
  (tarjeta con un valor destacado).

* **Clase `App`** — guarda el estado (`N`, `modelo`, `seccion`) y construye la UI:

| Sección | Qué muestra |
|---|---|
| `resumen` | Planteamiento, métricas (`T₁, T₅, T₃₀, S, ΣDₙ`), figura de los triángulos |
| `sucesiones` | Las 4 sucesiones (2 figuras) + tabla comparativa |
| `diferencias` | `n₀` de cada una + 2 figuras de errores + tabla de diferencias |
| `serie` | `S_N`, `Dₙ`, `ΣDₖ` (métricas + figura + tabla) |
| `matriz` | Matriz `B`, autovalores, `ρ(B)`, `tr`, `det`, figura del espectro |
| `informe` | Borrador del análisis en Markdown (dentro de la app) |

* **Controles:** el deslizador (`N` de 5 a 60), el selector de modelo (impresa /
  corregida), y el menú lateral. Al cambiar algo se reconstruye la sección activa
  (`refrescar()`).

* `main(page)` — punto de entrada que Flet invoca; monta la `App`.

### 4.1 Por qué las gráficas son imágenes y no canvas interactivo

Inicialmente usamos el canvas interactivo de Flet (`MatplotlibChart`, con zoom/pan),
pero no renderizaba de forma fiable (dejaba la ventana gris). Lo cambiamos a
**imágenes PNG** (`ft.Image`), que es un control base y siempre se dibuja. Es una
decisión de fiabilidad, no de matemática.

---

## 5. `app.py` y `run_app.cmd` — cómo arranca

* **`app.py`** (raíz): fija `MPLCONFIGDIR` a una carpeta local (para que matplotlib no
  falle si no puede escribir en `%LOCALAPPDATA%`), y llama `ft.run(main)`.

* **`run_app.cmd`**: lanzador de la **ventana nativa**. Redirige dos cachés **dentro
  del proyecto** (`.cache\home` y `.cache\mpl`) porque Flet descarga su cliente de
  escritorio a `C:\Users\<usuario>\.flet`, y en algunos equipos/entornos esa carpeta no
  es escribible. El lanzador evita el problema.

  ```bat
  set "USERPROFILE=%ROOT%.cache\home"
  set "MPLCONFIGDIR=%ROOT%.cache\mpl"
  flet run app.py
  ```

---

## 6. `scripts/` y `tests/`

* `generar_figuras.py` → produce las 14 PNG de `salidas/` (las del informe).
* `numeros_clave.py` → imprime raíces, `ρ`, `n₀`, formas cerradas (para verificar a mano).
* `verificar_matematica.py` → verificación **independiente** de todo el cálculo.
* `instalar_deps.py` → instala las dependencias de Flet sin usar el resolver de pip
  (que a veces se cuelga). Solo necesario si el entorno se rompe.
* `tests/test_interfaz.py` → construye **todas las secciones** para `N=5` y `N=60` sin
  abrir ventana; si pasa (`FALLOS: 0`), la UI no tiene errores de construcción.

---

## 7. Cómo explicar el proyecto en la defensa (hilo lógico)

1. **El problema:** subdividir un triángulo por el baricentro da `Tₙ = 3⁻ⁿ`.

2. **Los 3 algoritmos:** son la *misma* sucesión escrita de 3 formas. La diferencia es
   que las recurrencias de orden 2 y 3 añaden **raíces parásitas** (`3`, `6`) con
   módulo > 1, que el redondeo de las condiciones iniciales "despierta".

3. **La evidencia numérica:** la tabla y las gráficas muestran que `rₙ` sigue a `Tₙ`,
   mientras que `pₙ` se despega en `n₀≈6` y `qₙ` en `n₀≈5`.

4. **El porqué (análisis crítico):** las raíces del polinomio característico. Si
   `|λ| > 1`, el error crece como `|λ|ⁿ`.

5. **La serie y las áreas:** `S = 1/2` (mitad conservada) y `ΣDₙ = 1 = T₀` (mitad
   descartada), coherentes entre sí.

6. **El enfoque matricial:** `Xₙ = B Xₙ₋₁` con `B` matriz compañera; `ρ(B) > 1`
   justifica la divergencia, porque `‖Xₙ‖ ~ ρⁿ`.

### Preguntas probables y respuestas rápidas

* **¿Por qué diverge `pₙ` si la fórmula es "correcta"?** Porque la fórmula en coma
  flotante *no* es la misma que en aritmética exacta: el redondeo introduce la
  componente `3ⁿ`, que crece sin control.

* **¿Cómo definiste `n₀`?** Como el índice donde el modo parásito iguala al modo
  verdadero; coincide con el mínimo de `|xₙ|` (6 para `pₙ`, 5 para `qₙ`).

* **¿Por qué `S = 1/2` y no 1?** Porque se conserva *una* de cada tres partes; la otra
  mitad es la que se descarta (`ΣDₙ = 1`). Juntas suman 1.5 en apariencia, pero los
  conservados se vuelven a partir (se solapan), así que no es una partición disjunta.

* **¿Por qué usaste `Fraction` para `Tₙ`?** Para que la referencia sea exacta y el
  error medido refleje solo el algoritmo, no la referencia.

* **¿Qué es el radio espectral?** El mayor módulo de los autovalores; si es > 1, el
  error se amplifica en cada iteración.

* **¿Y la recurrencia (iii) "corregida"?** La impresa no tiene a `1/3` como raíz
  (`P(1/3) = −10`); los coeficientes coherentes son `−21` y `+6`. Implementamos ambas
  y lo documentamos.
