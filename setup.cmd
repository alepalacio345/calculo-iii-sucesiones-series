@echo off
REM ===========================================================================
REM  Configuracion automatica del proyecto "Sucesiones y Series" (version web).
REM
REM  Hace tres cosas:
REM    1. Crea el entorno virtual .venv
REM    2. Instala las dependencias de requirements.txt
REM    3. Deja todo listo para ejecutar .\run_web.cmd
REM
REM  Requisito: tener Python 3.10 o superior instalado y en el PATH.
REM ===========================================================================

setlocal
cd /d "%~dp0"

echo ============================================================
echo   Configurando el proyecto Sucesiones y Series (version web)
echo ============================================================
echo.

REM --- comprobar Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro Python. Instala Python 3.10+ desde https://python.org
    echo         y marca la casilla "Add python.exe to PATH".
    pause
    exit /b 1
)

REM --- 1) entorno virtual ---
if exist ".venv\Scripts\python.exe" (
    echo [1/3] El entorno virtual .venv ya existe; se reutiliza.
) else (
    echo [1/3] Creando entorno virtual .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

REM --- 2) dependencias ---
echo [2/3] Instalando dependencias ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

REM --- 3) listo ---
echo [3/3] Todo listo.
echo.
echo   Para ejecutar:  .\run_web.cmd
echo   Y abrir en el navegador:  http://127.0.0.1:8000
echo.
pause
endlocal
