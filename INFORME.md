# Proyecto: Sucesiones y Series

**Curso:** Cálculo III · **Fecha de entrega:** 23/11/2026 · **Modalidad:** grupos de dos

Implementación en **Python** (FastAPI + HTML/CSS + matplotlib + numpy) del proyecto de
subdivisión geométrica de un triángulo equilátero y del análisis numérico de tres
algoritmos recursivos equivalentes. La interfaz es **web** (HTML + CSS, sin JavaScript).

---

## 1. Planteamiento del problema

Se tiene un triángulo equilátero inicial de área `T₀ = 1` (unidad cuadrada). Al ubicar
su **baricentro** y unirlo con los tres vértices, el triángulo queda dividido en **tres
triángulos congruentes**, cada uno con área igual a `1/3` del área anterior. Se
selecciona uno de ellos (`T₁`) y se repite el procedimiento indefinidamente,
generando la colección infinita `{Tₙ}ₙ₌₁^∞`.

---

## 2. Término general de la sucesión (punto 1)

En cada paso el área se multiplica por `1/3`. Como `T₀ = 1`:

```
Tₙ = (1/3)ⁿ = 3⁻ⁿ ,   n = 0, 1, 2, …
```

Se trata de una **sucesión geométrica** de razón `r = 1/3`, con:

```
T₁ = 1/3,  T₂ = 1/9,  T₃ = 1/27, …   y   lim Tₙ = 0
```

En el programa, `Tₙ` se calcula con aritmética **exacta** (`Fraction`) como referencia
limpia para comparar contra las recurrencias numéricas, que sí usan coma flotante.

---

## 3. Análisis numérico y estabilidad de algoritmos (punto 2)

Se comparan tres recurrencias que, *algebraicamente*, deberían producir la misma
sucesión `{Tₙ}`:

| Algoritmo | Recurrencia | Condiciones iniciales |
|---|---|---|
| **(i)** | `rₙ = (1/3) rₙ₋₁` | `r₀ = 0.99997` |
| **(ii)** | `pₙ = (10/3) pₙ₋₁ − pₙ₋₂` | `p₀ = 1`, `p₁ = 0.33334` |
| **(iii)** | `qₙ = (28/3) qₙ₋₁ − 27 qₙ₋₂ + 18 qₙ₋₃` | `q₀ = 1`, `q₁ = 1/3`, `q₂ = 0.11112` |

### 3.1 Polinomios característicos, raíces y radio espectral

La estabilidad de una recurrencia lineal la determinan las raíces de su **polinomio
característico**. Si hay una raíz de módulo mayor que 1, el error de redondeo se
amplifica en cada iteración y la sucesión diverge numéricamente.

| Algoritmo | Polinomio característico | Raíces | `ρ` (radio espectral) | ¿Estable? |
|---|---|---|---|---|
| **(i)** | `λ − 1/3` | `1/3` | **0.333** | ✅ sí |
| **(ii)** | `λ² − (10/3)λ + 1` | `3`, `1/3` | **3** | ❌ no |
| **(iii) impresa** | `λ³ − (28/3)λ² + 27λ − 18` | `4.195163 ± 1.220027i`, `0.943008` | **4.369** | ❌ no |
| **(iii) corregida** | `λ³ − (28/3)λ² + 21λ − 6` | `6`, `3`, `1/3` | **6** | ❌ no |

### 3.2 Forma cerrada y por qué divergen

**(i)** Solo tiene el modo bueno `λ = 1/3`, por lo que

```
rₙ = 0.99997 · 3⁻ⁿ        ⟹   |Tₙ − rₙ| = 3·10⁻⁵ · 3⁻ⁿ  →  0
```

El error absoluto **decrece**; el relativo es constante e igual a `3·10⁻⁵`.

**(ii)** La raíz parásita `λ = 3` provoca que la solución general sea

```
pₙ = A·3ⁿ + B·3⁻ⁿ ,   con A = 2.5·10⁻⁶ ,  B = 0.9999975
```

El coeficiente `A` no es casual: sale de que `p₁ = 0.33334 ≠ 1/3` (una diferencia de
`6.7·10⁻⁶`). El modo `3ⁿ` domina cuando `A·3ⁿ ≈ 3⁻ⁿ`, es decir en `n ≈ 5.87`; por eso
la divergencia se observa en **`n₀ ≈ 6`**, y el error crece como `9ⁿ`.

**(iii)** (versión corregida) tiene raíces `1/3, 3, 6`, de modo que

```
qₙ = 5.229·10⁻⁷·6ⁿ − 1.111·10⁻⁶·3ⁿ + 1.000001·3⁻ⁿ
```

El modo parásito dominante es `6ⁿ`; el cruce ocurre en `n ≈ 5`, con error creciendo
como `18ⁿ`.

### 3.3 Determinación del índice `n₀`

El enunciado pide determinar a partir de qué índice `n₀` se observa convergencia o
divergencia. El criterio usado (defendible y verificable) es **el índice donde el modo
parásito iguala al modo verdadero**:

```
|A_malo|·ρⁿ = |A_bueno|·3⁻ⁿ  ⟹  n* = ln(|A_bueno/A_malo|) / ln(3ρ)
```

| Algoritmo | `n*` teórico | `n₀` empírico (mínimo de `|xₙ|`) |
|---|---|---|
| (i) `rₙ` | — (no diverge) | — |
| (ii) `pₙ` | **5.87** | **6** |
| (iii) corregida | **5.00** | **5** |

El acuerdo entre la predicción teórica y el valor medido (6 ↔ 5.87, 5 ↔ 5.00) es la
justificación que pide la rúbrica.

### 3.4 Diferencias `Tₙ − rₙ`, `Tₙ − pₙ`, `Tₙ − qₙ`

La segunda tabla del programa muestra `|Tₙ − rₙ|`, `|Tₙ − pₙ|`, `|Tₙ − qₙ|` (absolutas
y relativas). Su comportamiento:

* `|Tₙ − rₙ|` → 0 (decrece, error relativo constante `3·10⁻⁵`).
* `|Tₙ − pₙ|` → crece como `9ⁿ` (diverge a partir de `n₀ ≈ 6`).
* `|Tₙ − qₙ|` → crece como `18ⁿ` (versión corregida) o `4.37ⁿ` (impresa).

La figura `03_diferencias_abs.png` incluye además `|Tₙ − xₙ|^(1/n)`, que tiende al
autovalor dominante `|λ|` de cada recurrencia (1/3, 3 y 4.37), conectando
empíricamente las diferencias con el radio espectral.

### 3.5 Análisis crítico

* **Converge a cero:** `|Tₙ − rₙ|`, porque la recurrencia (i) solo tiene la raíz `1/3`
  (módulo < 1); el error no se amplifica.
* **Diverge:** `|Tₙ − pₙ|` (raíz parásita `3`) y `|Tₙ − qₙ|` (raíces parásitas `3` y `6`,
  o `4.195 ± 1.22i` en la versión impresa). El redondeo de las condiciones iniciales
  excita esos modos, que crecen geométricamente y destruyen la convergencia.

### 3.6 Hallazgo importante: la recurrencia (iii) impresa no genera `Tₙ`

El enunciado afirma que las tres recurrencias son algebraicamente equivalentes a
`Tₙ = 3⁻ⁿ`. Sin embargo, el polinomio **impreso** de (iii) no tiene a `1/3` como raíz:

```
P(λ) = λ³ − (28/3)λ² + 27λ − 18
P(1/3) = 1/27 − 28/27 + 9 − 18 = −10 ≠ 0
```

y la propia recurrencia da `q₃ = 10.037` frente a `T₃ = 0.037`. El coeficiente `28/3`
delata la intención: corresponde a las raíces `1/3, 3, 6`, es decir los coeficientes
correctos son **`−21` y `+6`** en vez de `−27` y `+18`:

```
(λ − 1/3)(λ − 3)(λ − 6) = λ³ − (28/3)λ² + 21λ − 6
```

El programa implementa **ambas** versiones (impresa y corregida), con un selector en
la interfaz, y documenta esta discrepancia como observación crítica.

---

## 4. Serie infinita asociada (punto 3)

La suma de las áreas de **todos** los triángulos conservados (desde la primera
partición) es una serie geométrica de razón `1/3`:

```
S = Σₙ₌₁^∞ Tₙ = Σₙ₌₁^∞ 3⁻ⁿ = (1/3)/(1 − 1/3) = 1/2
```

**Interpretación geométrica:** la suma de las áreas de todos los triángulos
conservados es exactamente **la mitad** del área del triángulo original. Como cada
triángulo conservado se vuelve a partir en el paso siguiente, esas áreas se solapan
en el tiempo; la mitad restante la conforman las áreas descartadas (sección 5).

---

## 5. Extensión: área acumulada de regiones descartadas (punto 4)

En cada paso se conserva una parte (`Tₙ`) y se descartan **dos** de las tres partes
iguales. El área combinada descartada en el paso `n` es

```
Dₙ = 2·Tₙ = 2·3⁻ⁿ ,   n = 1, 2, 3, …
```

La suma de todas las áreas descartadas es

```
Σₙ₌₁^∞ Dₙ = 2 · Σₙ₌₁^∞ 3⁻ⁿ = 2 · (1/2) = 1 = T₀   ∎
```

**Demostración por sumas parciales** (la forma que cierra el problema): tras `N` pasos
se ha descartado

```
Σₖ₌₁^N Dₖ = 2·(1/3 + 1/9 + ⋯ + 3⁻ᴺ) = 1 − 3⁻ᴺ
```

y queda el triángulo `T_N = 3⁻ᴺ`. La suma es `1` para todo `N`, de modo que en el
límite lo descartado agota exactamente el área original y el triángulo límite tiene
área `lim Tₙ = 0`.

---

## 6. Enfoque matricial y análisis espectral (punto 5)

La recurrencia de tercer orden se reescribe como sistema de primer orden
`Xₙ = B Xₙ₋₁` con el vector de estado

```
Xₙ = [qₙ, qₙ₋₁, qₙ₋₂]ᵀ
```

y la **matriz compañera**

```
        ⎡ 28/3  −27   18 ⎤
B  =    ⎢  1      0    0 ⎥        (versión impresa; con la corrección: −21 y 6)
        ⎣  0      1    0 ⎦
```

### 6.1 Polinomio característico

```
P(λ) = det(B − λI) = λ³ − (28/3)λ² + 27λ − 18 = 0
```

Por la propiedad de la matriz compañera, `det(B − λI)` **coincide exactamente** con el
polinomio característico de la recurrencia. El programa lo comprueba con `numpy.poly(B)`
y verifica la coincidencia (además `tr(B) = 28/3` y `det(B) = 18`).

### 6.2 Autovalores y radio espectral

Con `numpy.linalg.eig(B)`:

* **Versión impresa:** `λ₁,₂ = 4.195163 ± 1.220027i`, `λ₃ = 0.943008`, con
  `ρ(B) = max|λᵢ| = 4.368965`.
* **Versión corregida:** `λ = 6, 3, 1/3`, con `ρ(B) = 6`.

### 6.3 Justificación de la divergencia

Como `‖Xₙ‖ ~ ρ(B)ⁿ`, cualquier error de redondeo introducido en un paso se multiplica
por `ρ` en cada iteración. Con `ρ > 1` el error crece geométricamente y acaba tapando
la solución (por ejemplo, `6²⁰ ≈ 3.7·10¹⁵`). La estabilidad del algoritmo queda por
tanto **caracterizada por el radio espectral**: es el puente entre la recurrencia
algebraica y el comportamiento numérico observado en las gráficas. Las raíces
complejas de la versión impresa, además, producen un cambio de signo observable en
`q₂₀ = −3.59·10¹²`.

---

## 7. Conclusiones

1. La sucesión `Tₙ = 3⁻ⁿ` converge a 0 y la serie converge a `1/2`; las áreas
   descartadas suman `1 = T₀`.
2. **El algoritmo importa:** la misma relación algebraica, reescrita como recurrencia
   de orden superior, introduce raíces espurias de módulo mayor que 1 que destruyen la
   convergencia numérica.
3. La estabilidad queda caracterizada por el radio espectral de la matriz compañera.
4. El programa permite **reproducir** todo lo anterior de forma interactiva: tablas,
   gráficas, `n₀`, diferencias, serie, áreas descartadas y espectro de `B`.

---

## Anexo A. Números clave (para citar en la defensa)

```
Tₙ = 3⁻ⁿ

(i)  rₙ = 0.99997·3⁻ⁿ ; |Tₙ − rₙ| = 3·10⁻⁵·3⁻ⁿ ; λ = 1/3 ; ρ = 0.3333  → estable
(ii) λ² − (10/3)λ + 1 = 0 ; λ = 3, 1/3 ; ρ = 3 ; n₀ ≈ 6 (n* = 5.87)
     pₙ = 2.5·10⁻⁶·3ⁿ + 0.9999975·3⁻ⁿ
(iii) impresa: λ³ − (28/3)λ² + 27λ − 18 = 0 ; λ = 4.195163 ± 1.220027i, 0.943008 ; ρ = 4.368965
      P(1/3) = −10 ; q₃ = 10.037 (≠ T₃ = 0.037)
(iii) corregida: λ³ − (28/3)λ² + 21λ − 6 = 0 ; λ = 6, 3, 1/3 ; ρ = 6 ; n₀ ≈ 5 (n* = 5.00)

S  = Σₙ₌₁^∞ Tₙ = 1/2
Dₙ = 2·3⁻ⁿ ; Σₖ₌₁^N Dₖ = 1 − 3⁻ᴺ ; Σₙ₌₁^∞ Dₙ = 1 = T₀

B = [[28/3, −27, 18], [1, 0, 0], [0, 1, 0]]
    det(B − λI) = λ³ − (28/3)λ² + 27λ − 18  (coincide con la recurrencia ✔)
    tr(B) = 28/3 = 9.333333 ; det(B) = 18
```

## Anexo B. Cómo ejecutar el programa

```powershell
cd "C:\Users\slara\Documents\calculo III\proyecto"

.\run_web.cmd              # arranca el servidor web; abrir http://127.0.0.1:8000
python scripts\generar_figuras.py    # figuras -> salidas/*.png
```

La interfaz es una **página web** servida por Python (FastAPI): HTML + CSS para lo
visual, Python para la matemática, y las gráficas se incrustan como imágenes PNG.
