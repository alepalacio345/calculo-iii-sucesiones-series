# Proyecto: Sucesiones y Series — Cálculo III

Implementación en Python del proyecto del PDF `Proyecto Sucesiones y Series.pdf`
(entrega 23/11/2026).

> **Lee primero [`INVESTIGACION.md`](INVESTIGACION.md)**: planteamiento, matemática
> resuelta, entradas/salidas del programa, comparación de frameworks y un hallazgo
> importante sobre la recurrencia (iii).

## Estructura (back-end / front-end separados)

| Ruta | Contenido |
|---|---|
| `main.py` | **punto de entrada** (arranca la interfaz) |
| `backend/sucesiones.py` | **back-end**: toda la matemática (sucesiones, raíces, series, matriz `B`) |
| `backend/graficas.py` | **back-end**: las 7 figuras, sólo matplotlib (sin UI) |
| `frontend/app.py` | **front-end**: interfaz Flet (menú, tablas, figuras, informe) |
| `scripts/` | generación de figuras y números clave |
| `tests/` | prueba de la interfaz sin abrir ventana |
| `salidas/` | figuras PNG ya generadas |

## Ejecutar

```powershell
cd "C:\Users\slara\Documents\calculo III\proyecto"
.\.venv\Scripts\activate

flet run main.py            # ventana nativa (descarga el cliente la 1.ª vez)
flet run --web main.py      # alternativa: en el navegador
```

## Sin interfaz

```powershell
python scripts\generar_figuras.py    # figuras -> salidas/*.png
python scripts\numeros_clave.py      # raíces, radio espectral, formas cerradas
python tests\test_interfaz.py        # comprueba que la UI se construye sin GUI
```

## Documentación del código

El código usa **docstrings** — en Python es el equivalente de Doxygen. Para
generar HTML navegable a partir de ellas (opcional):

```powershell
.\.venv\Scripts\python.exe -m pip install pdoc
.\.venv\Scripts\python.exe -m pdoc backend frontend -o docs
```

(Con `pdoc` no hace falta configurar nada; `Sphinx` es la alternativa más
completa si se quiere un sitio de documentación.)

## Stack

Python 3.12 · Flet 1.1.2 · flet-charts 1.1.2 · matplotlib 3.11 · numpy 2.5
