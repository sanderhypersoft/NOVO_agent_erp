# 🚀 Script de Atualização Universal

Copie e cole os comandos abaixo no seu **Terminal** (PowerShell ou CMD) para subir qualquer alteração para o Vercel:

```powershell
# 1. Entrar na pasta do projeto
cd "c:\Users\HYPERSOFT\Documents\NOVO_agent_erp"

# 2. Preparar arquivos
git add .

# 3. Criar registro da alteração (Com data/hora automática)
git commit -m "Atualização Agente: $(Get-Date -Format 'dd/MM/yyyy HH:mm')"

# 4. Enviar para o GitHub/Vercel
git push
```

---

### 💡 Dica Extra: Atalho Automático
Eu criei um arquivo chamado `atualizar.bat` na sua pasta. 
**Basta dar dois cliques nele** e ele fará todo o processo acima sozinho!
