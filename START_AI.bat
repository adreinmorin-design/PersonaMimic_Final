@echo off
title PersonaMimic Studio CLI Orchestrator
color 0B

echo ==========================================================
echo Starting PersonaMimic in STUDIO-CLI Mode (Low Stress)
echo ==========================================================
echo.

cd "%~dp0\backend"

:: Option to run the full stack or just the CLI
set /p mode="Start Full Stack [F] or CLI Only [C]? (Default is C): "

if /i "%mode%"=="F" (
    uv run python orchestrator.py
) else (
    echo Booting local infrastructure...
    docker-compose up -d nats redis postgres
    echo.
    echo Launching Studio CLI Interface...
    uv run python studio_cli.py
)

pause
