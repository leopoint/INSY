@echo off
rem Startet die Weboberflaeche (Doppelklick genuegt). Beenden: dieses Fenster schliessen oder Strg+C.
rem Nimmt Python 3.12 aus dem Benutzerordner, sonst das "python" aus dem PATH.
set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0server.py"
pause
