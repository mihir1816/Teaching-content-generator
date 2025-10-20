# app/main/main_topic_name.py
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

import app.config as cfg

# Gemini SDK (required)
try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError(
        "google-generativeai is required. Install with:\n  pip install google-generativeai"
    ) from e


SYSTEM_PROMPT = """You are “Classroom Coach,” a helpful teacher assistant.
Write clear, structured, student-friendly content.
Do NOT include citations, IDs, or external references.
Respond ONLY with valid JSON that matches the schema you are given—no extra text.
If some information is missing from the plan, make reasonable assumptions and proceed.
"""

# JSON schemas we want back (single response including all three objectives)
SCHEMA = """Return JSON ONLY with this schema:
{
  "topic": "string",
  "level": "beginner|intermediate|advanced",
  "style": "concise|detailed|exam-prep",
  "language": "string",
  "notes": {
    "summary": "string",                  // 3–6 sentences
    "key_points": ["string", "..."],      // 5–10 bullets
    "sections": [                         // 2–5 sections
      { "title": "string", "bullets": ["string", "..."] }
    ],
    "glossary": [                         // 5–10 terms
      { "term": "string", "definition": "string" }
    ],
    "misconceptions": [                   // 3–5 items
      { "statement": "string", "correction": "string" }
    ]
  },
  "summary": {
    "overview": "string",                 // 5–8 tight sentences
    "key_points": ["string", "..."]
  },
  "mcqs": {
    "count": 0,
    "questions": [
      {
        "stem": "string",
        "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
        "answer": "A",
        "explanation": "string"
      }
    ]
  }
}
"""

TASK_TEMPLATE = """TOPIC: {topic}
LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}
MCQ_COUNT: {mcq_count}

PLAN (from teacher):
{plan_pretty}

INSTRUCTIONS:
- Produce high-quality content aligned to LEVEL and STYLE.
- Make the content self-contained and readable.
- MCQs: generate approximately MCQ_COUNT items.
- No citations or external links.
"""

def _slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "untitled"

def _ensure_output_dir() -> Path:
    out_dir = Path(getattr(cfg, "DATA_PATH", "data/")) / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def _json_sanitize(s: str) -> Dict[str, Any]:
    # strict parse first
    try:
        return json.loads(s)
    except Exception:
        pass
    # best-effort: extract the first {...} block
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(s[start:end + 1])
    raise ValueError("LLM did not return valid JSON.")

def generate_content_from_plan(plan: Dict[str, Any], output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate Notes + Summary + MCQs directly from a teacher plan using Gemini (no RAG).
    Reads topic/level/style/mcq_count from `plan` if present, else uses defaults.

    Returns:
      {
        "topic": ...,
        "level": ...,
        "style": ...,
        "language": ...,
        "notes": {...},
        "summary": {...},
        "mcqs": {...},
        "_output_path": "data/outputs/<topic>_plan_content.json"
      }
    """
    if not getattr(cfg, "GOOGLE_API_KEY", None):
        raise RuntimeError("GOOGLE_API_KEY missing in config/env.")

    # Extract controls from plan or use defaults
    topic = plan.get("topic") or (", ".join(plan.get("topics", [])) if plan.get("topics") else "Untitled Topic")
    level = plan.get("level", "beginner")
    style = plan.get("style", "concise")
    language = plan.get("language", "en")
    mcq_count = int(plan.get("mcq_count", 8))

    # Prepare prompt
    plan_pretty = json.dumps(plan, ensure_ascii=False, indent=2)
    task = TASK_TEMPLATE.format(
        topic=topic, level=level, style=style, language=language, mcq_count=mcq_count, plan_pretty=plan_pretty
    )
    prompt = f"{task}\n\n{SCHEMA}"

    # Model
    genai.configure(api_key=cfg.GOOGLE_API_KEY)
    model_name = getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)

    # Call LLM
    resp = model.generate_content(prompt)
    raw = (resp.text or "").strip()
    data = _json_sanitize(raw)

    # Backfill required fields if missing
    data.setdefault("topic", topic)
    data.setdefault("level", level)
    data.setdefault("style", style)
    data.setdefault("language", language)
    # Ensure mcq count field mirrors request (not mandatory if model already filled)
    if "mcqs" in data and isinstance(data["mcqs"], dict):
        data["mcqs"].setdefault("count", mcq_count)

    # Decide output path
    out_dir = _ensure_output_dir()
    default_name = f"{_slugify(topic)}_plan_content.json"
    out_path = Path(output_path) if output_path else (out_dir / default_name)

    # Save
    with Path(out_path).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    data["_output_path"] = str(out_path)
    return data
