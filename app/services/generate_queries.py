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


_LLM_PROMPT_TEMPLATE = """
You are an expert assistant that helps a teacher prepare retrieval queries for a video transcript.

Given the teacher's topic or short plan, produce {n_total} short, diverse search queries
(≤ 15 words each) that would best retrieve relevant transcript chunks for RAG (Retrieval-Augmented Generation).

Mix styles:
- key concept phrases
- "what is …" questions
- "how does … work" questions
- comparison or example-based questions

Each query must stand alone, be natural English, and stay within 15 words.

Output: plain text only, ONE query per line. No numbering, no quotes, no extra text.

Content Plan:
\"\"\"{plan_text}\"\"\"
""".strip()


def _gemini_queries(plan: str, n_total: int, model_name: str) -> List[str]:
    """Call Gemini model to generate short, diverse RAG queries."""
    genai.configure(api_key=cfg.GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name)
    prompt = _LLM_PROMPT_TEMPLATE.format(n_total=n_total, plan_text=plan[:6000])
    
    # FIX: Handle response more safely
    try:
        resp = model.generate_content(prompt)
        
        # Check if response has text attribute and it's not None
        if not hasattr(resp, 'text'):
            raise RuntimeError("Gemini response has no 'text' attribute")
        
        if resp.text is None:
            # Check if response was blocked or has no content
            if hasattr(resp, 'prompt_feedback'):
                feedback = resp.prompt_feedback
                raise RuntimeError(f"Gemini blocked the request. Reason: {feedback}")
            raise RuntimeError("Gemini returned None response with no feedback")
        
        text = resp.text.strip()
        
    except Exception as e:
        # More descriptive error for debugging
        raise RuntimeError(f"Failed to generate content from Gemini: {type(e).__name__} - {e}") from e

    out: List[str] = []
    seen = set()

    for line in text.splitlines():
        q = line.strip().strip("-•").strip()
        if not q:
            continue
        q = " ".join(q.split())
        q = q.strip('"').strip("'").lower()
        if q in seen:
            continue
        words = q.split()
        if len(words) > 9:
            q = " ".join(words[:9])
        if q:
            seen.add(q)
            out.append(q)

    return out[:n_total]


def generate_queries_from_plan(plan: str, n: int = 8, model_name: str | None = None) -> List[str]:
    """
    Generate ~n short, diverse RAG queries from a teacher's content plan using Gemini.
    """
    if not cfg.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY missing. Set it in your environment/.env.")
    
    if not plan or not plan.strip():
        raise ValueError("Plan text cannot be empty")

    n = max(3, min(12, n))
    llm_model = model_name or getattr(cfg, "LLM_MODEL_NAME", "gemini-2.5-flash")
    return _gemini_queries(plan, n_total=n, model_name=llm_model)
