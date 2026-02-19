@echo off
echo ===========================================
echo   ATUALIZANDO AGENTE ERP PRO VERCEL
echo ===========================================
cd /d "c:\Users\HYPERSOFT\Documents\NOVO_agent_erp"
git add .
git commit -m "Sincronizacao automatica: %date% %time%"
git push
echo.
echo ===========================================
echo   SUCESSO! Deploy iniciado no Vercel.
echo ===========================================
pause
