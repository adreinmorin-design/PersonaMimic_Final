@echo off
REM ==========================================================
REM Script: START_N8N.bat
REM Purpose: Bootstrapper for PersonaMimic n8n Automation Engine
REM Author: PersonaMimic
REM Date: 2026-04-22
REM ==========================================================
title PersonaMimic n8n Automation Bootstrapper
color 0D

echo ==========================================================
echo Starting n8n Automation Engine...
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

REM Check for Docker
docker ps >nul 2>&1
if errorlevel 1 goto :no_docker

echo [SUCCESS] Docker is online.
echo Booting n8n container...
call %COMPOSE% -f "%ROOT%docker-compose.yml" up -d n8n
echo.
echo Importing n8n Workflows...
timeout /t 5 /NOBREAK >NUL
call %COMPOSE% -f "%ROOT%docker-compose.yml" exec n8n n8n import:workflow --input /home/node/n8n/industrial_loop.json
call %COMPOSE% -f "%ROOT%docker-compose.yml" exec n8n n8n import:workflow --input /home/node/n8n/industrial_distribution_loop.json
call %COMPOSE% -f "%ROOT%docker-compose.yml" exec n8n n8n import:workflow --input /home/node/n8n/swarm_monitor.json
echo.
SET N8N_PORT=5678
echo n8n is ready at http://localhost:%N8N_PORT%
goto :end

:no_docker
echo [WARNING] Docker is NOT running.
echo Please start Docker Desktop to use the full containerized stack.
echo Attempting to start n8n via NPX (Local Mode)...
echo.
npx -y n8n start
goto :end

:end

pause
EXIT /b 0
