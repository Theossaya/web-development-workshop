@echo off
rem ===========================================================================
rem  Workshop decks - local server
rem
rem  Double-click this file. It serves this folder on port 8000, to this
rem  machine and to anything else on the same wifi.
rem
rem  You do NOT need this to present. Double-clicking a deck works on its own.
rem  Use this when you want the class on their own laptops with no internet,
rem  or when you want team scores to persist between refreshes.
rem
rem  Close the black window (or press Ctrl+C) to stop it.
rem ===========================================================================

setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo   Python was not found on this machine.
  echo   Either install it from python.org, or just double-click a deck
  echo   file instead - no server is needed to present.
  echo.
  pause
  exit /b 1
)

rem Pick the adapter that actually has a default gateway, so we report the
rem real wifi address rather than a virtual one.
set IP=
for /f "delims=" %%i in ('powershell -NoProfile -Command "(Get-NetIPConfiguration ^| Where-Object { $_.IPv4DefaultGateway -ne $null } ^| Select-Object -First 1).IPv4Address.IPAddress"') do set IP=%%i
if "%IP%"=="" set IP=your-ip-here

echo.
echo   ============================================================
echo     Workshop decks are being served. Leave this window open.
echo   ============================================================
echo.
echo     On this laptop:        http://localhost:8000/
echo     On the class wifi:     http://%IP%:8000/
echo.
echo     HTML/CSS, session 1:   /session-1.html
echo     HTML/CSS, everything:  /workshop.html
echo     JavaScript, 5 hours:   /javascript/js-workshop.html
echo.
echo     Example for students:
echo       http://%IP%:8000/javascript/js-workshop.html
echo.
echo     Windows may ask to allow Python through the firewall the first
echo     time. Say yes for Private networks, or students cannot connect.
echo.
echo     Press Ctrl+C to stop.
echo.

python -m http.server 8000 --bind 0.0.0.0
