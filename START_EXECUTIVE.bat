@echo off
title PersonaMimic Studio - EXECUTIVE BRIDGE (12-Core Optimized)
color 0B

echo ==========================================================
echo Starting PersonaMimic in EXECUTIVE MODE
echo ==========================================================
echo [HARDWARE] Detected: High-Performance CPU (Ryzen 9 5900X)
echo [HARDWARE] Detected: AMD Radeon RX 6700 XT (12GB VRAM)
echo.

set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Prefer Docker Compose v2 ("docker compose"), but fall back to legacy docker-compose if needed
docker compose version >nul 2>&1
if errorlevel 1 (
    set "COMPOSE=docker-compose"
) else (
    set "COMPOSE=docker compose"
)

:: Ask user for Power Mode or Lite Mode
set /p mode="Use [P]ower Mode (3 Brains) or [L]ite Mode (2 Brains)? (Default is P): "

if /i "%mode%"=="L" (
    echo [STATUS] Mode: High-Quality Sequential (Lite)
    set STUDIO_LITE_MODE=1
    set STUDIO_POWER_MODE=0
) else (
    echo [STATUS] Mode: 12-Core Optimized (Power)
    set STUDIO_LITE_MODE=0
    set STUDIO_POWER_MODE=1
)

echo.
echo [INFRA] Using Industrial Docker Stack (Postgres/Redis/NATS)
echo [INFRA] Bypassing Frontend UI (Using High-Performance CLI Bridge)
echo.

:: Ensure Docker Infrastructure is UP
echo Synchronizing Docker services...
call %COMPOSE% -f "%ROOT%docker-compose.yml" up -d nats redis postgres
echo Waiting for Neural Infrastructure to stabilize (10s)...
timeout /t 10 /nobreak > nul

:: Launch the High-Quality CLI Bridge
echo Booting Executive Industrial Bridge via uv...
cd /d "%ROOT%backend"
if "%STUDIO_LITE_MODE%"=="1" (
    uv run python studio_cli.py --lite
) else (
    uv run python studio_cli.py --power
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Studio failed to boot.
    pause
)

echo.
echo Executive session terminated.
pause
