from __future__ import annotations
import json
from typing import List, Dict, Any

import app.config as cfg
from app.services.retriever import retrieve_from_queries

# Gemini SDK
try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError(
        "google-generativeai is required. Install with:\n  pip install google-generativeai"
    ) from e


# =========================
# System style (no citations)
# =========================
_SYSTEM_PROMPT = """You are “Classroom Coach”, a patient pedagogue who explains clearly and accurately.

PRINCIPLES:
- Write as a supportive teacher: clear, structured, and concise.
- Use only the Context Snippets given; do not assume outside knowledge.
- If something is not in the context, avoid making it up; say “insufficient information.”
- Do NOT include any citations, IDs, or references in the output.
- Output MUST be valid JSON that matches the requested schema exactly, with no extra text.
"""


# =========================
# Task templates & schemas (no citation fields)
# =========================
_TASK_TEMPLATE = """TOPIC: {topic}
LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}

INSTRUCTIONS:
- Produce high-quality content tailored to LEVEL and STYLE.
- Rely on Context Snippets. If information is missing, write “insufficient information.”
- No citations or chunk IDs in the output.
"""

_SCHEMA_NOTES = """Return JSON ONLY with this schema:
{
  "topic": "string",
  "objective": "notes",
  "level": "string",
  "language": "string",
  "style": "string",
  "summary": "string",                         // 3–6 sentences
  "key_points": ["string", "..."],             // 5–10 concise bullets
  "sections": [
    {"title": "string", "bullets": ["string", "..."]}  // 3–6 bullets
  ],
  "glossary": [
    {"term": "string", "definition": "string"}         // 5–10 entries
  ],
  "misconceptions": [
    {"statement": "string", "correction": "string"}    // 3–5 entries
  ]
}
"""

_SCHEMA_SUMMARY = """Return JSON ONLY with this schema:
{
  "topic": "string",
  "objective": "summary",
  "level": "string",
  "language": "string",
  "style": "string",
  "summary": "string",                      // 5–8 tight sentences
  "key_points": ["string", "..."]           // 5–10 bullets
}
"""

_SCHEMA_MCQS = """Return JSON ONLY with this schema:
{
  "topic": "string",
  "objective": "mcqs",
  "level": "string",
  "language": "string",
  "style": "string",
  "questions": [
    {
      "stem": "string",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "explanation": "string"
    }
  ]
}
"""


# =========================
# Context packing (no IDs, just text)
# =========================
def _pack_context(hits: List[Dict[str, Any]], max_context_chars: int = 6000) -> str:
    """
    Build a plain context block (no chunk IDs). We still cap total size.
    """
    lines = ["CONTEXT SNIPPETS:"]
    total = 0
    for h in hits:
        txt = (h.get("text") or "").strip()
        if not txt:
            continue
        snippet = f"{txt}\n"
        # keep at least one snippet even if long; otherwise cap by max_context_chars
        if total + len(snippet) > max_context_chars and total > 0:
            break
        lines.append(snippet)
        total += len(snippet)
    return "\n".join(lines)


def _build_prompt(objective: str, topic: str, level: str, style: str, language: str, context_block: str) -> str:
    task = _TASK_TEMPLATE.format(topic=topic, level=level, style=style, language=language)
    schema = _SCHEMA_NOTES if objective == "notes" else (_SCHEMA_SUMMARY if objective == "summary" else _SCHEMA_MCQS)
    # Concatenate carefully; system instruction is injected via system_instruction (Gemini supports it)
    return f"OBJECTIVE: {objective}\n\n{task}\n\n{context_block}\n\n{schema}"


# =========================
# Gemini call + JSON guard
# =========================
def _gemini_call(prompt: str, model_name: str) -> str:
    genai.configure(api_key=cfg.GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name, system_instruction=_SYSTEM_PROMPT)
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()


def _json_sanitize(s: str) -> Dict[str, Any]:
    """
    Parse JSON; if it fails, try to recover the first {...} block.
    """
    try:
        return json.loads(s)
    except Exception:
        pass
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(s[start:end + 1])
    raise ValueError("LLM did not return valid JSON.")


# =========================
# Public API
# =========================
def generate_all(
    video_id: str,
    topic: str,
    queries: List[str],
    level: str = "beginner",
    style: str = "concise",
    language: str = "en",
    final_k: int = 8,
    max_context_chars: int = 6000,
    model_name: str | None = None,
    mcq_count: int = 8
) -> Dict[str, Any]:
    """
    Produce all three objectives (notes, summary, mcqs) without any citations.
    """
    if not cfg.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY missing. Set it in your environment/.env.")

    # 1) Retrieve once using your simple dense RAG
    hits = retrieve_from_queries(
        video_id=video_id,
        queries=queries,
        per_query_k=5,
        final_k=final_k,
        include_text=True
    )

    # If nothing retrieved, return “insufficient information” scaffolds
    if not hits:
        scaffold = {
            "topic": topic,
            "level": level,
            "language": language,
            "style": style,
            "notes": {
                "topic": topic, "objective": "notes", "level": level, "language": language, "style": style,
                "summary": "insufficient information",
                "key_points": [],
                "sections": [],
                "glossary": [],
                "misconceptions": []
            },
            "summary": {
                "topic": topic, "objective": "summary", "level": level, "language": language, "style": style,
                "summary": "insufficient information",
                "key_points": []
            },
            "mcqs": {
                "topic": topic, "objective": "mcqs", "level": level, "language": language, "style": style,
                "questions": []
            }
        }
        return scaffold

    context_block = _pack_context(hits, max_context_chars=max_context_chars)
    model = model_name or getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash")

    # 2) NOTES
    notes_prompt = _build_prompt("notes", topic, level, style, language, context_block)
    notes_raw = _gemini_call(notes_prompt, model)
    notes = _json_sanitize(notes_raw)

    # 3) SUMMARY
    summary_prompt = _build_prompt("summary", topic, level, style, language, context_block)
    summary_raw = _gemini_call(summary_prompt, model)
    summary = _json_sanitize(summary_raw)

    # 4) MCQS (nudge for quantity)
    mcq_steer = f"\n\nAdditional requirement: generate approximately {mcq_count} questions."
    mcqs_prompt = _build_prompt("mcqs", topic, level, style, language, context_block) + mcq_steer
    mcqs_raw = _gemini_call(mcqs_prompt, model)
    mcqs = _json_sanitize(mcqs_raw)

    # Backfill missing required fields if the model omitted any
    for blob, objective in ((notes, "notes"), (summary, "summary"), (mcqs, "mcqs")):
        blob.setdefault("topic", topic)
        blob.setdefault("objective", objective)
        blob.setdefault("level", level)
        blob.setdefault("language", language)
        blob.setdefault("style", style)

    return {
        "topic": topic,
        "level": level,
        "language": language,
        "style": style,
        "notes": notes,
        "summary": summary,
        "mcqs": mcqs,
    }
