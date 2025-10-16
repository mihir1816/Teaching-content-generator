import requests
from typing import Optional, List
import app.config as cfg

def _split_for_api(text: str, max_len: int = 4500) -> List[str]:
    """
    Split long text into chunks so we don't exceed typical API limits.
    Splits on sentence-ish boundaries when possible.
    """
    if len(text) <= max_len:
        return [text]
    parts, buf = [], []
    cur_len = 0
    for token in text.split():
        if cur_len + len(token) + 1 > max_len:
            parts.append(" ".join(buf))
            buf, cur_len = [token], len(token) + 1
        else:
            buf.append(token)
            cur_len += len(token) + 1
    if buf:
        parts.append(" ".join(buf))
    return parts

def translate_to_english(text: str, source_lang: Optional[str] = None) -> str:
    """
    Translate arbitrary text to English using LibreTranslate.
    - Uses cfg.LT_URL and optional cfg.LT_API_KEY
    - If source_lang is None, LibreTranslate will auto-detect.
    """
    if not text.strip():
        return text

    endpoint = cfg.LT_URL.rstrip("/") + "/translate"
    headers = {"Accept": "application/json"}
    api_key = cfg.LT_API_KEY or None

    chunks = _split_for_api(text)
    translated_parts = []

    for chunk in chunks:
        payload = {
            "q": chunk,
            "source": source_lang if source_lang else "auto",
            "target": "en",
            "format": "text",
        }
        if api_key:
            payload["api_key"] = api_key
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        translated_parts.append(data.get("translatedText", ""))

    return " ".join(translated_parts).strip()