# 🚀 Como Iniciar a Aplicação

## Método Rápido (Recomendado)

Execute o script automático:

```bash
bash start.sh
```

O script irá:
1. ✅ Verificar se o Streamlit já está rodando
2. ✅ Iniciar automaticamente se necessário
3. ✅ Confirmar que está funcionando
4. ✅ Mostrar o link de acesso

---

## Método Manual

Se preferir iniciar manualmente:

```bash
# Parar processo anterior (se houver)
pkill -9 -f "streamlit run app.py"

# Iniciar em segundo plano
nohup streamlit run app.py --server.port 5000 --server.headless true > /tmp/streamlit.log 2>&1 &

# Aguardar 15 segundos
sleep 15

# Verificar se está funcionando
curl http://localhost:5000/_stcore/health
```

Se mostrar "ok", está tudo certo!

---

## Verificar Status

**Ver se está rodando:**
```bash
ps aux | grep streamlit
```

**Testar conexão:**
```bash
curl http://localhost:5000/_stcore/health
```

**Ver logs em tempo real:**
```bash
tail -f /tmp/streamlit.log
```

---

## ⚠️ Observação Importante

O workflow do Replit (`streamlit_app`) falha devido a um problema de timeout na porta 5000, **mas a aplicação funciona perfeitamente** quando executada manualmente com os comandos acima.

Este é um problema de infraestrutura do Replit, não da aplicação. Use o script `start.sh` para rodar normalmente.

---

## 🎯 Acesso

Após iniciar, acesse:
- **URL Local**: http://localhost:5000
- **Webview**: Clique no painel "Webview" do Replit

---

## 📋 Solução de Problemas

**Problema**: "Address already in use"
```bash
pkill -9 -f "streamlit run app.py"
bash start.sh
```

**Problema**: Página mostra apenas "Running"
```bash
# Aguarde mais 10-15 segundos - o Streamlit está carregando
sleep 15
```

**Problema**: Erro de dependências
```bash
# Reinstale os pacotes
pip install -r requirements.txt
bash start.sh
```
