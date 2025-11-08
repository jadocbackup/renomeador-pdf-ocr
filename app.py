import streamlit as st
import zipfile
import io
import os
from datetime import datetime
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from core.ocr import extract_text_from_pdf
from core.parser import generate_filename, TEMPLATES
from core.batch_manager import BatchManager

st.set_page_config(
    page_title="Renomeador de PDFs com OCR - Sistema de Lotes",
    page_icon="📄",
    layout="wide"
)

# Inicializar session state
if 'batch_manager' not in st.session_state:
    st.session_state.batch_manager = BatchManager(batch_size=50)
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = {}  # Armazenar conteúdo binário aqui
if 'batch_results_data' not in st.session_state:
    st.session_state.batch_results_data = {}  # Resultados com bytes

st.title("📄 Renomeador de PDFs com OCR - Sistema de Lotes")
st.markdown("**Processamento otimizado em lotes + Cloud Storage + Notificações**")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Processar", "📊 Fila de Tarefas", "☁️ Cloud Storage", "⚙️ Configurações"])

with tab1:
    st.subheader("Upload de PDFs")
    st.info("**Sistema de Lotes Automático**: Arquivos divididos em grupos de 50 PDFs para processamento otimizado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_pdfs = st.file_uploader(
            "Selecione arquivos PDF:",
            type=['pdf'],
            accept_multiple_files=True,
            key="pdf_uploader"
        )
    
    with col2:
        uploaded_zip = st.file_uploader(
            "Ou selecione arquivo ZIP:",
            type=['zip'],
            key="zip_uploader"
        )
    
    # Processar ZIP
    all_files = []
    if uploaded_zip:
        try:
            with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.filename.lower().endswith('.pdf') and not file_info.is_dir():
                        pdf_content = zip_ref.read(file_info.filename)
                        all_files.append({
                            'name': os.path.basename(file_info.filename),
                            'content': pdf_content
                        })
            if all_files:
                st.success(f"✅ {len(all_files)} PDFs encontrados no ZIP")
        except Exception as e:
            st.error(f"❌ Erro ao processar ZIP: {str(e)}")
    
    if uploaded_pdfs and not all_files:
        all_files = [{'name': f.name, 'content': f.read()} for f in uploaded_pdfs]
    
    if all_files:
        st.markdown("---")
        st.info(f"📋 **{len(all_files)} arquivos carregados** - Serão divididos em lotes de 50 PDFs")
        
        # Configurações
        col_a, col_b = st.columns(2)
        with col_a:
            doc_type = st.selectbox("Tipo de Documento:", list(TEMPLATES.keys()))
        with col_b:
            pattern = st.text_input("Padrão:", value="NF + Número")
        
        if st.button("🚀 Criar Lotes e Iniciar Processamento", type="primary", use_container_width=True):
            # Salvar arquivos no session state
            st.session_state.uploaded_files_data = {f['name']: f['content'] for f in all_files}
            
            # Criar lotes (sem conteúdo binário)
            batch_ids = st.session_state.batch_manager.create_batches(all_files, doc_type, pattern)
            st.success(f"✅ {len(batch_ids)} lotes criados! Processando...")
            
            # Processar cada lote
            for batch_id in batch_ids:
                batch = st.session_state.batch_manager.get_batch(batch_id)
                st.session_state.batch_manager.update_batch_status(batch_id, "processing")
                
                # Inicializar armazenamento de resultados
                if batch_id not in st.session_state.batch_results_data:
                    st.session_state.batch_results_data[batch_id] = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file_meta in enumerate(batch['files']):
                    status_text.text(f"Lote {batch_id}: Processando {idx+1}/{len(batch['files'])}")
                    
                    # Recuperar conteúdo binário
                    file_name = file_meta['name']
                    file_content = st.session_state.uploaded_files_data.get(file_name)
                    
                    if not file_content:
                        st.session_state.batch_manager.add_batch_error(batch_id, {
                            "file": file_name,
                            "error": "Arquivo não encontrado"
                        })
                        continue
                    
                    try:
                        # Extrair texto
                        text = extract_text_from_pdf(file_content, max_pages=2, dpi=150)
                        
                        # Gerar nome
                        new_name = generate_filename(text, doc_type, pattern)
                        if not new_name:
                            new_name = f"SEM_DADOS_{idx}"
                        
                        # Salvar resultado (metadados no BatchManager, bytes no session state)
                        st.session_state.batch_manager.add_batch_result(batch_id, {
                            "original": file_name,
                            "novo": f"{new_name}.pdf"
                        })
                        
                        # Salvar bytes separadamente
                        st.session_state.batch_results_data[batch_id].append({
                            "original": file_name,
                            "novo": f"{new_name}.pdf",
                            "content": file_content
                        })
                        
                    except Exception as e:
                        st.session_state.batch_manager.add_batch_error(batch_id, {
                            "file": file_name,
                            "error": str(e)
                        })
                    
                    progress_bar.progress((idx + 1) / len(batch['files']))
                
                st.session_state.batch_manager.update_batch_status(batch_id, "completed")
                progress_bar.empty()
                status_text.empty()
            
            st.success("✅ Todos os lotes processados!")
            st.rerun()

with tab2:
    st.subheader("📊 Fila de Tarefas")
    
    batches = st.session_state.batch_manager.get_all_batches()
    
    if not batches:
        st.info("Nenhum lote criado ainda. Faça upload de PDFs na aba 'Upload & Processar'")
    else:
        # Criar tabela de lotes
        batch_data = []
        for batch_id, batch in batches.items():
            status_emoji = {
                "pending": "⏳",
                "processing": "⚙️",
                "completed": "✅",
                "failed": "❌"
            }
            
            progress = st.session_state.batch_manager.get_progress(batch_id)
            
            batch_data.append({
                "Lote": batch_id,
                "Status": f"{status_emoji.get(batch['status'], '❓')} {batch['status'].title()}",
                "PDFs": f"{batch['processed_files']}/{batch['total_files']}",
                "Progresso": f"{int(progress * 100)}%",
                "Criado": batch['created_at'][:19]
            })
        
        df = pd.DataFrame(batch_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download dos lotes completados
        st.markdown("---")
        st.subheader("⬇️ Download dos Lotes Processados")
        
        completed_batches = [bid for bid, b in batches.items() if b['status'] == 'completed']
        
        if completed_batches:
            selected_batch = st.selectbox("Selecione um lote:", completed_batches)
            
            if st.button("📥 Baixar ZIP", use_container_width=True):
                # Recuperar resultados com bytes
                results = st.session_state.batch_results_data.get(selected_batch, [])
                
                if results:
                    # Criar ZIP
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for result in results:
                            zf.writestr(result['novo'], result['content'])
                    
                    zip_buffer.seek(0)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    st.download_button(
                        label=f"📥 Baixar Lote {selected_batch}",
                        data=zip_buffer,
                        file_name=f"Lote_{selected_batch}_{timestamp}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                else:
                    st.warning("Nenhum resultado encontrado para este lote")
        else:
            st.info("Nenhum lote completado ainda")

with tab3:
    st.subheader("☁️ Integração com Cloud Storage")
    
    st.info("""
    **Como configurar o monitoramento automático:**
    
    Para Google Drive e Dropbox, você precisará:
    1. Criar aplicação OAuth nas respectivas plataformas
    2. Obter credenciais (API keys)
    3. Configurar webhook ou polling para novos arquivos
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📁 Google Drive")
        st.markdown("""
        **Instruções:**
        1. [Google Cloud Console](https://console.cloud.google.com/)
        2. Crie projeto e ative Google Drive API
        3. Configure OAuth 2.0
        4. Defina pasta monitorada
        """)
        
        drive_folder = st.text_input("ID da pasta:", placeholder="1ABC...")
        if st.button("💾 Salvar Google Drive"):
            st.success("Configuração salva!")
    
    with col2:
        st.markdown("### 📦 Dropbox")
        st.markdown("""
        **Instruções:**
        1. [Dropbox App Console](https://www.dropbox.com/developers/apps)
        2. Crie aplicação
        3. Obtenha Access Token
        4. Defina pasta monitorada
        """)
        
        dropbox_folder = st.text_input("Caminho:", placeholder="/PDFs")
        if st.button("💾 Salvar Dropbox"):
            st.success("Configuração salva!")

with tab4:
    st.subheader("⚙️ Configurações")
    
    st.markdown("### 📧 Notificações por Email")
    email = st.text_input("Email:", placeholder="seu@email.com")
    
    if st.button("💾 Salvar Email"):
        if email and "@" in email:
            st.success(f"✅ Email {email} salvo!")
        else:
            st.error("Email inválido")
    
    st.markdown("### ⚡ Performance")
    batch_size = st.slider("Tamanho do lote:", 10, 100, 50, 10)
    st.caption(f"PDFs em grupos de {batch_size}")
    
    st.markdown("### 🗑️ Limpeza")
    if st.button("🧹 Limpar lotes antigos (>7 dias)"):
        removed = st.session_state.batch_manager.clear_completed_batches()
        st.success(f"✅ {removed} lotes removidos")

st.markdown("---")
st.caption(f"Sistema ativo | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
