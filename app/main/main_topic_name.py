"""
Topic Content Generator (from Plan)
Generates comprehensive educational content based on the output from generate_plan.py
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
import app.config as cfg

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "google-generativeai is required. Install with:\n  pip install google-generativeai"
    )


# =========================
# Configuration
# =========================
GOOGLE_API_KEY = cfg.GOOGLE_API_KEY 
MODEL_NAME = cfg.LLM_MODEL_NAME 

# =========================
# System Prompt
# =========================
SYSTEM_PROMPT = """You are "Classroom Coach", an expert educational content creator.

PRINCIPLES:
- Create comprehensive, well-structured educational content
- Write in clear, engaging language appropriate to the level
- Include practical examples and real-world applications
- Make content memorable and easy to understand
- Output MUST be valid JSON matching the exact schema provided
- No extra text outside the JSON structure
"""


# =========================
# Content Generation Prompt
# =========================
def build_subtopic_prompt(
    subtopic: Dict[str, Any],
    level: str,
    style: str,
    language: str,
    main_topics: List[str]
) -> str:
    """Build prompt for generating content for a single subtopic."""
    
    learning_outcomes = "\n".join(f"- {lo}" for lo in subtopic.get("learning_outcomes", []))
    key_terms = ", ".join(subtopic.get("key_terms", []))
    examples = "\n".join(f"- {ex}" for ex in subtopic.get("suggested_examples", []))
    
    prompt = f"""
MAIN TOPICS: {', '.join(main_topics)}
SUBTOPIC: {subtopic['title']}
LEVEL: {level}
STYLE: {style}
LANGUAGE: {language}
ESTIMATED TIME: {subtopic.get('estimated_time_minutes', 30)} minutes

LEARNING OUTCOMES:
{learning_outcomes}

KEY TERMS TO COVER: {key_terms}

SUGGESTED EXAMPLES:
{examples}

Generate comprehensive educational content in JSON format with this exact schema:
{{
  "subtopic": "{subtopic['title']}",
  "level": "{level}",
  "style": "{style}",
  "language": "{language}",
  
  "notes": {{
    "introduction": "string (2-3 paragraphs introducing this subtopic)",
    "detailed_explanation": "string (comprehensive explanation, 5-8 paragraphs)",
    "key_concepts": [
      {{
        "concept": "string",
        "explanation": "string (2-3 sentences)"
      }}
    ],
    "examples": [
      {{
        "title": "string",
        "description": "string (detailed example)"
      }}
    ],
    "visual_aids_suggestions": ["string", "..."], // 2-3 suggestions for diagrams/charts
    "common_pitfalls": ["string", "..."] // 3-5 common mistakes students make
  }},
  
  "summary": {{
    "brief_overview": "string (3-4 sentences)",
    "key_takeaways": ["string", "..."], // 4-6 main points
    "connections": "string (how this connects to other topics)"
  }},
  
  "practice_questions": [
    {{
      "question": "string (open-ended question)",
      "difficulty": "easy|medium|hard",
      "hint": "string",
      "sample_answer": "string"
    }}
  ], // Generate {subtopic.get('suggested_questions', 5)} questions
  
  "mcqs": [
    {{
      "question": "string",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A|B|C|D",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }}
  ], // Generate {subtopic.get('suggested_questions', 5)} MCQs
  
  "glossary": [
    {{
      "term": "string",
      "definition": "string"
    }}
  ] // Define all key terms mentioned
}}

REQUIREMENTS:
- Cover ALL learning outcomes specified above
- Use ALL key terms in your explanations
- Include concrete examples (use suggested examples as starting points)
- Make content match the {level} level and {style} style
- Ensure practice questions test understanding of learning outcomes
- MCQs should range from easy to hard difficulty
"""
    return prompt


# =========================
# LLM Interaction
# =========================
def call_gemini(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """Call Gemini API and return the response."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-api-key-here":
        raise ValueError(
            "GOOGLE_API_KEY not set. Set it as environment variable:\n"
            "export GOOGLE_API_KEY='your-key-here'"
        )
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)
    
    response = model.generate_content(prompt)
    return (response.text or "").strip()


def sanitize_json(raw_response: str) -> Dict[str, Any]:
    """Extract and parse JSON from LLM response."""
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON block
    start = raw_response.find("{")
    end = raw_response.rfind("}")
    
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw_response[start:end + 1])
        except json.JSONDecodeError:
            pass
    
    raise ValueError("Could not parse valid JSON from LLM response.")


# =========================
# Main Generation Function
# =========================
def generate_content_from_plan(
    plan: Dict[str, Any],
    output_dir: str = "generated_content"
) -> Dict[str, Any]:
    """
    Generate comprehensive content for all subtopics in a plan.
    
    Args:
        plan: Dictionary from generate_plan.py output
        output_dir: Directory to save generated content files
        
    Returns:
        Dictionary with all generated content organized by subtopic
    """
    
    # Extract plan metadata
    level = plan.get("level", "beginner")
    style = plan.get("style", "detailed")
    language = plan.get("language", "en")
    topics = plan.get("topics", [])
    subtopics = plan.get("subtopics", [])
    
    if not subtopics:
        raise ValueError("Plan must contain at least one subtopic")
    
    print(f"🎓 Generating content from plan")
    print(f"   Topics: {', '.join(topics)}")
    print(f"   Level: {level} | Style: {style}")
    print(f"   Subtopics to generate: {len(subtopics)}\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate content for each subtopic
    all_content = {
        "plan_metadata": {
            "topics": topics,
            "level": level,
            "style": style,
            "language": language,
            "generated_at": datetime.now().isoformat(),
            "planner_notes": plan.get("planner_notes", ""),
            "overall_objectives": plan.get("overall_objectives", [])
        },
        "subtopics_content": []
    }
    
    for i, subtopic in enumerate(subtopics, 1):
        print(f"[{i}/{len(subtopics)}] Generating: {subtopic['title']}")
        print(f"   Weight: {subtopic.get('weight', 0)}% | Time: {subtopic.get('estimated_time_minutes', 0)} min")
        
        try:
            # Build prompt and call LLM
            prompt = build_subtopic_prompt(subtopic, level, style, language, topics)
            raw_response = call_gemini(prompt)
            
            # Parse response
            content = sanitize_json(raw_response)
            
            # Add metadata from plan
            content["weight"] = subtopic.get("weight", 0)
            content["estimated_time_minutes"] = subtopic.get("estimated_time_minutes", 0)
            content["learning_outcomes"] = subtopic.get("learning_outcomes", [])
            
            all_content["subtopics_content"].append(content)
            
            # Save individual subtopic file
            safe_filename = subtopic['title'].replace(" ", "_").replace("/", "-").lower()
            subtopic_file = os.path.join(output_dir, f"{i:02d}_{safe_filename}.json")
            with open(subtopic_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Generated successfully\n")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
            all_content["subtopics_content"].append({
                "error": str(e),
                "subtopic": subtopic['title']
            })
    
    # Save complete content file
    complete_file = os.path.join(output_dir, "complete_content.json")
    with open(complete_file, 'w', encoding='utf-8') as f:
        json.dump(all_content, f, indent=2, ensure_ascii=False)
    
    print(f"✅ All content generated!")
    print(f"   Output directory: {output_dir}")
    print(f"   Complete file: {complete_file}")
    
    return all_content


def generate_markdown_from_content(
    content: Dict[str, Any],
    output_file: str = "complete_content.md"
) -> str:
    """Generate a readable markdown file from the complete content."""
    
    md = []
    metadata = content.get("plan_metadata", {})
    
    # Header
    md.append(f"# {', '.join(metadata.get('topics', ['Educational Content']))}\n")
    md.append(f"**Level:** {metadata.get('level', 'N/A')} | ")
    md.append(f"**Style:** {metadata.get('style', 'N/A')} | ")
    md.append(f"**Language:** {metadata.get('language', 'en')}\n")
    md.append(f"*Generated: {metadata.get('generated_at', 'N/A')}*\n\n")
    md.append("---\n\n")
    
    # Overall objectives
    if metadata.get('overall_objectives'):
        md.append("## 🎯 Overall Learning Objectives\n\n")
        for obj in metadata['overall_objectives']:
            md.append(f"- {obj}\n")
        md.append("\n---\n\n")
    
    # Subtopics
    for i, subtopic_content in enumerate(content.get("subtopics_content", []), 1):
        if "error" in subtopic_content:
            md.append(f"## {i}. {subtopic_content.get('subtopic', 'Unknown')} ❌\n\n")
            md.append(f"*Error generating content: {subtopic_content['error']}*\n\n")
            continue
        
        title = subtopic_content.get('subtopic', f'Subtopic {i}')
        weight = subtopic_content.get('weight', 0)
        time = subtopic_content.get('estimated_time_minutes', 0)
        
        md.append(f"## {i}. {title}\n\n")
        md.append(f"**Weight:** {weight}% | **Estimated Time:** {time} minutes\n\n")
        
        # Learning Outcomes
        if subtopic_content.get('learning_outcomes'):
            md.append("### 🎯 Learning Outcomes\n\n")
            for outcome in subtopic_content['learning_outcomes']:
                md.append(f"- {outcome}\n")
            md.append("\n")
        
        # Notes
        notes = subtopic_content.get('notes', {})
        md.append("### 📚 Notes\n\n")
        
        if notes.get('introduction'):
            md.append(f"**Introduction**\n\n{notes['introduction']}\n\n")
        
        if notes.get('detailed_explanation'):
            md.append(f"**Detailed Explanation**\n\n{notes['detailed_explanation']}\n\n")
        
        if notes.get('key_concepts'):
            md.append("**Key Concepts:**\n\n")
            for concept in notes['key_concepts']:
                md.append(f"- **{concept.get('concept', '')}**: {concept.get('explanation', '')}\n")
            md.append("\n")
        
        if notes.get('examples'):
            md.append("**Examples:**\n\n")
            for ex in notes['examples']:
                md.append(f"- **{ex.get('title', '')}**: {ex.get('description', '')}\n")
            md.append("\n")
        
        # Summary
        summary = subtopic_content.get('summary', {})
        if summary.get('brief_overview'):
            md.append(f"### 📝 Summary\n\n{summary['brief_overview']}\n\n")
            
            if summary.get('key_takeaways'):
                md.append("**Key Takeaways:**\n\n")
                for takeaway in summary['key_takeaways']:
                    md.append(f"- {takeaway}\n")
                md.append("\n")
        
        # Practice Questions
        if subtopic_content.get('practice_questions'):
            md.append("### 💡 Practice Questions\n\n")
            for j, pq in enumerate(subtopic_content['practice_questions'], 1):
                md.append(f"**Q{j}. {pq.get('question', '')}** ({pq.get('difficulty', 'medium')})\n\n")
                if pq.get('hint'):
                    md.append(f"*Hint: {pq['hint']}*\n\n")
        
        # MCQs
        if subtopic_content.get('mcqs'):
            md.append("### ✓ Multiple Choice Questions\n\n")
            for j, mcq in enumerate(subtopic_content['mcqs'], 1):
                md.append(f"**Q{j}. {mcq.get('question', '')}**\n\n")
                for opt in mcq.get('options', []):
                    md.append(f"   {opt}\n")
                md.append(f"\n   **Answer:** {mcq.get('correct_answer', '')}\n")
                md.append(f"   *{mcq.get('explanation', '')}*\n\n")
        
        # Glossary
        if subtopic_content.get('glossary'):
            md.append("### 📖 Glossary\n\n")
            for term in subtopic_content['glossary']:
                md.append(f"- **{term.get('term', '')}**: {term.get('definition', '')}\n")
            md.append("\n")
        
        md.append("---\n\n")
    
    markdown_text = "".join(md)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    
    return markdown_text


# =========================
# Example Usage
# =========================
if __name__ == "__main__":
    # Example 1: Load plan from JSON file
    try:
        # Assuming you have a plan.json from generate_plan.py
        with open("plan.json", 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        # Generate content
        content = generate_content_from_plan(
            plan=plan,
            output_dir="generated_content"
        )
        
        # Generate markdown
        generate_markdown_from_content(
            content=content,
            output_file="generated_content/complete_content.md"
        )
        
        print("\n✅ All done! Check the 'generated_content' directory.")
        
    except FileNotFoundError:
        print("ℹ️  No plan.json found. Here's how to use this script:\n")
        print("Option 1: Pass a plan dictionary directly")
        print("-" * 50)
        
        # Example plan structure
        example_plan = {
            "level": "beginner",
            "style": "detailed",
            "language": "en",
            "topics": ["Introduction to Python"],
            "planner_notes": "Focus on fundamentals",
            "overall_objectives": [
                "Understand Python basics",
                "Write simple programs"
            ],
            "subtopics": [
                {
                    "title": "Python Syntax Basics",
                    "weight": 30,
                    "learning_outcomes": [
                        "Understand Python syntax",
                        "Write basic statements"
                    ],
                    "key_terms": ["variable", "print", "input"],
                    "suggested_examples": ["Hello World", "Variable assignment"],
                    "suggested_questions": 5,
                    "estimated_time_minutes": 45
                },
                {
                    "title": "Data Types",
                    "weight": 40,
                    "learning_outcomes": [
                        "Understand different data types"
                    ],
                    "key_terms": ["int", "str", "float", "bool"],
                    "suggested_examples": ["Type conversion"],
                    "suggested_questions": 6,
                    "estimated_time_minutes": 60
                },
                {
                    "title": "Control Flow",
                    "weight": 30,
                    "learning_outcomes": [
                        "Use if-else statements",
                        "Write loops"
                    ],
                    "key_terms": ["if", "else", "for", "while"],
                    "suggested_examples": ["Conditional logic", "Loop examples"],
                    "suggested_questions": 5,
                    "estimated_time_minutes": 50
                }
            ]
        }
        
        print("\nGenerating content from example plan...\n")
        content = generate_content_from_plan(
            plan=example_plan,
            output_dir="generated_content"
        )
        
        generate_markdown_from_content(
            content=content,
            output_file="generated_content/complete_content.md"
        )
        
        print("\n✅ Example content generated! Check 'generated_content' directory.")