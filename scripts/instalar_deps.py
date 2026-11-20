"""
Descarga e instala las dependencias de Flet SIN depender del resolver de pip.

Motivo
    Con pip 23.2.1 (el que trae el venv) `pip install flet-cli` se queda
    colgado resolviendo dependencias y, ademas, `pip download` se ralentiza o
    bloquea con los indices grandes de PyPI. Python (urllib) si responde rapido
    (una peticion al JSON de PyPI tarda <1 s), asi que este script:

        1. descarga cada rueda directamente desde PyPI con urllib,
        2. recorre el grafo de dependencias leyendo ``requires_dist`` del JSON,
        3. instala todo desde las ruedas locales con ``pip --no-index --no-deps``.

Uso
    .\\.venv\\Scripts\\python.exe scripts\\instalar_deps.py

En un entorno con pip >= 24 no hace falta: basta ``pip install 'flet[all]'``.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import urllib.request

from packaging.markers import Marker
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHEELS = os.path.join(RAIZ, ".wheels")
os.makedirs(WHEELS, exist_ok=True)

PY = sys.executable

# Entorno que evalua `packaging` para decidir que markers aplican.
ENV = {
    "python_version": "3.12",
    "python_full_version": "3.12.0",
    "sys_platform": "win32",
    "platform_machine": "AMD64",
    "platform_system": "Windows",
    "os_name": "nt",
    "implementation_name": "cpython",
    "platform_python_implementation": "CPython",
    "extra": "",
}

# Paquetes que YA estan instalados en el venv (no se descargan).
INSTALADOS = {"flet", "flet-charts", "flet-desktop", "msgpack",
              "numpy", "matplotlib", "packaging", "pillow",
              "pyparsing", "python-dateutil", "contourpy", "kiwisolver",
              "cycler", "fonttools", "tzdata"}

# Semillas: dependencias directas de flet-cli / flet-web / flet (1.1.2).
SEMILLAS = [
    "flet-cli==1.1.2",
    "flet-web==1.1.2",
    "flet-platform-assets==1.1.2",
    "watchdog",
    "qrcode",
    "cookiecutter",
    "binaryornot",
    "chardet",
    "rich",
    "fastapi",
    "websockets",
    "uvicorn",
    "oauthlib",
    "repath",
    "httpx",
    # extras de uvicorn[standard] (uvloop es solo Linux/macOS)
    "watchfiles",
    "httptools",
    "colorama",
    "python-dotenv",
    "pyyaml",
]

HEADERS = {"User-Agent": "sucesiones-series/1.0 (+proyecto escolar)"}


def _nombre(espec: str) -> str:
    """Nombre normalizado (minusculas, guiones) de una especificacion."""
    return Requirement(espec).name.lower().replace("_", "-")


def _ya_existe(nombre: str) -> str | None:
    for pat in (nombre, nombre.replace("-", "_")):
        hits = glob.glob(os.path.join(WHEELS, f"{pat}-*.whl"))
        if hits:
            return hits[0]
    return None


def _json(nombre: str) -> dict:
    url = f"https://pypi.org/pypi/{nombre}/json"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def _elegir_rueda(data: dict, pin: str | None) -> dict | None:
    """Elige la mejor rueda para CPython 3.12 / Windows x64."""
    ver = pin or data["info"]["version"]
    files = data.get("releases", {}).get(ver) or []
    ruedas = [f for f in files if f["packagetype"] == "bdist_wheel"]
    if not ruedas:
        return None

    def puntuar(f: dict) -> int:
        fn = f["filename"]
        s = 0
        if "cp312" in fn:
            s += 100
        if "win_amd64" in fn:
            s += 20
        if "none-any" in fn:
            s += 8
        if "abi3" in fn:
            s += 4
        # respetar requires_python
        if f.get("requires_python"):
            try:
                if not SpecifierSet(f["requires_python"]).contains("3.12.0"):
                    s -= 1000
            except Exception:  # noqa: BLE001
                pass
        return s

    ruedas.sort(key=puntuar, reverse=True)
    return ruedas[0] if puntuar(ruedas[0]) > -500 else None


def _procesar(espec: str) -> dict:
    """Descarga la rueda (si falta) y devuelve el JSON de PyPI."""
    nombre = _nombre(espec)
    ya = _ya_existe(nombre)
    data = _json(nombre)
    if ya is None:
        pin = None
        spec = str(Requirement(espec).specifier)
        if spec.startswith("=="):
            pin = spec[2:].split(",")[0]
        rueda = _elegir_rueda(data, pin)
        if rueda is None:
            raise RuntimeError(f"sin rueda para {espec}")
        destino = os.path.join(WHEELS, rueda["filename"])
        req = urllib.request.Request(rueda["url"], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=300) as resp, open(destino, "wb") as fh:
            fh.write(resp.read())
        print(f"  descargado: {rueda['filename']} ({os.path.getsize(destino)//1024} KB)")
    else:
        print(f"  ya estaba: {os.path.basename(ya)}")
    return data


def _descubrir(data: dict, cola: list, vistos: set) -> None:
    """Anade a la cola las dependencias no vistas de ``requires_dist``."""
    for linea in data["info"].get("requires_dist") or []:
        try:
            req = Requirement(linea)
        except Exception:  # noqa: BLE001
            continue
        if req.marker and not Marker(str(req.marker)).evaluate(ENV):
            continue
        clave = req.name.lower().replace("_", "-")
        if clave not in vistos and clave not in INSTALADOS:
            cola.append(clave)


def main() -> int:
    cola: list[str] = list(SEMILLAS)
    vistos: set[str] = set()
    errores: list[str] = []

    while cola:
        espec = cola.pop(0)
        clave = _nombre(espec)
        if clave in vistos or clave in INSTALADOS:
            continue
        vistos.add(clave)
        try:
            data = _procesar(espec)
        except Exception as exc:  # noqa: BLE001
            errores.append(f"{espec}: {exc}")
            print(f"  [error] {espec}: {exc}")
            continue
        _descubrir(data, cola, vistos)

    if errores:
        print("\nErrores:", *errores, sep="\n  - ")

    if errores:
        print("\nErrores:", *errores, sep="\n  - ")

    # Instalar todas las ruedas desde disco (sin red ni resolver)
    ruedas = sorted(glob.glob(os.path.join(WHEELS, "*.whl")))
    print(f"\nInstalando {len(ruedas)} ruedas...")
    subprocess.run(
        [PY, "-m", "pip", "install", "--no-index", "--no-deps",
         *[os.path.abspath(r) for r in ruedas]],
        check=True,
    )
    print("Instalacion completa.")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
