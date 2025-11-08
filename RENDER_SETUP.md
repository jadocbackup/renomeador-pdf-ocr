# 🚀 Deploy no Render - Passo a Passo

## ✅ O Que Você Vai Conseguir

Ao final deste guia, você terá:
- ✅ Aplicação online 24/7
- ✅ URL pública tipo: `https://seu-app.onrender.com`
- ✅ GRÁTIS (plano free do Render)
- ✅ Deploy automático quando atualizar código

---

## 📋 Passo a Passo

### **1️⃣ Criar Conta no Render**

1. Acesse: [https://render.com](https://render.com)
2. Clique em **"Get Started"** ou **"Sign Up"**
3. Escolha: **"Sign up with GitHub"** (recomendado)
4. Autorize o Render a acessar seus repositórios

---

### **2️⃣ Preparar o Código**

**IMPORTANTE**: Antes de fazer deploy, você precisa subir o código para o GitHub.

#### Se você já tem GitHub conectado:
```bash
# No Shell do Replit, execute:
git add .
git commit -m "App completo - Renomeador de PDFs com OCR"
git push
```

#### Se NÃO tem GitHub configurado ainda:

1. **Baixe o projeto do Replit**:
   - Clique nos 3 pontinhos ⋮ no painel de arquivos
   - Escolha "Download as zip"
   - Extraia o arquivo ZIP no seu computador

2. **Crie repositório no GitHub**:
   - Acesse [github.com/new](https://github.com/new)
   - Nome: `renomeador-pdf-ocr` (ou o que preferir)
   - Marque "Add a README file"
   - Clique "Create repository"

3. **Suba os arquivos**:
   - Clique em "uploading an existing file"
   - Arraste todos os arquivos do projeto
   - Clique "Commit changes"

---

### **3️⃣ Criar Web Service no Render**

1. **No Render Dashboard**, clique: **"New +"** → **"Web Service"**

2. **Conecte seu repositório**:
   - Se não aparecer, clique "Configure account" e autorize
   - Selecione: `renomeador-pdf-ocr` (ou nome que você deu)

3. **Configure o serviço**:
   - **Name**: `renomeador-pdf-ocr` (ou o que preferir)
   - **Region**: Oregon (Free) ou qualquer região
   - **Branch**: `main` ou `master`
   - **Root Directory**: deixe vazio
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```
     pip install streamlit pandas PyPDF2 pytesseract pdf2image Pillow PyMuPDF python-dateutil
     ```
   - **Start Command**:
     ```
     streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
     ```

4. **Escolha o plano**:
   - Selecione: **"Free"** (0 USD/mês)
   - ⚠️ Atenção: App pode "dormir" após 15 min sem uso (normal no plano free)

5. **Clique em "Create Web Service"**

---

### **4️⃣ Aguardar Deploy**

Você verá os logs em tempo real:

```
==> Cloning from GitHub...
==> Installing Python dependencies...
==> Building...
==> Starting service...
==> Your service is live 🎉
```

⏱️ **Tempo estimado**: 5-10 minutos no primeiro deploy

---

### **5️⃣ Acessar Sua Aplicação**

Quando terminar, você verá:
- ✅ Status: "Live" (bolinha verde)
- 🌐 URL: `https://renomeador-pdf-ocr.onrender.com`

**Clique na URL e pronto!** Sua aplicação está online! 🎉

---

## ⚠️ Observações Importantes

### **OCR no Render**

O Render **NÃO inclui Tesseract** por padrão. Você tem 2 opções:

#### **Opção A: Usar apenas PyPDF2** (Recomendado para começar)
- Funciona com PDFs digitais (não escaneados)
- Zero configuração adicional
- Deploy mais rápido

#### **Opção B: Instalar Tesseract** (Para PDFs escaneados)

Adicione arquivo `aptfile` no seu repositório:
```
tesseract-ocr
tesseract-ocr-por
poppler-utils
```

E adicione no Build Command:
```
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-por poppler-utils && pip install streamlit pandas PyPDF2 pytesseract pdf2image Pillow PyMuPDF python-dateutil
```

---

## 🆘 Problemas Comuns

### **"Build failed"**
- Verifique se todos os arquivos estão no GitHub
- Confira se o Build Command está correto
- Veja os logs para identificar qual pacote falhou

### **"Application Error"**
- Verifique o Start Command
- Certifique-se que `app.py` existe na raiz
- Veja logs clicando em "Logs" no dashboard

### **"App muito lento"**
- Normal no plano Free
- App "dorme" após 15 min sem uso
- Primeiro acesso após "acordar" leva ~30 segundos

---

## 🎯 Próximos Passos Após Deploy

1. **Teste a aplicação** com alguns PDFs
2. **Compartilhe a URL** com quem precisar
3. **Configure domínio personalizado** (opcional, $1/mês)
4. **Ative auto-deploy** (já vem ativo por padrão)

---

## 💡 Dicas Pro

- **Logs em tempo real**: Clique em "Logs" no dashboard do Render
- **Reiniciar app**: Manual Deploys → "Clear build cache & deploy"
- **Upgrade para pago**: $7/mês = sempre ativo + mais rápido
- **Variáveis de ambiente**: Environment → Add Environment Variable

---

## ✅ Checklist Final

Antes de fazer deploy, certifique-se:
- [ ] Código está no GitHub
- [ ] Arquivo `app.py` existe na raiz
- [ ] Arquivo `core/ocr.py` existe
- [ ] Arquivo `core/parser.py` existe
- [ ] Arquivo `core/batch_manager.py` existe
- [ ] Pasta `data/` existe (será criada automaticamente)

---

**Está pronto?** Siga os passos acima e em 10 minutos seu app estará online! 🚀

Qualquer dúvida, me avise! 😊
