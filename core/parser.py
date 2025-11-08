"""
Módulo de parsing e extração de dados estruturados de PDFs
"""
import re
from datetime import datetime


# Templates predefinidos para diferentes tipos de documentos
TEMPLATES = {
    "Notas Fiscais": {
        "regex_patterns": {
            "numero": r"(?:N[FºªOo°]?\.?\s*|Nota\s+Fiscal\s*[Nn][ºªOo°]?\.?\s*|NF\s*)[:\s]*(\d{3,})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})",
            "valor": r"(?:R\$|RS|TOTAL|Valor)\s*[:\s]*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
        }
    },
    "Comprovantes de Pagamento": {
        "regex_patterns": {
            "fornecedor": r"(?:Fornecedor|Beneficiário|Para)[:\s]*([A-ZÀ-Ú][A-Za-zÀ-ú\s]{3,30})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})",
            "valor": r"(?:R\$|RS|Valor)\s*[:\s]*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
        }
    },
    "Processos Judiciais": {
        "regex_patterns": {
            "numero": r"(?:Processo|Proc\.?|N[ºª])[:\s]*(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{10,})",
            "parte": r"(?:Autor|Réu|Requerente)[:\s]*([A-ZÀ-Ú][A-Za-zÀ-ú\s]{3,40})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})"
        }
    },
    "Processos de Sinistros": {
        "regex_patterns": {
            "numero": r"(?:Sinistro|Sin\.?)[:\s]*(\d{5,})",
            "segurado": r"(?:Segurado|Beneficiário)[:\s]*([A-ZÀ-Ú][A-Za-zÀ-ú\s]{3,40})",
            "data": r"(\d{2}[/-]\d{2}[/-]\d{4})"
        }
    }
}


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
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', ' ', filename)
    filename = filename.strip()
    return filename


def generate_filename(text, doc_type, pattern, separator="_", prefix="", suffix=""):
    """
    Gera novo nome de arquivo baseado no texto extraído e template
    
    Args:
        text: Texto extraído do PDF
        doc_type: Tipo de documento
        pattern: Padrão de nomenclatura
        separator: Separador entre partes do nome
        prefix: Prefixo personalizado
        suffix: Sufixo personalizado
    
    Returns:
        str: Nome de arquivo gerado (sem extensão)
    """
    parts = []
    
    if prefix:
        parts.append(prefix)
    
    if doc_type not in TEMPLATES:
        return None
    
    regex_patterns = TEMPLATES[doc_type]["regex_patterns"]
    
    # Gerar nome baseado no tipo de documento
    if doc_type == "Notas Fiscais":
        numero = extract_field(text, "numero", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        valor = extract_field(text, "valor", regex_patterns)
        
        if numero:
            parts.append(f"NF{separator}{numero}")
        if "Data" in pattern and data:
            parts.append(data.replace("/", "-"))
        if "Valor" in pattern and valor:
            parts.append(f"R${valor.replace('.', '').replace(',', '.')}")
    
    elif doc_type == "Comprovantes de Pagamento":
        fornecedor = extract_field(text, "fornecedor", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        valor = extract_field(text, "valor", regex_patterns)
        
        if fornecedor:
            parts.append(fornecedor[:30])
        if data:
            parts.append(data.replace("/", "-"))
        if valor:
            parts.append(f"R${valor.replace('.', '').replace(',', '.')}")
    
    elif doc_type == "Processos Judiciais":
        numero = extract_field(text, "numero", regex_patterns)
        parte = extract_field(text, "parte", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        
        if numero:
            parts.append(f"Processo{separator}{numero}")
        if "Parte" in pattern and parte:
            parts.append(parte[:30])
        if "Data" in pattern and data:
            parts.append(data.replace("/", "-"))
    
    elif doc_type == "Processos de Sinistros":
        numero = extract_field(text, "numero", regex_patterns)
        segurado = extract_field(text, "segurado", regex_patterns)
        data = extract_field(text, "data", regex_patterns)
        
        if numero:
            parts.append(f"Sinistro{separator}{numero}")
        if segurado:
            parts.append(segurado[:30])
        if data:
            parts.append(data.replace("/", "-"))
    
    if suffix:
        parts.append(suffix)
    
    if parts:
        new_name = separator.join(parts)
        return clean_filename(new_name)
    
    return None
