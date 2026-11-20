"""
Punto de entrada de la aplicacion "Sucesiones y Series".

Arranca la interfaz Flet definida en `frontend/app.py`. Mantener este archivo
minimo: toda la logica de UI vive en `frontend/` y la matematica en `backend/`.

Ejecutar desde la raiz del proyecto:

    flet run app.py            ventana nativa (el cliente se descarga la 1.ª vez)
    flet run --web app.py      en el navegador
    python app.py              equivalente a `flet run` de escritorio
"""

import os

# Evitar el aviso/fallo de matplotlib cuando no se puede escribir en
# %LOCALAPPDATA%\matplotlib (p. ej. bajo un sandbox): usar una caché local.
os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", "mpl"),
)

import flet as ft

from frontend.app import main

if __name__ == "__main__":
    ft.run(main)
