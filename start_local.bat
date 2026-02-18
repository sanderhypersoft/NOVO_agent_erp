@echo off
echo ===========================================
echo   INICIANDO AGENTE ERP V2 (MODO LOCAL)
echo   Conectando ao Firebird Real...
echo ===========================================

:: Ativar VENV
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)

:: Instalar Driver Firebird
echo [1/2] Verificando fdb driver...
pip install fdb==2.0.4 -q

:: Iniciar Servidor
echo [2/2] Iniciando API em http://localhost:8000
echo Pressione CTRL+C para parar.
uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
