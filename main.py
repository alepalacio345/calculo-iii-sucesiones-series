"""
Punto de entrada de la aplicacion "Sucesiones y Series".

Arranca la interfaz Flet definida en `frontend/app.py`. Mantener este archivo
minimo: toda la logica de UI vive en `frontend/` y la matematica en `backend/`.

Ejecutar desde la raiz del proyecto:

    flet run main.py            ventana nativa (el cliente se descarga la 1.ª vez)
    flet run --web main.py      en el navegador
    python main.py              equivalente a `flet run` de escritorio
"""

import flet as ft

from frontend.app import main

if __name__ == "__main__":
    ft.run(main)
