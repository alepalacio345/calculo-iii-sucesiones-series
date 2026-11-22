# Proyecto: Sucesiones y Series — Cálculo III

Implementación en Python del proyecto del PDF `Proyecto Sucesiones y Series.pdf`
(entrega 23/11/2026). La interfaz es **web**: HTML + CSS para lo visual y Python
(FastAPI) para la lógica. **Sin JavaScript.**

> Documentos clave:
> [`INFORME.md`](INFORME.md) — el informe del proyecto ·
> [`EXPLICACION_CODIGO.md`](EXPLICACION_CODIGO.md) — explicación del código (para la defensa) ·
> [`COMO_EJECUTAR.md`](COMO_EJECUTAR.md) — guía rápida de instalación y ejecución

## Estructura

| Ruta | Contenido |
|---|---|
| `backend/sucesiones.py` | **back-end**: toda la matemática (sucesiones, raíces, series, matriz `B`) |
| `backend/graficas.py` | **back-end**: las 7 figuras, sólo matplotlib |
| `web/web_app.py` | **servidor**: FastAPI (lee parámetros, calcula y renderiza) |
| `web/templates/index.html` | **front-end**: plantilla HTML (Jinja2) |
| `web/static/style.css` | **front-end**: hoja de estilos |
| `run_web.cmd` | lanzador del servidor |
| `setup.cmd` | instalador (crea el entorno virtual y las dependencias) |
| `scripts/` | figuras y números clave por consola |
| `tests/` | pruebas del back-end |
| `salidas/` | figuras PNG ya generadas |

## Requisitos

- Python 3.10 o superior (en el PATH).
- Dependencias: `numpy`, `matplotlib`, `fastapi`, `uvicorn`, `jinja2` (ver `requirements.txt`).

## Instalación (primera vez)

```powershell
cd "C:\Users\slara\Documents\calculo III\proyecto"
.\setup.cmd
```

`setup.cmd` crea el entorno virtual `.venv` e instala las dependencias.

## Ejecutar

```powershell
.\run_web.cmd
```

Luego abre en el navegador: **http://127.0.0.1:8000**

La página tiene 6 secciones (Resumen, Sucesiones, Diferencias, Serie y áreas, Matriz
y espectro, Informe), un control para el número de iteraciones y otro para elegir la
recurrencia (iii) impresa o corregida.

## Sin interfaz (por consola)

```powershell
.\.venv\Scripts\python.exe scripts\generar_figuras.py    # figuras -> salidas/*.png
.\.venv\Scripts\python.exe scripts\numeros_clave.py      # raíces, radio espectral, n0
.\.venv\Scripts\python.exe tests\test_backend.py         # pruebas del back-end
```

## Stack

Python 3.12 · FastAPI · Uvicorn · Jinja2 (HTML/CSS) · matplotlib · numpy
