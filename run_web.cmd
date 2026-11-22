@echo off
REM ===========================================================================
REM  Lanzador de la version WEB del proyecto (HTML/CSS + Python, sin JavaScript).
REM  Abre el servidor en http://127.0.0.1:8000
REM ===========================================================================

setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"

set "MPLCONFIGDIR=%ROOT%.cache\mpl"
if not exist "%MPLCONFIGDIR%" mkdir "%MPLCONFIGDIR%"

"%ROOT%.venv\Scripts\python.exe" -m uvicorn web.web_app:app --host 127.0.0.1 --port 8000

endlocal
