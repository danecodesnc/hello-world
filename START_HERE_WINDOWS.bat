@echo off
setlocal
cd /d "%~dp0"
title Dane AI Support Portfolio
color 0A

echo.
echo ==========================================================
echo        DANE'S AI SUPPORT PORTFOLIO - ONE CLICK START
echo ==========================================================
echo.
echo You do not need to type any commands.
echo This window will prepare the app and open it in your browser.
echo.

set "PYTHON_CMD="
where py >nul 2>nul
if %errorlevel%==0 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>nul
  if %errorlevel%==0 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  echo Python is not installed yet.
  echo.
  echo A Python download page will open now.
  echo Install Python, then double-click this file again.
  start "" "https://www.python.org/downloads/windows/"
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1 of 3] First-time setup...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto :error
) else (
  echo [1 of 3] Setup already found.
)

echo [2 of 3] Checking required parts...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto :error

echo [3 of 3] Opening the portfolio...
echo.
echo Your browser should open automatically.
echo Keep this green window open while using the portfolio.
echo When you are finished, close this window.
echo.
".venv\Scripts\python.exe" -m streamlit run app.py --server.headless false --browser.gatherUsageStats false
exit /b 0

:error
color 0C
echo.
echo ==========================================================
echo Something did not start correctly.
echo ==========================================================
echo.
echo Nothing was damaged. Please take a screenshot of this window.
echo.
pause
exit /b 1
