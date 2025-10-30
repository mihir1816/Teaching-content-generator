from __future__ import annotations
import json
from typing import List, Dict, Any, Union

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
# System style (enhanced pedagogy, analogies, and completeness)
# =========================
_SYSTEM_PROMPT = """You are "Classroom Coach", a patient, knowledgeable, and engaging teacher.

PRINCIPLES:
- Write like a supportive educator: clear, structured, and insightful.
- Always ensure a logical and natural flow between ideas.
- Use the provided Context Snippets as the base, but you may add general or external knowledge to make the topic complete and meaningful.
- Avoid citations, IDs, or reference markers in the output.
- Use real-world analogies or relatable examples wherever possible to make complex ideas easier to grasp.
- Each section should be concise (around 10–12 lines) so that it can fit comfortably on one presentation slide.
- Explanations should feel like a smooth classroom lecture, not fragmented notes.
"""

# =========================
# Task templates & schemas (enhanced with analogies, depth, and section control)
# =========================
_TASK_TEMPLATE = """TOPIC: {topic}
LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}

INSTRUCTIONS:
- Produce high-quality educational content suited for the given LEVEL and STYLE.
- Ensure the content follows a logical and natural teaching flow:
  1. Why this topic is important or needed.
  2. What the topic is (definition and explanation).
  3. Subtypes, components, or variations (if any).
  4. How it works or is applied.
  5. Real-world examples or analogies (to enhance understanding).
  6. Summary or conclusion to reinforce learning.
- You may use general or external knowledge to make the content accurate, coherent, and meaningful.
- Do NOT include citations, IDs, or references in the output.
- Keep each section concise (10–12 lines max) and clear enough to fit a single slide.
"""

# =========================
# Notes Schema (detailed, structured, with analogies)
# =========================
_SCHEMA_NOTES = """Return JSON ONLY with this schema:
{
  "topic": "string",
  "objective": "notes",
  "level": "string",
  "language": "string",
  "style": "string",
  "summary": "string",                         
  "key_points": ["string", "..."],             
  "sections": [
    {"title": "string", "bullets": ["string", "..."]}  
  ],
  "glossary": [
    {"term": "string", "definition": "string"}         
  ],
  "misconceptions": [
    {"statement": "string", "correction": "string"}    
  ]
}

NOTES:
- Include 7–10 well-structured sections covering the topic in depth.
- Each section should have around 10–12 informative lines, keeping it detailed yet presentation-friendly.
- Maintain clear progression between sections so the content reads like a guided explanation.
- Use analogies or relatable real-world examples when they enhance understanding.
"""

# =========================
# Summary Schema (clear, standalone overview)
# =========================
_SCHEMA_SUMMARY = """Return JSON ONLY with this schema:
{
  "topic": "string",
  "objective": "summary",
  "level": "string",
  "language": "string",
  "style": "string",
  "summary": "string",                      
  "key_points": ["string", "..."]           
}

NOTES:
- The summary should feel complete and standalone, covering the topic concisely.
- Highlight main ideas, ensure conceptual clarity, and use simple real-world analogies when helpful.
"""

# =========================
# MCQ Schema (uses known or high-quality conceptual questions)
# =========================
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

NOTES:
- First, attempt to locate or adapt high-quality, well-known MCQs related to the topic from trusted educational sources available on the internet (without citing them).
- If suitable MCQs are not available, generate original, exam-quality MCQs that assess higher-order thinking:
  - Mix conceptual, applied, reasoning-based, and numerical/problem-solving questions.
  - Avoid trivial recall-type questions.
  - Ensure logical distractors (plausible wrong answers).
  - Provide clear, concise explanations that teach the reasoning behind the correct answer.
- Maintain a balanced difficulty distribution: ~30% easy, 40% medium, and 30% challenging.
- Avoid any citations, source mentions, or URLs in the output.
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
    # Include system prompt in the user prompt instead
    return f"{_SYSTEM_PROMPT}\n\nOBJECTIVE: {objective}\n\n{task}\n\n{context_block}\n\n{schema}"

# =========================
# Gemini call + JSON guard
# =========================
def _gemini_call(prompt: str, model_name: str) -> str:
    genai.configure(api_key=cfg.GOOGLE_API_KEY)
    # Remove system_instruction parameter - include system prompt in the main prompt instead
    model = genai.GenerativeModel(model_name)
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
    namespace: str,
    topic: Union[str, List[str]],
    queries: List[str],
    level: str = "beginner",
    style: str = "concise",
    language: str = "en",
    final_k: int = 8,
    max_context_chars: int = 6000,
    model_name: str | None = None,
    mcq_count: int = 4
) -> Dict[str, Any]:
    """
    Produce all three objectives (notes, summary, mcqs) without any citations.
    
    Args:
        namespace: Pinecone namespace (e.g., "video:abc123" or "article:example:hash")
        topic: Topic label for the content (string or list of strings)
        queries: List of retrieval queries
        level: Difficulty level (beginner/intermediate/advanced)
        style: Writing style (concise/detailed/exam-prep)
        language: Output language code
        final_k: Number of context chunks to retrieve
        max_context_chars: Maximum characters for context
        model_name: Gemini model name (defaults to config)
        mcq_count: Number of MCQs to generate
        
    Returns: Dict with notes, summary, and mcqs
    """
    if not cfg.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY missing. Set it in your environment/.env.")

    # Handle topic as string or list
    if isinstance(topic, list):
        topic_str = ", ".join(topic) if topic else "General Topic"
    else:
        topic_str = topic or "General Topic"

    # 1) Retrieve once using your simple dense RAG
    hits = retrieve_from_queries(
        namespace=namespace,
        queries=queries,
        per_query_k=5,
        final_k=final_k,
        include_text=True
    )

    # If nothing retrieved, return "insufficient information" scaffolds
    if not hits:
        scaffold = {
            "topic": topic_str,
            "level": level,
            "language": language,
            "style": style,
            "notes": {
                "topic": topic_str, "objective": "notes", "level": level, "language": language, "style": style,
                "summary": "insufficient information",
                "key_points": [],
                "sections": [],
                "glossary": [],
                "misconceptions": []
            },
            "summary": {
                "topic": topic_str, "objective": "summary", "level": level, "language": language, "style": style,
                "summary": "insufficient information",
                "key_points": []
            },
            "mcqs": {
                "topic": topic_str, "objective": "mcqs", "level": level, "language": language, "style": style,
                "questions": []
            }
        }
        return scaffold

    context_block = _pack_context(hits, max_context_chars=max_context_chars)
    model = model_name or getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash")

    # 2) NOTES
    notes_prompt = _build_prompt("notes", topic_str, level, style, language, context_block)
    notes_raw = _gemini_call(notes_prompt, model)
    notes = _json_sanitize(notes_raw)

    # 3) SUMMARY
    summary_prompt = _build_prompt("summary", topic_str, level, style, language, context_block)
    summary_raw = _gemini_call(summary_prompt, model)
    summary = _json_sanitize(summary_raw)

    # 4) MCQS (nudge for quantity)
    mcq_steer = f"\n\nAdditional requirement: generate approximately {mcq_count} questions."
    mcqs_prompt = _build_prompt("mcqs", topic_str, level, style, language, context_block) + mcq_steer
    mcqs_raw = _gemini_call(mcqs_prompt, model)
    mcqs = _json_sanitize(mcqs_raw)

    # Backfill missing required fields if the model omitted any
    for blob, objective in ((notes, "notes"), (summary, "summary"), (mcqs, "mcqs")):
        blob.setdefault("topic", topic_str)
        blob.setdefault("objective", objective)
        blob.setdefault("level", level)
        blob.setdefault("language", language)
        blob.setdefault("style", style)

    return {
        "topic": topic_str,
        "level": level,
        "language": language,
        "style": style,
        "notes": notes,
        "summary": summary,
        "mcqs": mcqs,
    }