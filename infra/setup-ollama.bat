@echo off
echo ========================================
echo  IMPORTANT: n'utilise PLUS infra\server.py
echo  Utilise Ollama (vrai modele IA)
echo ========================================
echo.
cd /d "%~dp0"
ollama create phi35-financial -f Modelfile 2>nul
ollama list
echo.
echo Ollama pret sur http://localhost:11434
echo Modele: phi35-financial (ou phi3.5)
pause
