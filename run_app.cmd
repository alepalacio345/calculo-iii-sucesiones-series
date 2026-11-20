@echo off
REM ===========================================================================
REM  Lanzador del proyecto "Sucesiones y Series".
REM
REM  Flet descarga su cliente de escritorio a %USERPROFILE%\.flet y matplotlib
REM  escribe su cache en %LOCALAPPDATA%\matplotlib. En algunos equipos (o bajo
REM  un sandbox) escribir en esas carpetas da "Acceso denegado". Este lanzador
REM  redirige ambas caches DENTRO del proyecto (.cache\), que siempre es
REM  escribible, y luego arranca la ventana nativa.
REM
REM  Uso (desde PowerShell o cmd, en la carpeta del proyecto):
REM      .\run_app.cmd
REM ===========================================================================

setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"

set "USERPROFILE=%ROOT%.cache\home"
set "MPLCONFIGDIR=%ROOT%.cache\mpl"

if not exist "%USERPROFILE%" mkdir "%USERPROFILE%"
if not exist "%MPLCONFIGDIR%" mkdir "%MPLCONFIGDIR%"

"%ROOT%.venv\Scripts\flet.exe" run app.py

endlocal
