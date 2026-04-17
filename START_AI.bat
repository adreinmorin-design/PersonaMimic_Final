@echo off
title PersonaMimic AI Orchestrator
color 0B

echo ==========================================================
echo Starting PersonaMimic Full Stack Orchestrator (Ollama + Backend + UI)...
echo ==========================================================
echo.

cd "%~dp0\backend"
python orchestrator.py

pause
