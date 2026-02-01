from __future__ import annotations
import json
from typing import List, Dict, Any, Optional, Union

import app.config as cfg

# Gemini SDK
try:
    import google.genai as genai
except Exception as e:
    raise ImportError(
        "google-genai is required. Install it with:\n  pip install google-genai"
    ) from e


# =========================
# System instruction
# =========================
_SYSTEM_PROMPT = """You are "Curriculum Planner," an expert pedagogy designer.
Create practical, classroom-ready content plans that are clear, structured, and tailored to the audience level.

Principles:
- Be precise, teacher-friendly, and realistic about scope and time.
- Use only the information provided by the teacher (topics + optional description).
- If something is unclear or unspecified, choose sensible defaults rather than asking follow-ups.
- Output MUST be valid JSON matching the requested schema, no extra text.
"""


# =========================
# Output schema (model hint)
# =========================
_SCHEMA = """Return JSON ONLY with this schema:
{
  "topic": "string",
  "objectives": ["string", "..."],   
  "subtopics": [
    {
      "title": "string",
      "learning_outcomes": ["string", "..."],
      "suggested_examples": ["string", "..."]
    }
  ]
}
"""


# =========================
# Prompt builder
# =========================
_PLAN_TEMPLATE = """LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}

TOPICS:
{topic}

TEACHER NOTES (optional):
{desc_block}

INSTRUCTIONS:
- Create a coherent content plan that covers the topic above.
- Include 6–10 subtopics.
- Each subtopic must have: title, learning outcomes (2-4 items), and 1–3 suggested examples.
- No citations, no references.
"""


def _build_prompt(
    level: str,
    style: str,
    topic: Union[str, List[str]], 
    language: str,
    description: Optional[str]
) -> str:
    desc_block = (description or "").strip() or "none"
    return f"{_PLAN_TEMPLATE.format(level=level, style=style, language=language, topic=topic, desc_block=desc_block)}\n\n{_SCHEMA}"


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


# =========================
# Public API
# =========================
def generate_plan(
    level: str,
    style: str,
    topics : Union[str, List[str]],
    description: Optional[str] = None,
    language: str = "en",
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a simple curriculum plan.
    
    Args:
        level: beginner, intermediate, or advanced
        style: concise, detailed, or exam-prep
        topics: Topic to create plan for (string)
        description: Optional teacher notes/description
        language: Language code (default: "en")
        model_name: Optional model override
    
    Returns:
        Dictionary with simple structure:
        {
          "topic": "...",
          "objectives": [...],
          "subtopics": [...]
        }
    """
    topic_str = topics.strip() if isinstance(topics, str) else " ".join(topics)
    if not topic_str:
        raise ValueError("Topic is required.")

    if not cfg.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY missing. Set it in your environment/.env.")

    genai.configure(api_key=cfg.GOOGLE_API_KEY)

    model = genai.GenerativeModel(model_name or getattr(cfg, "LLM_MODEL_NAME", "gemini-2.5-flash"))

    prompt = _build_prompt(level=level, style=style, topic=topic_str, language=language, description=description)

    resp = model.generate_content([
        {"role": "model", "parts": _SYSTEM_PROMPT},
        {"role": "user", "parts": prompt}
    ])

    raw = (resp.text or "").strip()
    data = _json_sanitize(raw)

    # Ensure defaults
    data.setdefault("topic", topic_str)  # fixed: use topic_str
    data.setdefault("objectives", [])
    data.setdefault("subtopics", [])
    
    # Normalize subtopics
    for s in data.get("subtopics", []):
        s.setdefault("title", "")
        s.setdefault("learning_outcomes", [])
        s.setdefault("suggested_examples", [])
    
    return data
