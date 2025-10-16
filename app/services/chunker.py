import hashlib
import re
from typing import List, Dict, Callable

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

import app.config as cfg

# --- Tokenizer ---------------------------------------------------------------

# Use a tokenizer compatible with your embedding/LLM models.
# (o200k_base works well with GPT-4o/Emb-3; fallback to cl100k_base if unavailable)
def _get_encoding():
    for name in (cfg.__dict__.get("TOKENIZER") or "", "o200k_base", "cl100k_base"):
        try:
            return tiktoken.get_encoding(name)
        except Exception:
            continue
    # absolute fallback
    return tiktoken.get_encoding("cl100k_base")

_encoding = _get_encoding()

def count_tokens(text: str) -> int:
    """Count tokens using the chosen tiktoken encoding."""
    return len(_encoding.encode(text))

# --- Normalization -----------------------------------------------------------

_WS_RE = re.compile(r"\s+", flags=re.MULTILINE)

def normalize_text(text: str) -> str:
    """
    Light normalization:
      - Strip outer whitespace
      - Collapse repeated whitespace/newlines
    (We keep punctuation; it helps splitting.)
    """
    text = (text or "").strip()
    return _WS_RE.sub(" ", text)

# --- Chunk ID ----------------------------------------------------------------

def chunk_id(text: str) -> str:
    """Deterministic short id for a chunk (sha1 hex, 16 chars)."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]

# --- Splitter ----------------------------------------------------------------

def _build_splitter(length_fn: Callable[[str], int]) -> RecursiveCharacterTextSplitter:
    """
    Recursive splitter that prefers larger semantic boundaries first
    and falls back to smaller units. We use token-based sizes.
    """
    separators = [
        "\n\n",  # paragraphs
        "\n",    # lines
        ". ",    # sentences (basic)
        "! ",
        "? ",
        " ",     # words
        ""       # characters (last resort)
    ]

    return RecursiveCharacterTextSplitter(
        chunk_size=cfg.CHUNK_SIZE,
        chunk_overlap=cfg.CHUNK_OVERLAP,
        length_function=length_fn,
        separators=separators,
        is_separator_regex=False,
        add_start_index=False,  # we don't need positions
    )


def make_chunks(transcript_text: str) -> List[Dict[str, str]]:
    """
    Split full transcript text into token-aware chunks with overlap.
    Returns: [{"id": "...", "text": "..."}, ...]
    """
    clean = normalize_text(transcript_text)
    if not clean:
        return []

    splitter = _build_splitter(count_tokens)

    # Primary split
    parts: List[str] = splitter.split_text(clean)

    # Optional tail/edge handling:
    # - If last part is too small and previous can absorb without exceeding a soft max,
    #   merge them. We'll use CHUNK_MIN and CHUNK_MAX if present in config.
    min_tokens = getattr(cfg, "CHUNK_MIN", None)
    max_tokens = getattr(cfg, "CHUNK_MAX", None)

    if len(parts) >= 2 and min_tokens is not None and max_tokens is not None:
        last = parts[-1]
        prev = parts[-2]
        if count_tokens(last) < min_tokens and count_tokens(prev) + count_tokens(last) <= max_tokens:
            parts[-2] = (prev + " " + last).strip()
            parts.pop()

    # Materialize final chunks with deterministic IDs
    chunks: List[Dict[str, str]] = []
    for p in parts:
        txt = p.strip()
        if not txt:
            continue
        chunks.append({"id": chunk_id(txt), "text": txt})

    return chunks

# --- Public API --------------------------------------------------------------

__all__ = ["count_tokens", "normalize_text", "make_chunks"]
