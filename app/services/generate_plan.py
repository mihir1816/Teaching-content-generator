from __future__ import annotations
import json
from typing import List, Dict, Any, Optional, Union

import app.config as cfg

# Gemini SDK
try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError(
        "google-generativeai is required. Install it with:\n  pip install google-generativeai"
    ) from e


# =========================
# System instruction
# =========================
_SYSTEM_PROMPT = """You are “Curriculum Planner,” an expert pedagogy designer.
Create practical, classroom-ready content plans that are clear, structured, and tailored to the audience level.

Principles:
- Be precise, teacher-friendly, and realistic about scope and time.
- Use only the information provided by the teacher (topics + optional description).
- If something is unclear or unspecified, choose sensible defaults rather than asking follow-ups.
- Output MUST be valid JSON matching the requested schema, no extra text.
- Ensure subtopic weights sum to exactly 100 (we’ll also normalize on our side if needed).
"""


# =========================
# Output schema (model hint)
# =========================
_SCHEMA = """Return JSON ONLY with this schema:
{
  "level": "beginner|intermediate|advanced",
  "style": "concise|detailed|exam-prep",
  "language": "string",
  "topics": ["string", "..."],
  "planner_notes": "string",                 // brief rationale of the structure
  "overall_objectives": ["string", "..."],   // 3–6 high-level outcomes
  "subtopics": [
    {
      "title": "string",
      "weight": 0,                           // integer percent, 0–100
      "learning_outcomes": ["string", "..."],
      "key_terms": ["string", "..."],
      "suggested_examples": ["string", "..."],
      "suggested_questions": 0,              // how many MCQs/short-answer to generate later
      "estimated_time_minutes": 0            // estimated teaching/reading time
    }
  ],
  "assessment_strategy": {
    "format": ["mcqs", "short-answer", "applied-task"],
    "notes": "string"
  }
}
"""


# =========================
# Prompt builder
# =========================
_PLAN_TEMPLATE = """LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}

TOPICS:
{topics_block}

TEACHER NOTES (optional):
{desc_block}

INSTRUCTIONS:
- Create a coherent content plan that covers ALL topics above.
- Include 6–10 subtopics total for single-topic; for multiple topics, distribute fairly.
- Each subtopic must have: title, weight %, learning outcomes, key terms, 1–3 suggested examples,
  suggested_questions (count), and estimated_time_minutes.
- Weights across all subtopics MUST sum to 100 in total.
- Keep style and depth aligned to LEVEL and STYLE.
- No citations, no references.
"""

def _build_prompt(
    level: str,
    style: str,
    topics: List[str],
    language: str,
    description: Optional[str]
) -> str:
    topics_block = "\n".join(f"- {t}" for t in topics)
    desc_block = (description or "").strip() or "none"
    return f"{_PLAN_TEMPLATE.format(level=level, style=style, language=language, topics_block=topics_block, desc_block=desc_block)}\n\n{_SCHEMA}"


# =========================
# JSON helpers
# =========================
def _json_sanitize(s: str) -> Dict[str, Any]:
    try:
        return json.loads(s)
    except Exception:
        pass
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(s[start:end + 1])
    raise ValueError("LLM did not return valid JSON.")

def _coerce_int(x, default=0) -> int:
    try:
        return int(round(float(x)))
    except Exception:
        return default

def _normalize_weights(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure subtopic weights are ints and sum to 100.
    If sum is 0, distribute evenly.
    """
    subs = plan.get("subtopics") or []
    if not isinstance(subs, list) or not subs:
        return plan

    # Coerce to ints >=0
    weights = []
    for s in subs:
        w = _coerce_int(s.get("weight", 0), default=0)
        w = max(0, w)
        s["weight"] = w
        weights.append(w)

    total = sum(weights)
    n = len(subs)

    if total == 100:
        return plan

    if total == 0:
        # Even split
        even = [100 // n] * n
        remainder = 100 - sum(even)
        for i in range(remainder):
            even[i] += 1
        for s, w in zip(subs, even):
            s["weight"] = w
        return plan

    # Rescale proportionally
    scaled = []
    running = 0
    for i, w in enumerate(weights):
        if i < n - 1:
            new_w = int(round(w * 100.0 / max(1, total)))
            scaled.append(new_w)
            running += new_w
        else:
            # last one takes the remainder to ensure exact 100
            scaled.append(100 - running)

    for s, w in zip(subs, scaled):
        s["weight"] = w
    return plan


# =========================
# Public API
# =========================
def generate_plan(
    level: str,
    style: str,
    topics: Union[str, List[str]],
    description: Optional[str] = None,
    language: str = "en",
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a detailed, weighted content plan for teacher approval.

    Args:
      level: "beginner" | "intermediate" | "advanced"
      style: "concise" | "detailed" | "exam-prep"
      topics: str or list[str] (one or multiple topics)
      description: optional teacher notes
      language: output language (default "en")
      model_name: override Gemini model; defaults to cfg.LLM_MODEL_NAME

    Returns:
      dict with fields described in _SCHEMA, weights normalized to sum 100.
    """
    if isinstance(topics, str):
        topics_list = [t.strip() for t in topics.split(",") if t.strip()] if ("," in topics) else [topics.strip()]
    else:
        topics_list = [t.strip() for t in topics if t and t.strip()]
    if not topics_list:
        raise ValueError("At least one topic is required.")

    if not cfg.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY missing. Set it in your environment/.env.")

    genai.configure(api_key=cfg.GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name or getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash"),
                                  system_instruction=_SYSTEM_PROMPT)

    prompt = _build_prompt(level=level, style=style, topics=topics_list, language=language, description=description)
    resp = model.generate_content(prompt)
    raw = (resp.text or "").strip()
    data = _json_sanitize(raw)

    # Backfill/ensure fields
    data.setdefault("level", level)
    data.setdefault("style", style)
    data.setdefault("language", language)
    data.setdefault("topics", topics_list)

    # Normalize weights
    data = _normalize_weights(data)

    # Coerce numeric fields for safety
    for s in data.get("subtopics") or []:
        s["weight"] = _coerce_int(s.get("weight", 0), default=0)
        s["suggested_questions"] = _coerce_int(s.get("suggested_questions", 0), default=0)
        s["estimated_time_minutes"] = _coerce_int(s.get("estimated_time_minutes", 0), default=0)

        # ensure list fields exist
        s.setdefault("learning_outcomes", [])
        s.setdefault("key_terms", [])
        s.setdefault("suggested_examples", [])

    # Ensure top-level fields exist
    data.setdefault("planner_notes", "")
    data.setdefault("overall_objectives", [])
    data.setdefault("assessment_strategy", {"format": ["mcqs"], "notes": ""})

    return data
