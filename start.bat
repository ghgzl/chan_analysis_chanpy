@echo off
title Chan Analysis Web - chan.py Launcher
cd /d "%~dp0"
echo ==========================================
echo    Chan Analysis Web (chan.py) Launcher
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 goto :nopython

if exist ".streamlit\config.toml" goto :deps
if not exist ".streamlit" mkdir ".streamlit"
echo [browser] > ".streamlit\config.toml"
echo gatherUsageStats = false >> ".streamlit\config.toml"
echo. >> ".streamlit\config.toml"
echo [server] >> ".streamlit\config.toml"
echo headless = false >> ".streamlit\config.toml"
echo [1/4] Config file created ^(skip email prompt^).
goto :deps

:nopython
echo [ERROR] Python not found!
echo Please install Python 3.11+ from https://www.python.org/downloads/
echo IMPORTANT: check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:deps
echo [2/4] Checking dependencies...
pip show streamlit >nul 2>nul
if errorlevel 1 goto :install
echo Dependencies already installed.
goto :run

:install
echo Installing dependencies, please wait a few minutes...
python -m pip install -r requirements.txt
if errorlevel 1 goto :installfail
goto :run

:installfail
echo.
echo [ERROR] Dependency install failed. Check your network and retry.
echo.
pause
exit /b 1

:run
echo [3/4] Starting web app...
echo The browser will open automatically once ready.
echo If it does not open, visit http://localhost:8501 manually.
echo Close this window to stop the app.
echo.
echo [4/4] Running...
python -m streamlit run streamlit_app.py
pause
