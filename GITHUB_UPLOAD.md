# 📤 Como Subir Para o GitHub - Guia Simples

## 🎯 Método Recomendado: Download + Upload Manual

Este é o jeito mais fácil e seguro!

---

## **Passo 1: Baixar o Código do Replit** ⬇️

1. **No Replit**, olhe para o painel de arquivos à esquerda
2. Clique nos **3 pontinhos** `⋮` no topo do painel de arquivos
3. Selecione **"Download as zip"**
4. Salve o arquivo `workspace.zip` no seu computador
5. **Extraia o ZIP** em uma pasta (ex: `renomeador-pdf`)

---

## **Passo 2: Criar Repositório no GitHub** 🆕

1. Acesse: [https://github.com/new](https://github.com/new)
2. **Repository name**: `renomeador-pdf-ocr` (ou o nome que quiser)
3. **Description**: `Renomeador de PDFs com OCR - Sistema de Lotes`
4. Deixe **Public** ✅
5. **NÃO marque** "Add a README file"
6. Clique **"Create repository"**

📝 **Anote a URL do repositório**: `https://github.com/SEU_USUARIO/renomeador-pdf-ocr`

---

## **Passo 3: Subir os Arquivos** ⬆️

Você verá uma página com instruções. Escolha uma opção:

### **Opção A: Upload pela Interface** (Mais Fácil)

1. Na página do seu repositório novo, clique em **"uploading an existing file"**
2. **Arraste TODOS os arquivos** da pasta extraída para a página
   - `app.py`
   - Pasta `core/` (com todos os arquivos dentro)
   - Pasta `.streamlit/`
   - `render.yaml`
   - `RENDER_SETUP.md`
   - Todos os outros arquivos
3. Escreva mensagem: `Código completo da aplicação`
4. Clique **"Commit changes"**

✅ **Pronto!** Arquivos no GitHub!

---

### **Opção B: Via Git Desktop** (Recomendado se souber usar Git)

1. **Baixe GitHub Desktop**: [desktop.github.com](https://desktop.github.com)
2. **Clone o repositório** que você criou
3. **Copie todos os arquivos** da pasta extraída para a pasta do repositório
4. No GitHub Desktop:
   - Escreva mensagem: `Código completo da aplicação`
   - Clique **"Commit to main"**
   - Clique **"Push origin"**

✅ **Pronto!** Arquivos no GitHub!

---

## **Passo 4: Verificar se Subiu Tudo** ✅

No GitHub, verifique se você vê:
- ✅ `app.py`
- ✅ `core/ocr.py`
- ✅ `core/parser.py`
- ✅ `core/batch_manager.py`
- ✅ `.streamlit/config.toml`
- ✅ `render.yaml`
- ✅ `RENDER_SETUP.md`

Se estiver tudo lá, **PERFEITO!** 🎉

---

## **Passo 5: Ir Para o Render** 🚀

Agora que o código está no GitHub, volte para o arquivo **`RENDER_SETUP.md`** e siga a partir do **Passo 3** (Criar Web Service no Render).

---

## 🆘 Problemas?

### "Não consigo baixar do Replit"
- Tente clicar com botão direito no painel de arquivos
- Ou use: Menu → Download Project

### "Não vejo opção de upload no GitHub"
- Certifique-se que está na página do repositório correto
- Procure o link "uploading an existing file"
- Ou simplesmente arraste os arquivos para a página

### "Deu erro ao fazer upload"
- Tente fazer upload de poucos arquivos por vez
- Primeiro: `app.py`
- Depois: pasta `core/` completa
- Por último: restante

---

**Está pronto?** Baixe o código do Replit agora! 📥

Quando terminar o upload no GitHub, me avise que eu ajudo com o Render! 😊
