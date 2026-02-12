@echo off
echo ==========================================
echo    HARD RESET: AGENT ERP V2
echo ==========================================

echo [1/4] Finalizando TODOS os processos Python...
taskkill /F /IM python.exe /T >nul 2>&1

echo [2/4] Limpando cache do Windows...
del /s /q *.pyc >nul 2>&1
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" >nul 2>&1

echo [3/4] Verificando se a porta 8000 esta livre...
timeout /t 2 /nobreak >nul

echo [4/4] Iniciando API Limpa...
echo.
echo ==========================================
echo ABRINDO API... (Aguarde a janela de comando)
echo ==========================================
start "AGENT_ERP_V2_FINAL" uvicorn api:app --host 0.0.0.0 --port 8000 --no-reload
echo.
echo API iniciada em uma nova janela.
echo Agora tente o Postman novamente.
pause
