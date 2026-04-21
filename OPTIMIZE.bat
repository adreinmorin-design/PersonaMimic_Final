@echo off
REM ==============================================================================
REM PERSONA-MIMIC INDUSTRIAL CORE (PICO) BOOTSTRAPPER
REM ==============================================================================
title PERSONA-MIMIC :: INDUSTRIAL CORE :: PICO v2.0
mode con: cols=100 lines=30
color 0B

echo.
echo    P E R S O N A  -  M I M I C
echo    [ INDUSTRIAL CORE OPTIMIZER ]
echo.
echo    [SYSTEM] Initializing PICO v2.0 Protocol...
echo    [SYSTEM] Targeting: Hardware Acceleration ^| Storage Purge ^| Neural Sync
echo.

REM Check for admin privileges and self-elevate if needed
net session >nul 2>&1
if "%ERRORLEVEL%" NEQ "0" (
    echo    [SYSTEM] Requesting Industrial Administrative Privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
echo    [STATUS] Administrator: VALIDATED

echo.
echo    [WARNING] This will terminate all active PersonaMimic agents and dev processes.
set /p confirm="   [CONFIRM] Execute Full Synchronization? (Y/N): "
if /i "%confirm%" NEQ "Y" (
    echo.
    echo    [ABORT] Protocol terminated by user.
    timeout /t 3 /nobreak > nul
    exit /b
)

echo.
echo    [LAUNCHING] Handing over to PICO PowerShell Engine...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0OPTIMIZE_PC.ps1"

if "%ERRORLEVEL%" NEQ "0" (
    echo.
    echo    [CRITICAL] PICO Engine encountered an error.
    pause
)

exit /b
