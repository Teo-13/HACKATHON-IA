@echo off
echo === TechCorp INFRA - Ollama local (sans Docker) ===
echo.
cd /d "%~dp0"
ollama create phi35-financial -f ollama_server\Modelfile 2>nul
ollama list
echo.
echo Ollama pret sur http://localhost:11434
echo Modele: phi35-financial
pause
