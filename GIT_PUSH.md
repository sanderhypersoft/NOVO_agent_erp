# Comandos para Atualização (Copiar e Colar)

Para enviar todas as alterações locais para o servidor (Vercel) agora mesmo, abra o terminal e execute:

```powershell
cd "c:\Users\HYPERSOFT\Documents\NOVO_agent_erp"
git add .
git commit -m "Evolução V4: Estabilização do Motor SQL e Mapeamento Real"
git push
.\atualizar.bat
```

> [!NOTE]
> O comando `git push` envia o código para o GitHub/Vercel.
> O script `.\atualizar.bat` é um reforço que você já tem no projeto para garantir a sincronização.
