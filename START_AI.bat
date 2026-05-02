@echo off
title PersonaMimic Studio CLI Orchestrator
color 0B

echo ==========================================================
echo Starting PersonaMimic in STUDIO-CLI Mode (Low Stress)
echo ==========================================================
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

:: Option to run the full stack or just the CLI
set /p mode="Start Full Stack [F] or CLI Only [C]? (Default is C): "

if /i "%mode%"=="F" (
    cd /d "%ROOT%backend"
    uv run python orchestrator.py
) else (
    echo Booting local infrastructure...
    call %COMPOSE% -f "%ROOT%docker-compose.yml" up -d nats redis postgres
    echo.
    echo Launching Studio CLI Interface...
    cd /d "%ROOT%backend"
    uv run python studio_cli.py
)

pause
