from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

# Assuming app.config and app.services.ppt_builder exist as in your original code
import app.config as cfg
from app.services.ppt_builder import build_ppt_from_result

try:
    import google.generativeai as genai
except Exception as e:
    raise ImportError(
        "google-generativeai is required. Install with:\n  pip install google-generativeai"
    ) from e


SYSTEM_PROMPT = """You are "Classroom Coach," an expert educational content creator.

Create clear, accurate, and engaging educational content that:
- Adapts to the student's level
- Uses practical examples
- Addresses common misconceptions
- Has a supportive tone

CRITICAL: Output ONLY valid JSON matching the schema. No extra text."""

LEVEL_GUIDELINES = {
    "beginner": "Use simple language and concrete examples.",
    "intermediate": "Use standard terminology and real-world cases.",
    "advanced": "Use technical terminology and explore edge cases."
}

STYLE_GUIDELINES = {
    "concise": "Brief explanations, 4-5 key points, 2-3 sections.",
    "detailed": "Full explanations, 6-8 key points, 3-4 sections.",
    "exam-prep": "Focus on testable knowledge, exam topics."
}


def _slugify(text: str) -> str:
    """Create a clean, URL-friendly slug from text."""
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)  # Replace non-alphanumeric with -
    return re.sub(r"-+", "-", text).strip("-") or "untitled"


def _ensure_output_dir() -> Path:
    """Ensure the output directory exists and return it."""
    out_dir = Path(getattr(cfg, "DATA_PATH", "data/")) / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON from model output, handling markdown blocks and pre/post-amble text.
    """
    # 1. Look for JSON inside a markdown code block
    match = re.search(r'```(?:json)?\s*({.*})\s*```', text, re.DOTALL | re.IGNORECASE)
    
    if match:
        json_str = match.group(1)
    else:
        # 2. If no markdown, find the first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}')
        if start == -1 or end == -1 or end < start:
            raise ValueError(f"Could not find valid JSON object in response. First 500 chars:\n{text[:500]}")
        json_str = text[start : end + 1]
        
    # 3. Try to parse the extracted string
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"     JSON parse failed: {e}")
        print(f"     Attempted to parse (first 500 chars): {json_str[:500]}...")
        raise ValueError("Failed to decode JSON from extracted string.") from e


def _call_gemini(model, prompt: str, part_name: str) -> str:
    """
    Make a Gemini API call with proper error handling and text extraction.
    
    FIX: This function now *only* uses `response.parts` to extract text,
    which resolves the error: "The `response.text` quick accessor only works..."
    """
    print(f"     Generating {part_name}...")
    
    config = genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=8192,  # Increased from 2048 to prevent truncated JSON
    )
    
    safety = [
        {"category": cat, "threshold": "BLOCK_NONE"}
        for cat in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", 
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
    ]
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=config,
            safety_settings=safety
        )
        
        # --- START: ROBUST TEXT EXTRACTION ---
        # Iterate over parts to build the full text. This is the
        # correct way to avoid the `response.text` accessor error.
        if response.parts:
            full_text = ''.join(part.text for part in response.parts if hasattr(part, 'text')).strip()
            if full_text:
                return full_text
        
        # If no parts, check if the prompt was blocked
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            raise ValueError(
                f"Generation failed for {part_name} due to safety block: "
                f"{response.prompt_feedback.block_reason.name}"
            )
            
        # Fallback error if no text and no block
        raise ValueError(f"No text parts found in response for {part_name}. Response: {response}")
        # --- END: ROBUST TEXT EXTRACTION ---
            
    except Exception as e:
        print(f"     ERROR generating {part_name}: {e}")
        # Re-raise the exception to be caught by the main function
        raise


def _generate_notes(model, base_prompt: str, plan_json: str) -> Dict[str, Any]:
    """Generate notes content."""
    prompt = f"""{base_prompt}

PLAN DETAILS:
{plan_json}

Generate educational notes as JSON:
{{
  "summary": "2-3 sentence overview",
  "key_points": ["point 1", "point 2", "..."],
  "sections": [
    {{"title": "Section Name", "bullets": ["bullet 1", "bullet 2", "..."]}}
  ],
  "glossary": [
    {{"term": "Term", "definition": "Brief definition"}}
  ],
  "misconceptions": [
    {{"statement": "Common mistake", "correction": "Why it's wrong"}}
  ]
}}

Return ONLY the JSON, no other text."""

    response_text = _call_gemini(model, prompt, "notes")
    return _extract_json_from_text(response_text)


def _generate_summary(model, base_prompt: str, plan_json: str) -> Dict[str, Any]:
    """Generate summary content."""
    prompt = f"""{base_prompt}

PLAN DETAILS:
{plan_json}

Generate a summary as JSON:
{{
  "overview": "3-4 sentence overview covering main concepts",
  "key_points": ["essential point 1", "essential point 2", "..."]
}}

Return ONLY the JSON, no other text."""

    response_text = _call_gemini(model, prompt, "summary")
    return _extract_json_from_text(response_text)


def _generate_mcqs(model, base_prompt: str, plan_json: str, count: int) -> Dict[str, Any]:
    """Generate MCQ content."""
    prompt = f"""{base_prompt}

PLAN DETAILS:
{plan_json}

Generate {count} multiple choice questions as JSON:
{{
  "count": {count},
  "questions": [
    {{
      "stem": "Question text",
      "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
      "answer": "A",
      "explanation": "Why this is correct"
    }}
  ]
}}

Return ONLY the JSON, no other text."""

    response_text = _call_gemini(model, prompt, "MCQs")
    return _extract_json_from_text(response_text)


def generate_content_from_plan(
    plan: Dict[str, Any],
    output_path: Optional[str] = None,
    level: str = "beginner",
    style: str = "concise"
) -> Dict[str, Any]:
    """Generate educational content from a teacher plan using Gemini."""
    
    # Validate API key
    api_key = getattr(cfg, "GOOGLE_API_KEY", None)
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY missing in config.")

    # Extract topic info
    topics_list = plan.get("topics", [plan.get("topic", "Untitled Topic")])
    topic = ", ".join(topics_list) if topics_list else "Untitled Topic"
    language = plan.get("language", "en")
    mcq_count = min(int(plan.get("mcq_count", 8)), 10)

    print(f">>> Generating content for: {topic}")
    print(f"     Level: {level}, Style: {style}, Language: {language}")

    # Configure Gemini
    genai.configure(api_key=api_key)
    model_name = getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash")
    
    # FIX: Removed the 'system_instruction' argument from here
    model = genai.GenerativeModel(model_name) 

    # Build base prompt
    level_guide = LEVEL_GUIDELINES.get(level, LEVEL_GUIDELINES["beginner"])
    style_guide = STYLE_GUIDELINES.get(style, STYLE_GUIDELINES["concise"])
    
    # FIX: Added SYSTEM_PROMPT back to the base_prompt string
    base_prompt = f"""{SYSTEM_PROMPT}

TOPIC: {topic}
LEVEL: {level} ({level_guide})
STYLE: {style} ({style_guide})
LANGUAGE: {language}"""

    plan_json = json.dumps(plan, ensure_ascii=False, indent=2)

    # Generate content
    try:
        notes = _generate_notes(model, base_prompt, plan_json)
        summary = _generate_summary(model, base_prompt, plan_json)
        mcqs = _generate_mcqs(model, base_prompt, plan_json, mcq_count)
    except Exception as e:
        print(f"\n!!! Content generation failed: {e}")
        raise

    # Build result
    result = {
        "topic": topic,
        "topics": topics_list,
        "level": level,
        "style": style,
        "language": language,
        "notes": notes,
        "summary": summary,
        "mcqs": mcqs
    }

    # Save JSON
    out_dir = _ensure_output_dir()
    out_file = Path(output_path) if output_path else (out_dir / f"{_slugify(topic)}_content.json")
    
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"     JSON saved -> {out_file}")

    # Generate PPT
    print(">>> Building PPT...")
    try:
        ppt_path = build_ppt_from_result(result)
        print(f"     PPT saved -> {ppt_path}")
        result["_ppt_path"] = str(ppt_path)
    except Exception as e:
        print(f"     PPT generation failed: {e}")
        result["_ppt_path"] = None

    result["_output_path"] = str(out_file)
    return result