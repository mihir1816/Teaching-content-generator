# app/services/translate.py

from typing import Optional, List
from deep_translator import GoogleTranslator


def _split_text(text: str, max_len: int = 4999) -> List[str]:
    """Split text into chunks respecting word boundaries."""
    if len(text) <= max_len:
        return [text]
    
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_len = len(word) + 1
        if current_length + word_len > max_len:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_len
        else:
            current_chunk.append(word)
            current_length += word_len
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def translate_to_english(text: str, source_lang: Optional[str] = None) -> str:
    """
    Translate text to English using deep-translator.
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., "hi", "ta") or None for auto-detect
    
    Returns:
        Translated English text
    """
    if not text or not text.strip():
        return text
    
    if source_lang is None or source_lang == "auto":
        source_lang = "auto"
    
    chunks = _split_text(text)
    translator = GoogleTranslator(source=source_lang, target='en')
    
    try:
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return " ".join(translated_chunks).strip()
    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}") from e