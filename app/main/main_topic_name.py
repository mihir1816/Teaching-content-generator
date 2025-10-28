from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

import app.config as cfg
from app.services.ppt_builder import build_ppt_from_result

# Gemini SDK (required)
try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError(
        "google-generativeai is required. Install with:\n  pip install google-generativeai"
    ) from e


SYSTEM_PROMPT = """You are "Classroom Coach," an expert educational content creator who produces high-quality teaching materials.

YOUR MISSION:
- Create clear, accurate, and engaging educational content
- Adapt complexity and depth based on the student's level
- Structure information logically and pedagogically
- Include practical examples and real-world applications
- Anticipate and address common misconceptions
- Write in a supportive, encouraging tone

CRITICAL RULES:
- Do NOT include citations, references, or source IDs
- Output MUST be valid JSON matching the exact schema provided
- Use ONLY information from the provided plan/context
- If information is missing, use "insufficient information" rather than inventing facts
- NO extra text outside the JSON structure
"""

# Level-specific guidelines
LEVEL_GUIDELINES = {
    "beginner": """
BEGINNER LEVEL APPROACH:
- Use simple, everyday language - avoid jargon
- Start with foundational concepts and build gradually
- Include plenty of concrete examples and analogies
- Break down complex ideas into small, digestible steps
- Emphasize "why" things matter before "how" they work
- Use relatable scenarios from daily life
""",
    "intermediate": """
INTERMEDIATE LEVEL APPROACH:
- Use standard terminology with clear explanations
- Connect concepts to show relationships and patterns
- Include both theory and practical applications
- Introduce some complexity and nuance
- Balance breadth and depth of coverage
- Reference real-world use cases and scenarios
""",
    "advanced": """
ADVANCED LEVEL APPROACH:
- Use precise technical terminology freely
- Explore subtle distinctions and edge cases
- Include theoretical foundations and advanced applications
- Discuss trade-offs, limitations, and best practices
- Connect to broader context and cutting-edge developments
- Challenge with thought-provoking questions and scenarios
"""
}

# Style-specific guidelines
STYLE_GUIDELINES = {
    "concise": """
CONCISE STYLE:
- Keep explanations brief and to-the-point (3-5 sentences max)
- Focus on essential information only
- Use bullet points for clarity
- Limit examples to 1-2 most illustrative cases
- Aim for quick reference and rapid learning
- 5-7 key points maximum
- 2-3 sections with 3-4 bullets each
""",
    "detailed": """
DETAILED STYLE:
- Provide comprehensive explanations (6-10 sentences)
- Include context, background, and rationale
- Use multiple examples to illustrate concepts
- Explore implications and applications
- Add helpful analogies and metaphors
- 8-12 key points
- 4-6 sections with 5-7 bullets each
- Rich glossary with thorough definitions
""",
    "exam-prep": """
EXAM-PREP STYLE:
- Focus on testable knowledge and skills
- Highlight key formulas, definitions, and procedures
- Include common exam question patterns
- Emphasize frequent mistakes and how to avoid them
- Provide memory aids and mnemonics
- Structure content as study guides
- 6-8 key points focused on assessment
- 3-4 sections organized by exam topics
- Extensive misconceptions section (5-8 items)
"""
}

# JSON schema
SCHEMA = """Return JSON ONLY with this exact schema:
{
  "topic": "string",
  "level": "beginner|intermediate|advanced",
  "style": "concise|detailed|exam-prep",
  "language": "string",
  "notes": {
    "summary": "string",
    "key_points": ["string", "..."],
    "sections": [
      { "title": "string", "bullets": ["string", "..."] }
    ],
    "glossary": [
      { "term": "string", "definition": "string" }
    ],
    "misconceptions": [
      { "statement": "string", "correction": "string" }
    ]
  },
  "summary": {
    "overview": "string",
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

{level_guide}

{style_guide}

TEACHER'S PLAN:
{plan_pretty}

YOUR TASK:
1. Create comprehensive NOTES following the level and style guidelines above
2. Write a focused SUMMARY that captures the essence
3. Generate {mcq_count} high-quality MCQs that test understanding at the appropriate level

QUALITY CHECKLIST:
✓ Content matches the {level} level complexity
✓ Format follows the {style} style requirements
✓ All sections are complete and well-structured
✓ Examples are relevant and clear
✓ Glossary terms are essential and well-defined
✓ Misconceptions address real student confusion
✓ MCQs test genuine understanding, not just memorization
✓ Output is valid JSON with no extra text
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
    try:
        return json.loads(s)
    except Exception:
        pass
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(s[start:end + 1])
    raise ValueError("LLM did not return valid JSON.")

def generate_content_from_plan(
    plan: Dict[str, Any], 
    output_path: Optional[str] = None,
    level: str = "beginner",
    style: str = "concise"
) -> Dict[str, Any]:
    """
    Generate Notes + Summary + MCQs directly from a teacher plan using Gemini (no RAG).
    """
    if not getattr(cfg, "GOOGLE_API_KEY", None):
        raise RuntimeError("GOOGLE_API_KEY missing in config/env.")

    topic = plan.get("topic") or (", ".join(plan.get("topics", [])) if plan.get("topics") else "Untitled Topic")
    language = plan.get("language", "en")
    mcq_count = int(plan.get("mcq_count", 8))

    level_guide = LEVEL_GUIDELINES.get(level, LEVEL_GUIDELINES["beginner"])
    style_guide = STYLE_GUIDELINES.get(style, STYLE_GUIDELINES["concise"])

    plan_pretty = json.dumps(plan, ensure_ascii=False, indent=2)
    task = TASK_TEMPLATE.format(
        topic=topic, 
        level=level, 
        style=style, 
        language=language, 
        mcq_count=mcq_count, 
        plan_pretty=plan_pretty,
        level_guide=level_guide,
        style_guide=style_guide
    )
    prompt = f"{task}\n\n{SCHEMA}"

    genai.configure(api_key=cfg.GOOGLE_API_KEY)
    model_name = getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)

    print(f">>> Generating content for: {topic}")
    print(f"    Level: {level}, Style: {style}, Language: {language}")

    resp = model.generate_content(prompt)
    raw = (resp.text or "").strip()
    data = _json_sanitize(raw)

    data.setdefault("topic", topic)
    data.setdefault("level", level)
    data.setdefault("style", style)
    data.setdefault("language", language)

    if "mcqs" in data and isinstance(data["mcqs"], dict):
        data["mcqs"].setdefault("count", mcq_count)

    out_dir = _ensure_output_dir()
    default_name = f"{_slugify(topic)}_plan_content.json"
    out_path = Path(output_path) if output_path else (out_dir / default_name)

    with Path(out_path).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"    JSON saved -> {out_path}")

    print(">>> Building PPT ...")
    try:
        ppt_path = build_ppt_from_result(data)
        print(f"    PPT saved -> {ppt_path}")
        data["_ppt_path"] = str(ppt_path)
    except Exception as e:
        print(f"    PPT generation failed: {str(e)}")
        data["_ppt_path"] = None

    data["_output_path"] = str(out_path)
    return data
