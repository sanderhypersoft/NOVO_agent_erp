@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    INICIANDO AMBIENTE AGENT ERP V2
echo ==========================================

:: 0. Limpar processos antigos na porta 8000
echo [LIMPEZA] Verificando processos na porta 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    if not "%%a"=="0" (
        echo [!] Encerrando processo %%a na porta 8000...
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: 1. Ativar VENV se existir
if exist venv\Scripts\activate (
    echo [VENV] Ativando ambiente virtual...
    call venv\Scripts\activate
) else (
    echo [VENV] Ambiente virtual nao encontrado. Usando Python global.
)

:: 1.5 Verificar Dependências (opcional, rápido)
echo [SISTEMA] Verificando dependencias...
pip install fastapi uvicorn pydantic requests >nul 2>&1

:: 2. Abrir o Postman na Web
echo [POSTMAN] Abrindo Postman na Web (https://web.postman.co)...
start https://web.postman.co

:: 3. Iniciar a API e mostrar instruções
echo.
echo ==========================================
echo          INSTRUCOES DE TESTE
echo ==========================================
echo O Agente usa POST. Nao use GET no navegador.
echo Use o Postman ou este comando no terminal:
echo.
echo curl -X POST http://localhost:8000/agent/query ^
echo      -H "Content-Type: application/json" ^
echo      -d "{\"question\": \"Qual o faturamento de hoje?\"}"
echo.
echo ==========================================
echo [API] Iniciando uvicorn...
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
