import re
from typing import List

def sanitize_text(text: str) -> str:
    """
    Limpa e normaliza o texto bruto, removendo caracteres unicode 
    estranhos e excesso de espaços.
    """
    if not text:
        return ""
    # Normalizar bullets comuns para hífen
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\*]\s*', '- ', text)
    # Remover espaços em branco excessivos
    text = re.sub(r'[ \t\r\f\v]+', ' ', text)
    # Colapsar quebras de linha múltiplas
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def truncate_text(text: str, max_words: int) -> str:
    """Corta o texto se exceder max_words e adiciona '...'."""
    if not text or max_words <= 0:
        return text
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

def chunk_list(items: list, chunk_size: int) -> List[list]:
    """Divide uma lista em sub-listas de tamanho chunk_size."""
    if not items:
        return []
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]