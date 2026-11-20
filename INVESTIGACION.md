# Investigación del proyecto «Sucesiones y Series»

**Curso:** Cálculo III · **Entrega:** 23/11/2026 · **Modalidad:** grupos de dos
**Documento analizado:** `Proyecto Sucesiones y Series.pdf` (2 páginas)
**Fecha de esta investigación:** 20/11/2026 — *quedan 3 días para la entrega*

---

## 0. Resumen en una página

| Pregunta | Respuesta corta |
|---|---|
| ¿Qué pide el proyecto? | Implementar una sucesión geométrica de áreas (`Tₙ = 3⁻ⁿ`), compararla con **tres recurrencias** que deberían dar lo mismo, tabular y graficar el error, calcular dos series, y analizar la **matriz compañera** y su **radio espectral**. |
| ¿Entradas del programa? | Muy pocas: `N` (iteraciones), los valores iniciales (`r₀`, `p₁`, `q₂`) y los coeficientes de la recurrencia. **No hay datos externos.** |
| ¿Salidas? | 2 tablas, 4–6 gráficas, el índice `n₀` de divergencia, `S = ½`, `ΣDₙ = 1`, la matriz `B`, sus autovalores y `ρ(B)`. |
| ¿Sirve Flet? | **Sí, y bien.** Flet 1.x tiene `MatplotlibChart` nativo (con barra de herramientas: zoom, pan, descarga), `DataTable` y `Markdown`. Es la mejor opción para ti. |
| ¿Hay algún problema? | **Sí, uno importante:** la recurrencia (iii) **tal como está impresa no genera `Tₙ`**. Ver §3. |
| ¿Se puede hacer en 3 días? | Sí, si se decide hoy qué hacer con la errata (§10) y no se sobre-diseña la interfaz. |

---

## 1. Qué hay que hacer exactamente

El PDF plantea un único escenario y cinco entregables.

**Escenario.** Triángulo equilátero de área `T₀ = 1`. Se une el baricentro con los
tres vértices: el triángulo queda partido en **tres triángulos congruentes de área
`1/3` del anterior**. Se conserva uno (`T₁`) y se repite indefinidamente.

| # | Entregable | Producto concreto |
|---|---|---|
| 1 | Término general | Expresión de `Tₙ` (y `T₀ = 1`) |
| 2 | Análisis numérico y estabilidad | Implementar `Tₙ, rₙ, pₙ, qₙ`; **tabla comparativa**; **gráfica de las cuatro** en un plano o paneles; determinar **`n₀`**; **segunda tabla** con las diferencias absolutas o relativas de `Tₙ` contra `rₙ`, `pₙ` y `qₙ`; **gráfica de las diferencias**; **análisis crítico** justificado con las raíces de los polinomios característicos |
| 3 | Serie infinita | `S = Σ Tₙ` (n ≥ 1) + interpretación geométrica |
| 4 | Extensión | Término general de `Dₙ` (área descartada) y demostración de que `Σ Dₙ = T₀` |
| 5 | Matriz y espectro | `Xₙ = B Xₙ₋₁`, polinomio característico por `det(B − λI)`, autovalores con `numpy.linalg.eig`, radio espectral `ρ(B)` y su relación con la divergencia |

**Requisitos de forma** (lo que se califica): tablas, gráficas legibles,
justificación matemática, interpretación geométrica. El PDF dice explícitamente
«utilice un lenguaje de programación de su preferencia (Python, C++, MATLAB…)».

---

## 2. La matemática resuelta

> Todo lo que sigue está implementado y **verificado numéricamente** en
> `core/sucesiones.py` y `scripts/verificar_matematica.py`.

### 2.1 Término general (punto 1)

Cada paso divide el área entre 3 y se conserva una parte:

```
Tₙ = 3⁻ⁿ ,   T₀ = 1 ,   T₁ = 1/3 ,  T₂ = 1/9 ,  T₃ = 1/27 , …
```

Es una **sucesión geométrica** de razón `r = 1/3`, decreciente y con
`lim Tₙ = 0`.

> **Detalle de implementación que suma puntos:** calcular la referencia `Tₙ` con
> aritmética exacta (`fractions.Fraction`, `Fraction(1,3)**n`) y convertir a
> `float` sólo al mostrar. Si la referencia se calcula también en coma flotante,
> el «error» que se mide incluye el error de la propia referencia.

### 2.2 Los tres algoritmos y sus raíces (punto 2)

Los tres son la misma sucesión escrita de otra forma. La diferencia está en el
**polinomio característico**: si tiene raíces de módulo mayor que 1, el error de
redondeo crece y el algoritmo diverge.

| | Recurrencia | Polinomio característico | Raíces | `ρ` |
|---|---|---|---|---|
| **(i)** | `rₙ = ⅓ rₙ₋₁`, `r₀ = 0.99997` | `λ − 1/3` | `1/3` | **0.333** |
| **(ii)** | `pₙ = (10/3)pₙ₋₁ − pₙ₋₂`, `p₀=1`, `p₁=0.33334` | `λ² − (10/3)λ + 1` | `3`, `1/3` | **3** |
| **(iii)** *impresa* | `qₙ = (28/3)qₙ₋₁ − 27qₙ₋₂ + 18qₙ₋₃` | `λ³ − (28/3)λ² + 27λ − 18` | `4.195163 ± 1.220027i`, `0.943008` | **4.369** |
| **(iii)** *corregida* | `qₙ = (28/3)qₙ₋₁ − 21qₙ₋₂ + 6qₙ₋₃` | `λ³ − (28/3)λ² + 21λ − 6` | `6`, `3`, `1/3` | **6** |

**Formas cerradas** (esto es lo que hay que poner en el análisis crítico):

```
(i)   rₙ = 0.99997 · 3⁻ⁿ
      ⟹ |Tₙ − rₙ| = 3·10⁻⁵ · 3⁻ⁿ            → 0   (error relativo constante 3·10⁻⁵)

(ii)  pₙ = A·3ⁿ + B·3⁻ⁿ ,  A = 2.5·10⁻⁶ ,  B = 0.9999975
      ⟹ el modo espurio 3ⁿ acaba dominando: el error crece como 9ⁿ

(iii) qₙ = 5.228758·10⁻⁷·6ⁿ − 1.111111·10⁻⁶·3ⁿ + 1.000001·3⁻ⁿ
      ⟹ el modo espurio 6ⁿ domina: el error crece como 18ⁿ
```

El coeficiente `A` de (ii) no es casual: sale de que `p₁ = 0.33334 ≠ 1/3` por
`6.7·10⁻⁶`. Ese pequeño «0.00034» de más es **toda** la causa de la divergencia.

### 2.3 ¿A partir de qué índice `n₀` se observa divergencia?

Hay que dar un criterio explícito. El más defendible es **el índice en que el
modo espurio iguala al modo bueno**:

```
|A_malo|·ρⁿ = |A_bueno|·3⁻ⁿ   ⟹   n* = ln(|A_bueno/A_malo|) / ln(3ρ)
```

| Algoritmo | `n*` teórico | `n₀` empírico (mínimo de la sucesión) | primer `n` con error > 100 % |
|---|---|---|---|---|
| (i) `rₙ` | — (no diverge) | — | nunca |
| (ii) `pₙ` | **5.87** | **6** | 6 |
| (iii) corregida | **5.0** | **5** | 6 |
| (iii) impresa | — (no aplica) | 2 | 3 |

El acuerdo entre la predicción teórica y el valor medido (6 ↔ 5.87, 5 ↔ 5.0) es
justamente el argumento que pide la rúbrica. En `core/sucesiones.py` están las
tres definiciones implementadas (`n0_min`, `n0_crece`, `n100`) para poder
reportar la que el profesor prefiera.

### 2.4 Serie infinita y áreas descartadas (puntos 3 y 4)

```
S = Σ_{n≥1} 3⁻ⁿ = (1/3)/(1 − 1/3) = 1/2
```

**Interpretación geométrica:** la suma de las áreas de *todos* los triángulos
conservados es **media unidad**, es decir la mitad del triángulo original.

En el paso `n` se descartan dos de las tres partes iguales, luego

```
Dₙ = 2·Tₙ = 2·3⁻ⁿ
Σ_{n≥1} Dₙ = 2·(1/2) = 1 = T₀          ✔
```

**Demostración por sumas parciales** (la forma elegante, y la que cierra el
problema): tras `N` pasos se ha descartado

```
Σ_{k=1}^{N} Dₖ = 1 − 3⁻ᴺ
```

y queda el triángulo `T_N = 3⁻ᴺ`. La suma es `1` exacto para todo `N`, así que en
el límite lo descartado agota el área original y el triángulo límite tiene área
`lim Tₙ = 0`. Que `Σ conservado + Σ descartado = 1.5` no es una contradicción: los
triángulos conservados se vuelven a partir en el paso siguiente (se solapan).

### 2.5 Matriz compañera y análisis espectral (punto 5)

Con `Xₙ = [qₙ, qₙ₋₁, qₙ₋₂]ᵀ`:

```
        ⎡ 28/3  −27   18 ⎤
B  =    ⎢  1      0    0 ⎥      (versión impresa; con la corrección: −21 y 6)
        ⎣  0      1    0 ⎦
```

Propiedad de la matriz compañera: `det(B − λI)` reproduce **exactamente** el
polinomio característico de la recurrencia. Verificado numéricamente
(`np.poly(B)` = `[1, −28/3, 27, −18]`, coincidencia exacta), y además
`tr(B) = 28/3`, `det(B) = 18` (que es `−` el término independiente, con el signo
correcto).

```
ρ(B) = max|λᵢ| = 4.368965  >  1   (impresa)
ρ(B) = 6.000000            >  1   (corregida)
```

**Cómo se justifica la divergencia:** `‖Xₙ‖ ~ ρ(B)ⁿ`. Todo error de redondeo
introducido en un paso se multiplica por `ρ` en cada iteración; con `ρ > 1` el
error crece geométricamente y acaba tapando la solución. Con `ρ = 6`, en 20 pasos
el factor es `6²⁰ ≈ 3.7·10¹⁵`. La estabilidad del algoritmo queda **caracterizada
por el radio espectral**: es el puente entre la recurrencia algebraica y el
comportamiento numérico observado en las gráficas.

---

## 3. Hallazgo importante: la recurrencia (iii) impresa no genera `Tₙ`

Esto hay que resolverlo **antes** de escribir el informe. Tres pruebas
independientes:

**Prueba 1 — evaluación directa.** Si `1/3` fuese raíz del polinomio impreso:

```
P(λ) = λ³ − (28/3)λ² + 27λ − 18
P(1/3) = 1/27 − 28/27 + 9 − 18 = −27/27 − 9 = −10 ≠ 0     ✘
```

**Prueba 2 — la recurrencia se contradice a sí misma.** Con `q₀=1, q₁=1/3,
q₂=0.11112`, el primer valor que produce la recurrencia impresa es

```
q₃ = (28/3)(0.11112) − 27(1/3) + 18(1) = 10.03712
```

cuando debería ser `T₃ = 0.037037`. **Se desvía por un factor de 271 ya en el
tercer término**, no es una divergencia gradual por redondeo.

**Prueba 3 — el coeficiente `28/3` delata la intención.** Ese valor es exactamente
el que corresponde a las raíces `1/3, 3, 6`:

```
(λ − 1/3)(λ − 3)(λ − 6) = λ³ − (28/3)λ² + 21λ − 6
```

Es decir: el coeficiente de `λ²` está bien, y los otros dos (`27` y `18`) están
mal; deberían ser **`21` y `6`**. Con esa corrección las raíces son `1/3, 3, 6`,
el patrón es el mismo que en (ii) (una raíz buena y una parásita) pero con
divergencia `6ⁿ` en vez de `3ⁿ` — que es *exactamente* la progresión pedagógica
que el enunciado quiere mostrar.

**Consecuencias prácticas:**

- La variedad «impresa» **sí es analizable** (tiene `ρ = 4.369 > 1`, y sus raíces
  complejas producen un cambio de signo observable en `q₂₀ = −3.59·10¹²`), pero
  rompe la premisa del enunciado («algebraicamente generan *la misma* sucesión»).
- La variedad «corregida» respeta la premisa y produce un ejemplo más limpio.

**Recomendación:** implementar **las dos** (el prototipo ya lo hace, con un
selector en la interfaz) y explicar la discrepancia en el informe como *observación
crítica*. Es la salida que no depende de la decisión del profesor. Si se puede
preguntar antes del 23/11, mejor: es la pregunta nº 1 de §10.

---

## 4. Entradas y salidas del programa

### 4.1 Entradas

No hay ficheros de datos. Todo son parámetros:

| Entrada | Tipo | Valor del enunciado | ¿La cambia el usuario? |
|---|---|---|---|
| `N` | entero | «un número suficiente de iteraciones» → 20–30 | sí (deslizador 5–60) |
| `r₀` | real | `0.99997` | opcional |
| `p₀`, `p₁` | reales | `1`, `0.33334` | opcional |
| `q₀`, `q₁`, `q₂` | reales | `1`, `1/3`, `0.11112` | opcional |
| Coeficientes de (iii) | reales | `28/3, −27, 18` | sí (impresa / corregida) |
| `T₀` | real | `1` | no |

### 4.2 Salidas (lo que el programa calcula)

1. Las cuatro sucesiones para `n = 0…N`.
2. Tabla comparativa (punto 2).
3. Tabla de diferencias `Tₙ − rₙ`, `Tₙ − pₙ`, `Tₙ − qₙ` (absolutas y relativas).
4. `n₀` de convergencia/divergencia, por el criterio elegido.
5. Polinomios característicos, raíces y `ρ` de cada recurrencia.
6. `S` exacta (1/2) y sumas parciales `S_N`.
7. `Dₙ = 2·3⁻ⁿ` y su suma acumulada → 1.
8. Matriz `B`, `det(B − λI)`, autovalores, `ρ(B)`, traza y determinante.

### 4.3 Salidas en pantalla y en disco

| Salida | Formato |
|---|---|
| Gráficas de las cuatro sucesiones | ventana Flet (matplotlib embebido, con zoom/pan/descarga) |
| Gráficas de diferencias | ídem |
| Gráfica de la serie y áreas descartadas | ídem |
| Dibujo de la subdivisión del triángulo | ídem |
| Autovalores en el plano complejo | ídem |
| Tablas | `DataTable` de Flet, con scroll |
| Exportación | PNG (botón de descarga de la propia gráfica) + CSV/PNG vía `scripts/generar_figuras.py` |

---

## 5. Flet: investigación a fondo

### 5.1 Estado actual (noviembre 2026)

- Versión estable instalada y probada: **`flet 1.1.2`** (`requires_python >= 3.10`).
  La serie 1.x sustituyó a la 0.28.x; la 1.0 final salió de la beta 0.80.0.
- Los **controles de gráficos salieron a un paquete aparte**: `flet-charts`
  (misma versión, `1.1.2`).
- `numpy`, `pandas`, `matplotlib` funcionan sin problema en el proceso de Python.

### 5.2 Lo que ofrece para *este* proyecto

| Necesidad | Control de Flet | Veredicto |
|---|---|---|
| Curvas con escala logarítmica | `flet_charts.MatplotlibChart` ← figura de matplotlib | ✅ perfecto: `semilogy` resuelve el rango `10⁻²⁰ … 10⁺¹⁵` |
| Zoom / pan / guardar imagen | `MatplotlibChartWithToolbar` | ✅ barra de herramientas lista, sin código extra |
| Tablas de 20–30 filas | `ft.DataTable` (`DataColumn`/`DataRow`/`DataCell`) | ✅ con `Column(scroll=AUTO)` + `Row(scroll=AUTO)` |
| Fórmulas en el informe | `ft.Markdown` | ⚠️ LaTeX **no** está garantizado; usar notación `Tₙ`, `3⁻ⁿ` en Unicode |
| Aspecto moderno | Material 3, `Colors.SURFACE_CONTAINER_*` | ✅ se ve profesional sin esfuerzo |
| Un solo código → Windows/web/móvil | `flet run` / `flet run --web` | ✅ |
| Entregar un `.exe` | `flet build windows` (Flutter SDK) / `flet pack` (PyInstaller) | ⚠️ `flet build` exige instalar el SDK de Flutter (pesado) |

### 5.3 Trampas detectadas (importantes)

1. **`ft.ElevatedButton` ya no existe.** En 1.1 es `ft.Button` (y `ft.FilledButton`).
   Casi todos los tutoriales de internet siguen usando la API 0.28 → no compilan.
2. **`ft.app()` ya no existe**: es `ft.run(main)`. El error que lanza
   (`'module' object is not callable`) es confuso.
3. **`Dropdown` no usa `on_change`, usa `on_select`.** Comprobado en la firma real.
4. **Modelo de un solo hilo (cambio de la 1.0).** Los manejadores síncronos corren
   en el bucle de eventos: si tardan, la ventana no repinta. En este proyecto no
   importa (recalcular 60 términos es instantáneo), pero conviene saberlo.
5. **`pip install "flet[all]"` puede colgarse** resolviendo dependencias (pasó en
   esta máquina >10 min con CPU al 100 %). Solución que funcionó: instalar
   `--no-deps` y luego las dependencias sueltas (`msgpack`, `oauthlib`, `repath`,
   `httpx`).
6. **El cliente de escritorio se descarga en el primer arranque**, no viene en el
   wheel (`flet-desktop` son sólo 18 kB). La primera vez necesita internet y un
   rato. En un entorno con el directorio de caché bloqueado, la ventana no llega a
   abrirse.
7. **No hay `ft.testing` en 1.1.2**: para probar sin GUI hay que construir los
   controles sin `Page` (lo hace `tests/test_interfaz.py`).

### 5.4 Matplotlib dentro de Flet — cómo se usa (API real, 1.1.2)

```python
import matplotlib.pyplot as plt
import flet as ft
import flet_charts as fch

def main(page: ft.Page):
    fig, ax = plt.subplots()
    ax.semilogy([0, 1, 2], [1, 0.33, 0.11])
    page.add(fch.MatplotlibChartWithToolbar(figure=fig, expand=True))
    # o bien: fch.MatplotlibChart(figure=fig, expand=True)

ft.run(main)
```

No hay que configurar backend, ni convertir a base64, ni `matplotlib.use("svg")`
(eso era la 0.28). El control pinta la figura en un canvas real y devuelve los
eventos del ratón: se puede hacer zoom sobre la zona donde `pₙ` empieza a crecer.

---

## 6. Alternativas comparadas

| | **Flet** | Streamlit | NiceGUI | Dash / Plotly | PySide6 o Tkinter + matplotlib |
|---|---|---|---|---|---|
| Gráficas log con zoom | ✅ matplotlib nativo + toolbar | ✅ pero re-ejecuta el script | ✅ matplotlib/ECharts | ✅ Plotly (zoom excelente) | ✅ matplotlib, Zoom manual |
| Tablas | ✅ `DataTable` | ✅ `st.dataframe` | ✅ | ✅ `dash_table` | ⚠️ a mano (`QTableWidget`) |
| Interactividad | ✅ nativa | ✅ pero modelo «rerun» | ✅ | ✅ callbacks | ✅ pero mucho código |
| Aspecto visual | ✅✅ Material 3 | ✅ limpio, tipo dashboard | ✅ | ✅ | ⚠️ anticuado (Tk) / ✅ (Qt) |
| Código necesario | medio | **bajo** | medio | alto | **alto** |
| App de escritorio real | ✅ | ❌ (servidor web) | ⚠️ modo nativo | ❌ | ✅ |
| `.exe` | ✅ `flet build` | ❌ | ⚠️ | ❌ | ✅ PyInstaller |
| Curva de aprendizaje | baja-media | **muy baja** | media | media-alta | alta |
| Encaja con lo que te gusta | **sí** (ya lo conoces) | no | — | — | — |

**Veredicto:** Flet no sólo *sirve*, es la opción adecuada. El único punto donde
otra herramienta sería mejor es la velocidad de desarrollo (Streamlit), y aquí no
compensa porque el proyecto pide **un programa**, no un notebook.

**Plan B realista:** si el 22/11 la interfaz no está cerrada, sacar las figuras
con `scripts/generar_figuras.py` (ya funciona) y montar el informe con esas PNG.
El programa en Flet se entrega igual, sin depender de él para las gráficas.

**Plan C:** `flet_charts.LineChart` nativo (sin matplotlib). **No lo recomiendo**:
no hay escala logarítmica, y con estos datos (`10⁻²⁰` a `10¹⁵`) las curvas serían
inservibles.

---

## 7. Recomendación

```
Python 3.12 + Flet 1.1.2 + flet-charts + matplotlib + numpy
```

- **Flet para la interfaz**: menú lateral, controles (`N`, modelo), `DataTable` y
  `Markdown` para el informe.
- **matplotlib para las figuras**, embebidas con `MatplotlibChartWithToolbar`: así
  se cumple «graficar» con calidad y además se puede hacer zoom en la zona
  interesante durante la defensa.
- **numpy sólo para las raíces y autovalores** (`np.roots`, `np.linalg.eigvals`),
  que es literalmente lo que pide el punto 5.
- **`Fraction` para `Tₙ`**: referencia exacta, sin contaminar la comparación.
- Lógica separada de la interfaz (`core/`), para poder generar las PNG del informe
  sin abrir la ventana.

---

## 8. Lo que ya está construido y verificado

```
proyecto/
├── Proyecto Sucesiones y Series.pdf
├── INVESTIGACION.md          ← este documento
├── main.py                   ← punto de entrada (arranca la interfaz)
├── backend/
│   ├── sucesiones.py         ← toda la matemática, sin UI
│   └── graficas.py           ← las 7 figuras, sólo matplotlib
├── frontend/
│   └── app.py                ← la interfaz Flet (menú, tablas, informe)
├── scripts/
│   ├── generar_figuras.py    ← exporta las PNG a salidas/
│   ├── verificar_matematica.py
│   └── numeros_clave.py
├── tests/
│   └── test_interfaz.py      ← construye todas las secciones sin GUI
├── salidas/                  ← 14 PNG ya generadas
└── .venv/                    ← entorno con flet 1.1.2
```

**Qué está comprobado:**

- ✅ La matemática: sucesiones, raíces, `ρ`, series, matriz `B` — verificados con
  dos implementaciones independientes.
- ✅ Las 7 figuras se generan y fueron revisadas visualmente (§8.1).
- ✅ La interfaz: las 6 secciones × 2 modelos × `N∈{5,30,60}` se construyen sin
  errores (`tests/test_interfaz.py` → `FALLOS: 0`). Esto valida nombres de clases,
  argumentos, enums de color/icono, tablas y el `Markdown` del informe.
- ⚠️ **No verificado:** la ventana real. En este entorno el cliente Flutter no
  puede descargarse (directorio de caché bloqueado), así que el proceso arranca
  pero no llega a pintar. **Hay que probarlo en tu sesión normal** con
  `flet run main.py`.

### 8.1 Las figuras

| Archivo | Contenido |
|---|---|
| `salidas/01_sucesiones.png` | las cuatro sucesiones, escala lineal y log |
| `salidas/02_sucesiones_detalle.png` | un panel por recurrencia + resumen del error |
| `salidas/03_diferencias_abs.png` | error absoluto y su raíz n-ésima, que tiende al autovalor dominante |
| `salidas/04_diferencias_rel.png` | error relativo (se ve el 3·10⁻⁵ constante de `rₙ`) |
| `salidas/05_serie_y_descartes.png` | `S_N → 1/2` y `ΣDₖ → 1` |
| `salidas/06_subdivision_geometrica.png` | la cadena `T₀>T₁>T₂>T₃` y el reparto 1/3 + 2/3 |
| `salidas/07_autovalores.png` | autovalores de `B`, círculo unitario y `ρ` |

Los archivos con sufijo `_variante` corresponden a la recurrencia (iii)
**corregida**.

La figura `03` es la más valiosa para la rúbrica: el panel (b) demuestra
empíricamente que `|Tₙ−xₙ|^{1/n}` tiende a `1/3`, `3` y `4.37` — es decir, al
autovalor dominante de cada recurrencia. Conecta los tres puntos del enunciado
(diferencias, raíces del polinomio y radio espectral) en **una sola imagen**.

---

## 9. Cómo ejecutarlo

```powershell
cd "C:\Users\slara\Documents\calculo III\proyecto"

# el entorno ya está creado con flet 1.1.2
.\.venv\Scripts\activate

flet run main.py            # ventana nativa (la 1ª vez descarga el cliente)
flet run --web main.py      # en el navegador, sin cliente de escritorio

# o sin interfaz, sólo las figuras y los números:
python scripts\generar_figuras.py
python scripts\numeros_clave.py
python tests\test_interfaz.py
```

Si `flet run` falla al descargar el cliente, `pip install flet-desktop` y reintentar.

---

## 10. Decisiones pendientes

1. **¿Qué hacemos con la recurrencia (iii)?** ⚠️ *la más urgente*
   - (a) entregar la impresa y señalar la inconsistencia como hallazgo;
   - (b) entregar la corregida (`−21, +6`) explicando la errata;
   - (c) **entregar ambas** con el selector (lo que ya hace el prototipo) ← recomendado.
2. **¿Qué criterio de `n₀` quiere el profesor?** El enunciado no lo define. Hay tres
   razones defendibles (mínimo de `|xₙ|`, primer crecimiento, error relativo > 100 %).
   Conviene declarar el criterio usado en el informe.
3. **¿Tabla hasta qué `N`?** Con `N = 30` ya se ve todo. Más allá de ~300 los
   `float` de 64 bits pierden sentido (`3⁻ⁿ` subdesborda hacia `n ≈ 645`).
4. **¿Formato de entrega?** ¿Informe PDF + código, o sólo código con el informe
   dentro de la app?
5. **¿Se permite `numpy` para las raíces?** El propio PDF lo sugiere
   (`numpy.linalg.eig`), así que sí.

---

## 11. Plan sugerido para los 3 días

| Día | Trabajo |
|---|---|
| **20/11 (hoy)** | Decidir §10.1. Probar `flet run main.py` en tu sesión. Ajustar la interfaz si algo no pinta. |
| **21/11** | Redactar el informe con las derivaciones de §2 (ya están hechas): término general, formas cerradas, `n₀`, series, matriz. Insertar las PNG de `salidas/`. |
| **22/11** | Revisión cruzada: comprobar que cada punto del PDF tiene su tabla/gráfica. Preparar la defensa (saber explicar por qué `ρ > 1` implica divergencia). |
| **23/11** | Entrega. |

---

## Anexo: números clave para copiar al informe

```
Tₙ = 3⁻ⁿ

(i)   rₙ = 0.99997·3⁻ⁿ
      |Tₙ − rₙ| = 3·10⁻⁵·3⁻ⁿ      error relativo constante = 3.0·10⁻⁵
      λ = 1/3                        ρ = 0.3333   → estable

(ii)  λ² − (10/3)λ + 1 = 0        λ = 3 ; 1/3    ρ = 3   → diverge desde n₀ ≈ 6
      pₙ = 2.5·10⁻⁶·3ⁿ + 0.9999975·3⁻ⁿ            n* = 5.87

(iii) impresa:  λ³ − (28/3)λ² + 27λ − 18 = 0
      λ = 4.195163 ± 1.220027i ;  0.943008       ρ = 4.368965
      P(1/3) = −10    q₃ = 10.03712 (≠ T₃ = 0.037037)    q₂₀ = −3.59·10¹²

(iii) corregida: λ³ − (28/3)λ² + 21λ − 6 = 0
      λ = 6 ; 3 ; 1/3                            ρ = 6
      qₙ = 5.2288·10⁻⁷·6ⁿ − 1.1111·10⁻⁶·3ⁿ + 1.000001·3⁻ⁿ   n* = 5.0

S  = Σ_{n≥1} Tₙ = 1/2
Dₙ = 2·3⁻ⁿ ,   Σ_{k≤N} Dₖ = 1 − 3⁻ᴺ ,   Σ_{n≥1} Dₙ = 1 = T₀

B = [[28/3, −27, 18], [1, 0, 0], [0, 1, 0]]
    det(B − λI) = λ³ − (28/3)λ² + 27λ − 18      (coincide ✔)
    tr(B) = 28/3 = 9.333333 ,  det(B) = 18
```
