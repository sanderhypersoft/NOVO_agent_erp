# Guia de Comandos - Agent ERP v2

## 🚀 Inicialização do Sistema

### Opção 1: Inicialização Completa (Recomendado)
Use o script `start_dev.bat` que já está configurado:

```powershell
cd C:\Users\HYPERSOFT\Documents\agent-erp-mvp\agent_erp_v2
.\start_dev.bat
```

Este script irá:
- ✅ Limpar processos antigos na porta 8000
- ✅ Ativar o ambiente virtual (se existir)
- ✅ Verificar dependências
- ✅ Abrir Postman Web
- ✅ Iniciar servidor com uvicorn

### Opção 2: Inicialização Rápida
Use o `quick_start.bat` para iniciar apenas o servidor:

```powershell
cd C:\Users\HYPERSOFT\Documents\agent-erp-mvp\agent_erp_v2
.\quick_start.bat
```

### Opção 3: Manual (Terminal)
```powershell
cd C:\Users\HYPERSOFT\Documents\agent-erp-mvp\agent_erp_v2

# Se tiver venv:
.\venv\Scripts\Activate.ps1

# Iniciar servidor:
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

O servidor será iniciado em: `http://localhost:8000`

---

## 🧪 Testes e Validação

### Executar Testes de Geração SQL
```powershell
python tests\test_sql_generation_revised.py
```

### Executar Teste de Filtros
```powershell
python tests\test_filter_fix.py
```

### Executar Todos os Testes
```powershell
python run_tests.py
```

---

## 🔧 Comandos de Desenvolvimento

### Verificar Estrutura do Dicionário
```powershell
python verify_migration.py
```

### Limpar Cache Python
```powershell
Remove-Item -Recurse -Force __pycache__
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
```

### Reiniciar Ambiente (Hard Reset)
```powershell
.\hard_reset.bat
```

---

## 📊 Comandos Úteis

### Verificar Versão do Python
```powershell
python --version
```

### Listar Pacotes Instalados
```powershell
pip list
```

### Instalar Dependências (se necessário)
```powershell
pip install -r requirements.txt
```

---

## 🔄 Workflow Completo de Inicialização

### Método Recomendado (Mais Simples)
```powershell
cd C:\Users\HYPERSOFT\Documents\agent-erp-mvp\agent_erp_v2
.\start_dev.bat
```

### Método Manual (Passo a Passo)
```powershell
# 1. Navegar para o projeto
cd C:\Users\HYPERSOFT\Documents\agent-erp-mvp\agent_erp_v2

# 2. (Opcional) Ativar ambiente virtual se existir
.\venv\Scripts\Activate.ps1

# 3. (Opcional) Executar testes
python tests\test_sql_generation_revised.py

# 4. Iniciar servidor
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🐛 Troubleshooting

### Erro: "venv não encontrado"
```powershell
# Criar novo ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erro: "Módulo não encontrado"
```powershell
# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "Porta 5000 já em uso"
```powershell
# Encontrar processo usando a porta
netstat -ano | findstr :5000

# Matar processo (substitua PID pelo número encontrado)
taskkill /PID <PID> /F
```

---

## 📝 Notas Importantes

- **Ambiente Virtual**: Sempre ative o `venv` antes de executar comandos Python
- **Diretório Correto**: Certifique-se de estar em `agent-erp-mvp\agent_erp_v2`
- **Testes**: Execute os testes após qualquer alteração no código
- **Logs**: Verifique `test_generation_log.txt` para resultados detalhados dos testes

---

## 🐛 Troubleshooting
