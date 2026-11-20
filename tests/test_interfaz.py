"""Prueba headless: construye el arbol de controles de todas las secciones."""
import os
import sys
import traceback

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import flet as ft  # noqa: E402

from frontend import app as appmod  # noqa: E402

fallos = 0


def prueba(nombre, fn):
    global fallos
    try:
        c = fn()
        n = 1 if not isinstance(c, list) else len(c)
        print("OK   %-30s -> %s control(es)" % (nombre, n))
    except Exception:
        fallos += 1
        print("FALLA %-29s" % nombre)
        traceback.print_exc()


a = appmod.App.__new__(appmod.App)
a.N = 30
a.modelo = "impreso"
a.relativa = False
a.seccion = "resumen"
a.menu = ft.Column(spacing=4, width=196)
a.lbl_n = ft.Text("30")
a.contenido = ft.Column()

# barra superior y menu (no requieren Page)
prueba("barra superior", lambda: a._barra_superior())
prueba("menu lateral", lambda: (a._construir_menu(), a.menu.controls)[1])

for seccion in [s[0] for s in appmod.App.SECCIONES]:
    a.seccion = seccion
    for modelo in ("impreso", "corregido"):
        a.modelo = modelo
        d, info = a._datos()
        metodo = {
            "resumen": a._sec_resumen,
            "sucesiones": a._sec_sucesiones,
            "diferencias": a._sec_diferencias,
            "serie": a._sec_serie,
            "matriz": a._sec_matriz,
            "informe": a._sec_informe,
        }[seccion]
        prueba("seccion %s (%s)" % (seccion, modelo), lambda m=metodo: m(d, info))

# valores extremos de n: TODAS las secciones (el resumen indexa T_n y
# rompia con N < 30 si no se acota).
metodos = {
    "resumen": a._sec_resumen,
    "sucesiones": a._sec_sucesiones,
    "diferencias": a._sec_diferencias,
    "serie": a._sec_serie,
    "matriz": a._sec_matriz,
    "informe": a._sec_informe,
}
for n in (5, 60):
    a.N = n
    a.modelo = "impreso"
    d, info = a._datos()
    for seccion, metodo in metodos.items():
        prueba("n=%d %s" % (n, seccion), lambda m=metodo: m(d, info))

# el texto del informe se genera y no esta vacio
d, info = a._datos()
texto = a._texto_informe(d, info)
print("informe: %d caracteres" % len(texto))

print()
print("FALLOS:", fallos)
sys.exit(1 if fallos else 0)
