import streamlit as st
import pytesseract
from PIL import Image
import PyPDF2
import fitz  # PyMuPDF
import os
import re
import zipfile
import io
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd

st.set_page_config(
    page_title="Renomeador de PDFs com OCR",
    page_icon="📄",
    layout="wide"
)

# Título principal
st.title("📄 Renomeador de PDFs com OCR")
st.markdown("**Ferramenta para renomear arquivos PDF automaticamente usando OCR**")

# Inicializar session state
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'template_configs' not in st.session_state:
    st.session_state.template_configs = {}
if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []  # Lista de lotes a processar
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = {}  # Resultados de cada lote
if 'processing_batch' not in st.session_state:
    st.session_state.processing_batch = None  # Lote atual sendo processado
if 'paused' not in st.session_state:
    st.session_state.paused = False  # Se o processamento está pausado

# Sidebar - Configurações de Templates
st.sidebar.header("⚙️ Configurações de Templates")

# Tipo de documento
doc_type = st.sidebar.selectbox(
    "Tipo de Documento:",
    ["Notas Fiscais", "Comprovantes de Pagamento", "Processos Judiciais", "Processos de Sinistros", "Personalizado"]
)

# Templates predefinidos
templates = {
    "Notas Fiscais": {
        "padrões": [
            "NF + Número",
            "NF + Número + Data Emissão",
            "NF + Número + Valor",
            "NF + Número + Data + Valor"
        ],
        "regex_patterns": {
            "numero": r"(?:N[FºªOo°]?\.?\s*|Nota\s+Fiscal\s*[Nn][ºªOo°]?\.?\s*|NF\s*)[:\s]*(\d{3,})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})",
            "valor": r"(?:R\$|RS|TOTAL|Valor)\s*[:\s]*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
        }
    },
    "Comprovantes de Pagamento": {
        "padrões": [
            "Fornecedor + Data",
            "Fornecedor + Data + Valor",
            "Data + Valor",
            "Data + Fornecedor + Valor"
        ],
        "regex_patterns": {
            "fornecedor": r"(?:Fornecedor|Beneficiário|Para)[:\s]*([A-ZÀ-Ú][A-Za-zÀ-ú\s]{3,30})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})",
            "valor": r"(?:R\$|RS|Valor)\s*[:\s]*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
        }
    },
    "Processos Judiciais": {
        "padrões": [
            "Processo + Número",
            "Número Processo + Parte",
            "Processo + Número + Data"
        ],
        "regex_patterns": {
            "numero": r"(?:Processo|Proc\.?|N[ºª])[:\s]*(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{10,})",
            "parte": r"(?:Autor|Réu|Requerente)[:\s]*([A-ZÀ-Ú][A-Za-zÀ-ú\s]{3,40})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})"
        }
    },
    "Processos de Sinistros": {
        "padrões": [
            "Sinistro + Número",
            "Sinistro + Número + Data",
            "Número Sinistro + Segurado"
        ],
        "regex_patterns": {
            "numero": r"(?:Sinistro|Sin\.?)[:\s]*(\d{5,})",
            "segurado": r"(?:Segurado|Beneficiário)[:\s]*([A-ZÀ-Ú][A-Za-zÀ-ú\s]{3,40})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})"
        }
    },
    "Personalizado": {
        "padrões": ["Padrão Personalizado"],
        "regex_patterns": {}
    }
}

# Seleção de padrão
if doc_type in templates:
    pattern = st.sidebar.selectbox(
        "Padrão de Renomeação:",
        templates[doc_type]["padrões"]
    )
else:
    pattern = "Padrão Personalizado"

# Configurações para templates personalizados
if doc_type == "Personalizado":
    st.sidebar.markdown("---")
    st.sidebar.subheader("✏️ Configurar Template Personalizado")
    
    # Inicializar configuração personalizada se não existir
    if 'custom_template' not in st.session_state:
        st.session_state.custom_template = {
            'campos': [],
            'regex_patterns': {}
        }
    
    # Adicionar campos personalizados
    st.sidebar.markdown("**Campos para extrair:**")
    
    num_campos = st.sidebar.number_input("Número de campos:", min_value=1, max_value=5, value=1, key="num_campos")
    
    custom_regex_patterns = {}
    custom_fields = []
    
    for i in range(num_campos):
        st.sidebar.markdown(f"**Campo {i+1}:**")
        campo_nome = st.sidebar.text_input(f"Nome do campo {i+1}:", value=f"campo{i+1}", key=f"campo_nome_{i}")
        campo_regex = st.sidebar.text_input(
            f"Regex para {campo_nome}:", 
            value=r"(\d+)",
            key=f"campo_regex_{i}",
            help="Expressão regular para extrair o campo. Use ( ) para captura."
        )
        
        if campo_nome and campo_regex:
            custom_regex_patterns[campo_nome] = campo_regex
            custom_fields.append(campo_nome)
    
    # Definir formato de saída
    st.sidebar.markdown("**Formato de saída:**")
    output_format = st.sidebar.text_input(
        "Formato (use {campo1}, {campo2}, etc.):",
        value="{campo1}",
        key="output_format",
        help="Exemplo: NF_{campo1}_{campo2}"
    )
    
    # Armazenar configuração personalizada
    st.session_state.custom_template = {
        'campos': custom_fields,
        'regex_patterns': custom_regex_patterns,
        'format': output_format
    }

# Configurações personalizadas
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Configurações Avançadas")

# Prefixo e sufixo personalizados
custom_prefix = st.sidebar.text_input("Prefixo personalizado (opcional):", "")
custom_suffix = st.sidebar.text_input("Sufixo personalizado (opcional):", "")

# Separador
separator = st.sidebar.selectbox("Separador:", [" ", "_", "-", "."], index=0)

# Qualidade do OCR
ocr_quality = st.sidebar.select_slider(
    "Qualidade do OCR:",
    options=["Rápido", "Normal", "Alta"],
    value="Normal"
)

# DPI para conversão
dpi_map = {"Rápido": 150, "Normal": 200, "Alta": 300}
dpi = dpi_map[ocr_quality]

# Área principal
st.markdown("---")

# Instruções
with st.expander("ℹ️ Como usar esta ferramenta", expanded=False):
    st.markdown("""
    ### Passo a passo:
    
    1. **Configure o template** na barra lateral:
       - Escolha o tipo de documento
       - Selecione o padrão de renomeação
       - Ajuste as configurações avançadas se necessário
    
    2. **Faça upload dos arquivos PDF**:
       - Arraste e solte múltiplos arquivos
       - Ou clique para selecionar
       - Suporta processamento de vários arquivos simultaneamente
    
    3. **Visualize o preview** dos novos nomes
    
    4. **Processe e baixe** os arquivos renomeados em um arquivo ZIP
    
    ### Tipos de documento suportados:
    - ✅ Notas Fiscais
    - ✅ Comprovantes de Pagamento
    - ✅ Processos Judiciais
    - ✅ Processos de Sinistros
    - ✅ Documentos Personalizados
    """)

# Upload de arquivos
st.subheader("📤 Upload de Arquivos PDF")

col1, col2 = st.columns(2)

with col1:
    uploaded_files = st.file_uploader(
        "Selecione um ou mais arquivos PDF:",
        type=['pdf'],
        accept_multiple_files=True,
        help="Arraste e solte arquivos PDF aqui ou clique para selecionar"
    )

with col2:
    uploaded_zip = st.file_uploader(
        "Ou selecione um arquivo ZIP com PDFs:",
        type=['zip'],
        help="O ZIP será extraído e todos os PDFs serão processados"
    )

# Processar ZIP se fornecido
all_files = []
if uploaded_zip:
    try:
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            # Encontrar todos os PDFs diretamente do ZIP
            pdf_files = []
            for file_info in zip_ref.filelist:
                # Validação de segurança contra Zip Slip
                normalized_path = os.path.normpath(file_info.filename)
                if normalized_path.startswith('..') or os.path.isabs(normalized_path):
                    st.warning(f"⚠️ Arquivo ignorado por motivo de segurança: {file_info.filename}")
                    continue
                
                # Processar apenas PDFs
                if file_info.filename.lower().endswith('.pdf') and not file_info.is_dir():
                    # Extrair apenas o conteúdo do arquivo, sem gravar em disco
                    pdf_content = zip_ref.read(file_info.filename)
                    file_name = os.path.basename(file_info.filename)
                    
                    pdf_files.append({
                        'name': file_name,
                        'content': pdf_content
                    })
            
            if pdf_files:
                st.success(f"✅ {len(pdf_files)} arquivo(s) PDF encontrado(s) no ZIP")
                all_files = pdf_files
            else:
                st.warning("⚠️ Nenhum arquivo PDF encontrado no ZIP")
    except Exception as e:
        st.error(f"❌ Erro ao processar ZIP: {str(e)}")

# Se arquivos individuais foram enviados, usar eles
if uploaded_files and not all_files:
    all_files = [{'name': f.name, 'content': f.read(), 'file_obj': f} for f in uploaded_files]

def extract_text_from_pdf(pdf_content, dpi=100):
    """Extrai texto de um arquivo PDF - primeiro tenta extração direta, depois OCR RÁPIDO se necessário"""
    tmp_path = None
    
    try:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            # Se é bytes, escrever diretamente
            if isinstance(pdf_content, bytes):
                tmp_file.write(pdf_content)
            else:
                # Se é um objeto de arquivo, ler e escrever
                tmp_file.write(pdf_content.read())
            tmp_path = tmp_file.name
        
        # Primeira tentativa: Extrair texto diretamente do PDF (mais rápido, não precisa OCR)
        full_text = ""
        try:
            with open(tmp_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(min(3, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception:
            pass
        
        # Se conseguiu extrair texto suficiente (mais de 50 caracteres), usar ele
        if len(full_text.strip()) > 50:
            return full_text
        
        # Segunda tentativa: Usar OCR RÁPIDO se não conseguiu extrair texto
        try:
            # Abrir PDF com PyMuPDF
            pdf_document = fitz.open(tmp_path)
            
            # Converter APENAS a primeira página com DPI BAIXO (100) para performance máxima
            full_text = ""
            max_pages = min(1, len(pdf_document))  # Apenas 1 página!
            
            for page_num in range(max_pages):
                page = pdf_document[page_num]
                # Converter página para imagem com DPI MUITO BAIXO
                zoom = dpi / 72  # DPI 100 = muito rápido
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Converter pixmap para PIL Image
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                # Aplicar OCR RÁPIDO com configurações otimizadas do Tesseract
                try:
                    # PSM 6 = assume bloco uniforme de texto
                    # --oem 1 = usa LSTM neural network (mais rápido)
                    custom_config = r'--oem 1 --psm 6'
                    text = pytesseract.image_to_string(img, lang='por', config=custom_config)
                    full_text += text + "\n"
                except Exception as ocr_page_error:
                    # Se falhar, continuar
                    continue
            
            pdf_document.close()
            
        except Exception as ocr_error:
            # Se OCR falhar, retornar o texto que foi possível extrair
            if full_text.strip():
                return full_text
            else:
                return f"ERRO OCR: {str(ocr_error)}"
        
        return full_text if full_text.strip() else "ERRO: Nenhum texto extraído"
        
    except Exception as e:
        return f"ERRO: {str(e)}"
    finally:
        # Limpar arquivo temporário se foi criado
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

def extract_field(text, field_name, regex_patterns):
    """Extrai um campo específico do texto usando regex"""
    if field_name not in regex_patterns:
        return ""
    
    pattern = regex_patterns[field_name]
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    
    if match:
        return match.group(1).strip()
    return ""

def clean_filename(filename):
    """Remove caracteres inválidos do nome do arquivo"""
    # Remove caracteres especiais
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove múltiplos espaços
    filename = re.sub(r'\s+', ' ', filename)
    # Remove espaços no início e fim
    filename = filename.strip()
    return filename

def generate_new_filename(text, doc_type, pattern, separator, custom_prefix, custom_suffix, regex_patterns, custom_template=None):
    """Gera o novo nome do arquivo baseado no padrão selecionado"""
    
    parts = []
    
    # Adicionar prefixo personalizado
    if custom_prefix:
        parts.append(custom_prefix)
    
    # Template personalizado
    if doc_type == "Personalizado" and custom_template:
        extracted_values = {}
        for campo in custom_template.get('campos', []):
            value = extract_field(text, campo, custom_template['regex_patterns'])
            extracted_values[campo] = value if value else ""
        
        # Aplicar formato
        output_format = custom_template.get('format', '')
        try:
            formatted_name = output_format.format(**extracted_values)
            if formatted_name and formatted_name != output_format:
                parts.append(formatted_name)
        except (KeyError, ValueError):
            pass
    
    # Gerar nome baseado no tipo de documento e padrão
    elif doc_type == "Notas Fiscais":
        numero = extract_field(text, "numero", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        valor = extract_field(text, "valor", regex_patterns)
        
        if "NF + Número" in pattern:
            if numero:
                parts.append(f"NF{separator}{numero}")
        
        if "Data" in pattern and data:
            data_clean = data.replace("/", "-")
            parts.append(data_clean)
        
        if "Valor" in pattern and valor:
            valor_clean = valor.replace(".", "").replace(",", ".")
            parts.append(f"R${valor_clean}")
    
    elif doc_type == "Comprovantes de Pagamento":
        fornecedor = extract_field(text, "fornecedor", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        valor = extract_field(text, "valor", regex_patterns)
        
        if "Fornecedor" in pattern and fornecedor:
            parts.append(fornecedor[:30])
        
        if "Data" in pattern and data:
            data_clean = data.replace("/", "-")
            parts.append(data_clean)
        
        if "Valor" in pattern and valor:
            valor_clean = valor.replace(".", "").replace(",", ".")
            parts.append(f"R${valor_clean}")
    
    elif doc_type == "Processos Judiciais":
        numero = extract_field(text, "numero", regex_patterns)
        parte = extract_field(text, "parte", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        
        if numero:
            parts.append(f"Processo{separator}{numero}")
        
        if "Parte" in pattern and parte:
            parts.append(parte[:30])
        
        if "Data" in pattern and data:
            data_clean = data.replace("/", "-")
            parts.append(data_clean)
    
    elif doc_type == "Processos de Sinistros":
        numero = extract_field(text, "numero", regex_patterns)
        segurado = extract_field(text, "segurado", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        
        if numero:
            parts.append(f"Sinistro{separator}{numero}")
        
        if "Segurado" in pattern and segurado:
            parts.append(segurado[:30])
        
        if "Data" in pattern and data:
            data_clean = data.replace("/", "-")
            parts.append(data_clean)
    
    # Adicionar sufixo personalizado
    if custom_suffix:
        parts.append(custom_suffix)
    
    # Juntar partes
    if parts:
        new_name = separator.join(parts)
        return clean_filename(new_name)
    
    return None

# Processar arquivos
if all_files:
    st.markdown("---")
    st.subheader("🔍 Processamento e Preview")
    
    # Informação sobre os arquivos
    st.info(f"📋 Total de arquivos para processar: **{len(all_files)}**")
    
    # Botão para processar
    if st.button("🚀 Processar Arquivos", type="primary", use_container_width=True):
        results = []
        
        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        regex_patterns = templates.get(doc_type, {}).get("regex_patterns", {})
        
        # Obter template personalizado se aplicável
        custom_template = None
        if doc_type == "Personalizado" and 'custom_template' in st.session_state:
            custom_template = st.session_state.custom_template
        
        # Contador para nomes duplicados
        used_names = {}
        
        for idx, file_data in enumerate(all_files):
            # Atualizar progresso
            progress = (idx + 1) / len(all_files)
            progress_bar.progress(progress)
            status_text.text(f"Processando {idx + 1}/{len(all_files)}: {file_data['name']}")
            
            try:
                # Extrair texto com DPI MUITO BAIXO para máxima performance (100 DPI, 1 página)
                text = extract_text_from_pdf(file_data['content'], dpi=100)
                
                # Gerar novo nome
                new_name = generate_new_filename(
                    text, doc_type, pattern, separator, 
                    custom_prefix, custom_suffix, regex_patterns, custom_template
                )
                
                # Se não conseguiu gerar nome, usar nome original
                if not new_name:
                    new_name = f"SEM_DADOS_{idx+1}"
                
                # Verificar se nome já existe e adicionar contador se necessário
                base_name = new_name
                counter = 1
                while new_name in used_names:
                    new_name = f"{base_name}_{counter}"
                    counter += 1
                
                # Marcar nome como usado
                used_names[new_name] = True
                
                # Adicionar extensão .pdf
                new_name_with_ext = f"{new_name}.pdf"
                
                results.append({
                    "original": file_data['name'],
                    "novo": new_name_with_ext,
                    "file": file_data['content'],
                    "text_preview": text[:200] if not text.startswith("ERRO") else text
                })
                
            except Exception as e:
                # Erro inesperado - não parar o processamento
                results.append({
                    "original": file_data['name'],
                    "novo": f"ERRO_{idx+1}.pdf",
                    "file": file_data['content'],
                    "text_preview": f"❌ Erro: {str(e)[:100]}"
                })
        
        # Limpar progresso
        progress_bar.empty()
        status_text.empty()
        
        # Armazenar resultados
        st.session_state.processed_files = results
        
        st.success(f"✅ {len(results)} arquivo(s) processado(s) com sucesso!")

# Exibir preview e permitir download
if st.session_state.processed_files:
    st.markdown("---")
    st.subheader("📋 Preview dos Arquivos Renomeados")
    
    # Criar DataFrame para visualização
    df = pd.DataFrame([
        {"#": idx+1, "Nome Original": r["original"], "Novo Nome": r["novo"]}
        for idx, r in enumerate(st.session_state.processed_files)
    ])
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Mostrar preview do texto extraído
    with st.expander("👁️ Ver texto extraído (preview)"):
        for idx, r in enumerate(st.session_state.processed_files):
            st.text_area(
                f"{idx+1}. {r['original']}", 
                r['text_preview'], 
                height=100,
                key=f"preview_{idx}"
            )
    
    # Gerar ZIP para download
    st.markdown("---")
    st.subheader("⬇️ Download dos Arquivos Renomeados")
    
    # Criar ZIP em memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for r in st.session_state.processed_files:
            zip_file.writestr(r['novo'], r['file'])
    
    zip_buffer.seek(0)
    
    # Botão de download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"PDFs_Renomeados_{timestamp}.zip"
    
    st.download_button(
        label="📥 Baixar ZIP com Arquivos Renomeados",
        data=zip_buffer,
        file_name=zip_filename,
        mime="application/zip",
        type="primary",
        use_container_width=True
    )
    
    # Botão para processar novos arquivos
    if st.button("🔄 Processar Novos Arquivos", use_container_width=True):
        st.session_state.processed_files = []
        st.rerun()

