"""
Paquete `frontend`: interfaz de usuario construida con Flet.

Expone la clase :class:`App` (estado y secciones de la interfaz) y la funcion
:func:`main`, que es el punto de entrada que Flet invoca con la :class:`ft.Page`.
"""

from .app import App, main  # noqa: F401

__all__ = ["App", "main"]
