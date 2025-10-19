# app/services/translate.py

from typing import Optional, List
import time


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


def translate_to_english(text: str, source_lang: Optional[str] = None, max_retries: int = 3) -> str:
    """
    Translate text to English using translators library with multiple backend fallback.
    Automatically tries: Google → Bing → Yandex → Baidu (whichever works!)
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., "hi", "ta") or "auto" for auto-detect
        max_retries: Maximum number of retry attempts
    
    Returns:
        Translated English text
    
    Raises:
        RuntimeError: If all translation methods fail
    """
    if not text or not text.strip():
        return text
    
    try:
        import translators as ts
    except ImportError:
        raise ImportError(
            "translators library not installed.\n"
            "Install it with: pip install translators"
        )
    
    if source_lang is None or source_lang == "auto":
        source_lang = "auto"
    
    # Split text into chunks
    chunks = _split_text(text, max_len=4999)
    translated_chunks = []
    
    # Multiple translation engines to try (in order of preference)
    engines = ['google', 'bing' ]
    
    for chunk_idx, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append("")
            continue
        
        chunk_translated = False
        last_error = None
        
        # Try each translation engine
        for engine in engines:
            for attempt in range(max_retries):
                try:
                    result = ts.translate_text(
                        query_text=chunk,
                        translator=engine,
                        from_language=source_lang,
                        to_language='en'
                    )
                    translated_chunks.append(result)
                    chunk_translated = True
                    break
                    
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
            
            if chunk_translated:
                break
        
        # If all engines failed for this chunk
        if not chunk_translated:
            raise RuntimeError(
                f"All translation engines failed for chunk {chunk_idx + 1}.\n"
                f"Tried: {', '.join(engines)}\n"
                f"Last error: {last_error}\n"
                "This may be due to:\n"
                "- Network connectivity issues\n"
                "- All services are temporarily unavailable\n"
                "- Firewall blocking translation APIs"
            )
    
    return " ".join(translated_chunks).strip()