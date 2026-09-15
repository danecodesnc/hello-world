@echo off
setlocal
cd /d "%~dp0"
title Create Dane AI Support Portfolio Desktop Icon
color 0A

echo.
echo ==========================================================
echo          CREATE DESKTOP ICON - ONE TIME SETUP
echo ==========================================================
echo.
echo This will place a shortcut on your Windows desktop.
echo After that, just double-click the desktop icon anytime.
echo.

set "TARGET=%~dp0START_HERE_WINDOWS.bat"
set "WORKDIR=%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop=[Environment]::GetFolderPath('Desktop'); $ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut((Join-Path $desktop 'Dane AI Support Portfolio.lnk')); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%WORKDIR%'; $s.IconLocation=$env:SystemRoot + '\System32\shell32.dll,220'; $s.Description='Open Dane Edwards Agentic AI Support Portfolio'; $s.Save()"

if errorlevel 1 goto :error

echo Success!
echo.
echo Look on your desktop for:
echo.
echo     Dane AI Support Portfolio
echo.
echo Double-click that icon to start the program.
echo.
pause
exit /b 0

:error
color 0C
echo.
echo The shortcut could not be created automatically.
echo You can still double-click START_HERE_WINDOWS.bat to run the portfolio.
echo.
pause
exit /b 1
