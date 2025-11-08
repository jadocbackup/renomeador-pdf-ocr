"""
Módulo de OCR otimizado para processamento de PDFs
Usa PyMuPDF + Tesseract com fallback para PyPDF2
"""
import pytesseract
from PIL import Image
import PyPDF2
import fitz  # PyMuPDF
import io
import tempfile
import os


def extract_text_from_pdf(pdf_content, max_pages=2, dpi=150):
    """
    Extrai texto de um PDF usando abordagem híbrida:
    1. Tenta extração direta do texto (PyPDF2) - rápido
    2. Fallback para OCR (Tesseract) se necessário - lento mas funciona em scans
    
    Args:
        pdf_content: Conteúdo do PDF em bytes
        max_pages: Número máximo de páginas para processar (default: 2)
        dpi: Resolução para OCR (default: 150 para velocidade)
    
    Returns:
        str: Texto extraído do PDF
    """
    tmp_path = None
    
    try:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            if isinstance(pdf_content, bytes):
                tmp_file.write(pdf_content)
            else:
                tmp_file.write(pdf_content.read())
            tmp_path = tmp_file.name
        
        # ETAPA 1: Tentar extração direta (mais rápido)
        full_text = ""
        try:
            with open(tmp_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pages_to_read = min(max_pages, len(pdf_reader.pages))
                
                for page_num in range(pages_to_read):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception:
            pass
        
        # Se extraiu texto suficiente, retornar
        if len(full_text.strip()) > 50:
            return full_text
        
        # ETAPA 2: Fallback para OCR (documentos escaneados)
        try:
            pdf_document = fitz.open(tmp_path)
            pages_to_process = min(max_pages, len(pdf_document))
            
            for page_num in range(pages_to_process):
                page = pdf_document[page_num]
                
                # Converter página para imagem
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Converter para PIL Image
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                # Aplicar OCR
                try:
                    custom_config = r'--oem 1 --psm 6'
                    text = pytesseract.image_to_string(img, lang='por', config=custom_config)
                    full_text += text + "\n"
                except Exception:
                    continue
            
            pdf_document.close()
            
        except Exception as ocr_error:
            if full_text.strip():
                return full_text
            else:
                return f"ERRO OCR: {str(ocr_error)}"
        
        return full_text if full_text.strip() else "ERRO: Nenhum texto extraído"
        
    except Exception as e:
        return f"ERRO: {str(e)}"
    finally:
        # Limpar arquivo temporário
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
