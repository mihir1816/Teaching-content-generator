from __future__ import annotations
from typing import List

import app.config as cfg

# Gemini SDK
try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError(
        "google-generativeai is required. Install it with:\n  pip install google-generativeai"
    ) from e


# ---------------------------
# Prompt template
# ---------------------------
_LLM_PROMPT_TEMPLATE = """
You are an expert assistant that helps a teacher prepare retrieval queries for a video transcript.

Given the teacher’s topic or short plan, produce {n_total} short, diverse search queries
(≤ 15 words each) that would best retrieve relevant transcript chunks for RAG (Retrieval-Augmented Generation).

Mix styles:
- key concept phrases
- “what is …” questions
- “how does … work” questions
- comparison or example-based questions

Each query must stand alone, be natural English, and stay within 15 words.

Output: plain text only, ONE query per line. No numbering, no quotes, no extra text.

Content Plan:
\"\"\"{plan_text}\"\"\"
""".strip()


# ---------------------------
# Gemini query generation
# ---------------------------
def _gemini_queries(plan: str, n_total: int, model_name: str) -> List[str]:
    """Call Gemini model to generate short, diverse RAG queries."""
    genai.configure(api_key=cfg.GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name)
    prompt = _LLM_PROMPT_TEMPLATE.format(n_total=n_total, plan_text=plan[:6000])
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    out: List[str] = []
    seen = set()

    for line in text.splitlines():
        q = line.strip().strip("-•").strip()
        if not q:
            continue
        q = " ".join(q.split())  # collapse spaces
        q = q.strip('"').strip("'").lower()
        if q in seen:
            continue
        words = q.split()
        if len(words) > 9:
            q = " ".join(words[:9])  # trim long ones
        if q:
            seen.add(q)
            out.append(q)

    return out[:n_total]


# ---------------------------
# Public API
# ---------------------------
def generate_queries_from_plan(plan: str, n: int = 8, model_name: str | None = None) -> List[str]:
    """
    Generate ~n short, diverse RAG queries from a teacher's content plan using Gemini.
    """
    if not cfg.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY missing. Set it in your environment/.env.")

    n = max(3, min(12, n))  # keep reasonable bounds
    llm_model = model_name or getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash")
    return _gemini_queries(plan, n_total=n, model_name=llm_model)
