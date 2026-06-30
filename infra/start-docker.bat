@echo off
cd /d "%~dp0"

echo === TechCorp INFRA - Docker Ollama ===
echo.

docker ps >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Docker Desktop n'est pas demarre.
    echo 1. Ouvre Docker Desktop
    echo 2. Relance ce script
    pause
    exit /b 1
)

echo Demarrage du conteneur Ollama sur le port 11434...
docker compose up -d

echo.
echo Attente du serveur...
timeout /t 5 /nobreak >nul

echo Creation du modele phi35-financial...
docker exec techcorp-ollama-prod ollama pull phi3.5
docker exec techcorp-ollama-prod ollama create phi35-financial -f /ollama_server/Modelfile

echo.
echo OK - Serveur pret sur http://localhost:11434
echo Modele: phi35-financial
echo.
echo Lance l'interface DEV WEB:
echo   cd ..\devweb
echo   python -m streamlit run app.py
pause
