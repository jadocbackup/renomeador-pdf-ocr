# 📦 Guia de Deployment (Publicação)

## ⚠️ Problema Atual com Replit Deployment

O Replit tem um **bug conhecido** com aplicações Streamlit:
- Streamlit usa porta 5000 para desenvolvimento
- Deployment do Replit espera porta dinâmica ($PORT)
- Há conflito entre as portas mapeadas

**Status**: Aplicação funciona perfeitamente em desenvolvimento, mas deployment tem timeout.

---

## ✅ Soluções Alternativas Recomendadas

### **1. Streamlit Cloud** (MAIS FÁCIL - 100% GRÁTIS)

**Por que escolher:**
- ✅ Feito especificamente para Streamlit
- ✅ 100% gratuito
- ✅ Deploy em 2 minutos
- ✅ Atualizações automáticas
- ✅ Funciona perfeitamente

**Como fazer:**

1. **Preparar repositório Git**:
   ```bash
   git init
   git add .
   git commit -m "App completo de renomeação de PDFs"
   ```

2. **Subir para GitHub**:
   - Crie repositório em [github.com](https://github.com/new)
   - Execute:
     ```bash
     git remote add origin https://github.com/SEU_USUARIO/NOME_REPO.git
     git push -u origin main
     ```

3. **Deploy no Streamlit Cloud**:
   - Acesse [share.streamlit.io](https://share.streamlit.io)
   - Clique "New app"
   - Selecione seu repositório
   - Main file: `app.py`
   - Clique "Deploy"!

**Pronto!** URL pública em 2 minutos: `https://seu-app.streamlit.app`

---

### **2. Render** (CONFIÁVEL - GRÁTIS)

**Por que escolher:**
- ✅ Plano gratuito robusto
- ✅ Suporta aplicações Python
- ✅ Deploy automático do GitHub

**Como fazer:**

1. **Criar `requirements.txt`** (já existe no projeto)

2. **Criar conta em [render.com](https://render.com)**

3. **Novo Web Service**:
   - Conecte GitHub
   - Repository: seu repositório
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

4. **Configurar**:
   - Instance Type: Free
   - Deploy!

**URL pública**: `https://seu-app.onrender.com`

---

### **3. Railway** (MODERNO - $5/mês após créditos grátis)

**Por que escolher:**
- ✅ Interface moderna
- ✅ Deploy super rápido
- ✅ $5 em créditos grátis iniciais

**Como fazer:**

1. **Acesse [railway.app](https://railway.app)**

2. **"New Project"**:
   - Deploy from GitHub
   - Selecione repositório
   - Railway detecta Python automaticamente!

3. **Aguarde deploy** (1-2 minutos)

**URL pública**: `https://seu-app.up.railway.app`

---

## 🔧 Tentativa de Fix para Replit (Experimental)

Criamos o arquivo `deploy.sh` que tenta resolver o problema de porta:

```bash
bash deploy.sh
```

Mas por enquanto, **recomendamos usar Streamlit Cloud** que é:
- ✅ Gratuito
- ✅ Específico para Streamlit
- ✅ Sem problemas de porta
- ✅ Deploy em minutos

---

## 📊 Comparação Rápida

| Plataforma | Custo | Facilidade | Recomendação |
|------------|-------|------------|--------------|
| **Streamlit Cloud** | Grátis | ⭐⭐⭐⭐⭐ | 🥇 **MELHOR** |
| **Render** | Grátis | ⭐⭐⭐⭐ | 🥈 Ótima |
| **Railway** | $5/mês* | ⭐⭐⭐⭐⭐ | 🥉 Boa |
| **Replit** | Variável | ⭐⭐ | ⚠️ Bug atual |

*Railway dá créditos grátis iniciais

---

## 🆘 Precisa de Ajuda?

Se escolher qualquer uma dessas opções, posso ajudar com:
- Criar requirements.txt otimizado
- Configurar variáveis de ambiente
- Resolver problemas de deployment
- Configurar domínio personalizado

Apenas me avise qual plataforma prefere! 🚀
