# Cómo ejecutar el proyecto (guía rápida)

Esta guía es para que cualquier persona (por ejemplo, un compañero de equipo) pueda
ejecutar el proyecto en su computadora, paso a paso.

---

## 1. Qué necesitas

* **Python 3.10 o superior** instalado.
  * Descárgalo de https://python.org (botón "Download Python").
  * **Importante:** al instalarlo, marca la casilla **"Add python.exe to PATH"**.
  * Para comprobarlo, abre una terminal (cmd o PowerShell) y escribe:
    ```powershell
    python --version
    ```
    Debe mostrar algo como `Python 3.12.x`.

* Los archivos del proyecto (esta carpeta).

---

## 2. Instalar (solo la primera vez)

Abre una terminal **dentro de la carpeta del proyecto** y ejecuta:

```powershell
setup.cmd
```

(o, en PowerShell: `.\setup.cmd`)

Ese comando:

1. Crea el entorno virtual `.venv` (una copia aislada de Python para el proyecto).
2. Instala las dependencias (`numpy`, `matplotlib`, `fastapi`, `uvicorn`, `jinja2`).

Cuando termine verás "Todo listo".

> Si prefieres hacerlo a mano:
> ```powershell
> python -m venv .venv
> .venv\Scripts\python.exe -m pip install -r requirements.txt
> ```

---

## 3. Ejecutar el programa

En la misma carpeta:

```powershell
run_web.cmd
```

(o en PowerShell: `.\run_web.cmd`)

Verás algo como:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Ahora abre tu navegador y ve a:

### **http://127.0.0.1:8000**

---

## 4. Qué verás en la página

Una barra lateral con 6 secciones:

| Sección | Qué muestra |
|---|---|
| **Resumen** | El problema, el término general y la figura de los triángulos |
| **Sucesiones** | Las 4 sucesiones (gráficas) + tabla comparativa |
| **Diferencias** | El índice `n₀` y las diferencias `Tₙ − rₙ/pₙ/qₙ` |
| **Serie y áreas** | `S = ΣTₙ = 1/2` y las áreas descartadas `Dₙ` |
| **Matriz y espectro** | La matriz `B`, sus autovalores y el radio espectral `ρ(B)` |
| **Informe** | El análisis escrito (para el documento final) |

Arriba a la izquierda puedes cambiar:
* **Iteraciones** (n máx., de 5 a 60) → escribe un número y pulsa **Actualizar**.
* **Recurrencia (iii)** → "Impresa (−27, +18)" o "Corregida (−21, +6)".

---

## 5. Detener el servidor

En la terminal donde corre `run_web.cmd`, pulsa `Ctrl + C`.

---

## 6. Problemas comunes

* **"python no es reconocido..."** → Python no está en el PATH. Reinstálalo marcando
  "Add python.exe to PATH", o usa la ruta completa.
* **"No module named ..."** → ejecuta `setup.cmd` de nuevo para instalar las
  dependencias.
* **El puerto 8000 está ocupado** → edita `run_web.cmd` y cambia `--port 8000` por
  otro (por ejemplo 8001), luego abre `http://127.0.0.1:8001`.
* **No se ve la página** → revisa que el servidor siga corriendo en la terminal (no la
  cierres mientras usas la página).

---

## 7. Generar las figuras del informe (opcional)

Si quieres las figuras como archivos PNG (ya están en la carpeta `salidas/`):

```powershell
.venv\Scripts\python.exe scripts\generar_figuras.py
```
