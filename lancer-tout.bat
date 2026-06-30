@echo off
title TechCorp - Lancement complet
cd /d "%~dp0"

echo.
echo ============================================
echo   TECHCORP INDUSTRIES - Hackathon IA
echo ============================================
echo.

docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker Desktop n'est pas demarre.
    echo Ouvre Docker Desktop puis relance ce script.
    pause
    exit /b 1
)

echo [1/3] Demarrage Docker Ollama (INFRA)...
cd infra
docker compose up -d
timeout /t 5 /nobreak >nul

echo [2/3] Verification du modele phi35-financial...
docker exec techcorp-ollama-prod ollama list 2>nul | findstr phi35-financial >nul
if errorlevel 1 (
    echo Telechargement et creation du modele...
    docker exec techcorp-ollama-prod ollama pull phi3.5
    docker exec techcorp-ollama-prod ollama create phi35-financial -f /ollama_server/Modelfile
)

echo [3/3] Lancement interface DEV WEB...
cd ..\devweb
start http://localhost:8501
python -m pip install -r requirements.txt -q
python -m streamlit run app.py
