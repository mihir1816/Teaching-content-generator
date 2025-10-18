"""
Article-specific content generator using Gemini.
Generates teaching materials directly from pre-retrieved contexts.
"""
import json
import logging
from typing import List, Dict, Any
from app.config import cfg

logger = logging.getLogger(__name__)

# Import Gemini
try:
    import google.generativeai as genai
    genai.configure(api_key=cfg.GOOGLE_API_KEY)
except Exception as e:
    logger.error(f"Failed to import Gemini SDK: {e}")


def generate_article_content(
    contexts: List[str],
    topic: str,
    level: str = "beginner",
    style: str = "detailed",
    language: str = "en",
    mcq_count: int = 10
) -> Dict[str, Any]:
    """
    Generate teaching materials from article contexts.
    
    Args:
        contexts: List of text chunks retrieved from article
        topic: One-sentence topic description
        level: Learning level (beginner/intermediate/advanced)
        style: Writing style (concise/detailed/simple)
        language: Language code
        mcq_count: Number of MCQs to generate
        
    Returns:
        Dict with notes, summary, and mcqs
    """
    if not cfg.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set")
    
    if not contexts:
        logger.warning("No contexts provided, returning empty output")
        return _create_empty_output(topic, level, language, style)
    
    # Combine contexts
    context_text = "\n\n---\n\n".join(contexts)
    total_chars = len(context_text)
    logger.info(f"Combined context: {total_chars} characters from {len(contexts)} chunks")
    
    # Truncate if too long
    max_chars = 12000
    if total_chars > max_chars:
        context_text = context_text[:max_chars] + "\n\n[... content truncated ...]"
        logger.info(f"Truncated context to {max_chars} characters")
    
    # Initialize model
    model_name = getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)
    
    # Generate each content type
    logger.info("Generating summary...")
    summary = _generate_summary(model, context_text, topic, level, style, language)
    
    logger.info("Generating notes...")
    notes = _generate_notes(model, context_text, topic, level, style, language)
    
    logger.info("Generating MCQs...")
    mcqs = _generate_mcqs(model, context_text, topic, level, style, language, mcq_count)
    
    return {
        "topic": topic,
        "level": level,
        "language": language,
        "style": style,
        "summary": summary,
        "notes": notes,
        "mcqs": mcqs
    }


def _generate_summary(model, context: str, topic: str, level: str, style: str, language: str) -> Dict[str, Any]:
    """Generate comprehensive summary from contexts."""
    prompt = f"""You are an educational content creator. Create a comprehensive summary from the following context.

TOPIC: {topic}
LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}

CONTEXT:
{context}

Generate a JSON response with:
{{
  "summary": "A detailed summary covering all key points from the context (3-5 paragraphs)",
  "key_points": ["Key point 1", "Key point 2", "Key point 3", ...]
}}

Make the summary comprehensive and educational. Include all important information from the context.
Return ONLY valid JSON, no markdown formatting."""

    try:
        response = model.generate_content(prompt)
        result = _parse_json_response(response.text)
        
        # Add metadata
        result["topic"] = topic
        result["objective"] = "summary"
        result["level"] = level
        result["language"] = language
        result["style"] = style
        
        return result
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return {
            "topic": topic,
            "objective": "summary",
            "level": level,
            "language": language,
            "style": style,
            "summary": "Error generating summary",
            "key_points": []
        }


def _generate_notes(model, context: str, topic: str, level: str, style: str, language: str) -> Dict[str, Any]:
    """Generate detailed teaching notes."""
    prompt = f"""You are an educational content creator. Create detailed teaching notes from the following context.

TOPIC: {topic}
LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}

CONTEXT:
{context}

Generate a JSON response with:
{{
  "summary": "Overview paragraph introducing the topic",
  "key_points": ["Important point 1", "Important point 2", ...],
  "sections": [
    {{
      "title": "Section Title",
      "content": "Detailed explanation of this section"
    }}
  ],
  "glossary": [
    {{
      "term": "Term",
      "definition": "Definition"
    }}
  ],
  "misconceptions": ["Common misconception 1", "Common misconception 2", ...]
}}

Make the notes comprehensive, well-structured, and educational.
Return ONLY valid JSON, no markdown formatting."""

    try:
        response = model.generate_content(prompt)
        result = _parse_json_response(response.text)
        
        # Add metadata
        result["topic"] = topic
        result["objective"] = "notes"
        result["level"] = level
        result["language"] = language
        result["style"] = style
        
        return result
    except Exception as e:
        logger.error(f"Notes generation failed: {e}")
        return {
            "topic": topic,
            "objective": "notes",
            "level": level,
            "language": language,
            "style": style,
            "summary": "Error generating notes",
            "key_points": [],
            "sections": [],
            "glossary": [],
            "misconceptions": []
        }


def _generate_mcqs(model, context: str, topic: str, level: str, style: str, language: str, count: int) -> Dict[str, Any]:
    """Generate multiple choice questions."""
    prompt = f"""You are an educational assessment creator. Create {count} multiple choice questions from the following context.

TOPIC: {topic}
LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}

CONTEXT:
{context}

Generate a JSON response with:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Why this is correct"
    }}
  ]
}}

Create exactly {count} questions that test understanding of the context.
Return ONLY valid JSON, no markdown formatting."""

    try:
        response = model.generate_content(prompt)
        result = _parse_json_response(response.text)
        
        # Add metadata
        result["topic"] = topic
        result["objective"] = "mcqs"
        result["level"] = level
        result["language"] = language
        result["style"] = style
        
        return result
    except Exception as e:
        logger.error(f"MCQ generation failed: {e}")
        return {
            "topic": topic,
            "objective": "mcqs",
            "level": level,
            "language": language,
            "style": style,
            "questions": []
        }


def _parse_json_response(text: str) -> Dict[str, Any]:
    """Parse JSON from Gemini response, handling markdown formatting."""
    # Remove markdown code blocks
    text = text.strip()
    if text.startswith("```"):
        # Remove ```json and ``` markers
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.error(f"Response text: {text[:500]}")
        return {}


def _create_empty_output(topic: str, level: str, language: str, style: str) -> Dict[str, Any]:
    """Create empty output structure when no contexts available."""
    return {
        "topic": topic,
        "level": level,
        "language": language,
        "style": style,
        "summary": {
            "topic": topic,
            "objective": "summary",
            "level": level,
            "language": language,
            "style": style,
            "summary": "No content available - no contexts retrieved",
            "key_points": []
        },
        "notes": {
            "topic": topic,
            "objective": "notes",
            "level": level,
            "language": language,
            "style": style,
            "summary": "No content available - no contexts retrieved",
            "key_points": [],
            "sections": [],
            "glossary": [],
            "misconceptions": []
        },
        "mcqs": {
            "topic": topic,
            "objective": "mcqs",
            "level": level,
            "language": language,
            "style": style,
            "questions": []
        }
    }