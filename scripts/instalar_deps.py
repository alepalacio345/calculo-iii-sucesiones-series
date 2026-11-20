"""
Descarga e instala las dependencias de Flet SIN usar el resolver de pip.

Motivo: con pip 23.2.1 (el que trae el venv), `pip install flet-cli` se queda
"colgado" resolviendo el grafo de dependencias (CPU al 100 %, sin avanzar).
Este script evita ese paso: descarga cada rueda con `--no-deps` (rapido) y luego
instala todo desde el directorio local con `--no-index`.

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\instalar_deps.py

No es necesario en un entorno con pip >= 24 (ahi basta `pip install flet[all]`).
"""

from __future__ import annotations

import email
import glob
import os
import subprocess
import sys
import zipfile

from packaging.markers import Marker
from packaging.requirements import Requirement

WHEELS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".wheels")
os.makedirs(WHEELS, exist_ok=True)

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

# Paquetes que YA estan instalados en el venv (se saltan).
INSTALADOS = {"flet", "flet-charts", "flet-desktop", "msgpack",
              "numpy", "matplotlib", "packaging", "pillow"}

# Semillas: dependencias directas (leidas de la metadata de flet-cli / flet-web / flet).
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
    # extras de uvicorn[standard] (uvloop se salta: solo Linux/macOS)
    "watchfiles",
    "httptools",
    "colorama",
    "python-dotenv",
    "pyyaml",
]


def _nombre(espec: str) -> str:
    return Requirement(espec).name.lower().replace("_", "-")


def _wheel_existente(nombre: str) -> str | None:
    hits = glob.glob(os.path.join(WHEELS, f"{nombre.replace('-', '_')}-*.whl"))
    if not hits:
        hits = glob.glob(os.path.join(WHEELS, f"{nombre.replace('_', '-')}-*.whl"))
    return hits[0] if hits else None


def _descargar(espec: str) -> str:
    """Descarga la rueda (sin dependencias) y devuelve su ruta."""
    nombre = _nombre(espec)
    ya = _wheel_existente(nombre)
    if ya:
        return ya
    subprocess.run(
        [sys.executable, "-m", "pip", "download", "--no-deps", "-d", WHEELS, espec],
        check=True,
        env={**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_PROGRESS_BAR": "off"},
    )
    ruta = _wheel_existente(nombre)
    if not ruta:
        raise RuntimeError(f"No se encontro la rueda de {espec}")
    return ruta


def _requires(ruta: str) -> list[str]:
    with zipfile.ZipFile(ruta) as z:
        meta = next(n for n in z.namelist() if n.endswith(".dist-info/METADATA"))
        msg = email.message_from_bytes(z.read(meta))
        return msg.get_all("Requires-Dist") or []


def main() -> int:
    cola = list(SEMILLAS)
    vistos: set[str] = set()
    ruedas: list[str] = []

    while cola:
        espec = cola.pop(0)
        nombre = _nombre(espec)
        if nombre in vistos or nombre in INSTALADOS:
            continue
        vistos.add(nombre)

        try:
            ruta = _descargar(espec)
        except Exception as exc:  # noqa: BLE001
            print(f"  [error descarga] {espec}: {exc}")
            continue

        ruedas.append(ruta)
        print(f"  ok: {os.path.basename(ruta)}")

        for linea in _requires(ruta):
            try:
                req = Requirement(linea)
            except Exception:  # noqa: BLE001
                continue
            # evaluar marker de entorno (descarta extras no pedidos y SO/version)
            if req.marker and not Marker(str(req.marker)).evaluate(ENV):
                continue
            sub = req.name
            if sub.lower().replace("_", "-") not in vistos:
                cola.append(sub)

    # instalar todo desde las ruedas locales (sin red ni resolver)
    if ruedas:
        print(f"\nInstalando {len(ruedas)} ruedas...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps",
             *[os.path.abspath(r) for r in ruedas]],
            check=True,
        )
    print("Listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
