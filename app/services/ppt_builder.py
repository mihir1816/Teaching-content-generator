from __future__ import annotations
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import app.config as cfg

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    from pptx.dml.color import RGBColor
except Exception as e:
    raise ImportError(
        "python-pptx is required. Install with:\n  pip install python-pptx>=0.6.21"
    ) from e


# =========================
# Helpers / formatting
# =========================
def _slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "untitled"

def _ensure_outputs_dir() -> Path:
    out_dir = Path(getattr(cfg, "DATA_PATH", "data/")) / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def _as_list(x: Any) -> List[str]:
    if not x:
        return []
    if isinstance(x, str):
        return [x]
    if isinstance(x, Iterable):
        return [str(i) for i in x]
    return [str(x)]

def _trim(s: str) -> str:
    return (s or "").strip()

def _split_chunks(items: List[str], chunk_size: int) -> List[List[str]]:
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

def _shape_textframe(tf, title: bool = False):
    # Simple, clean defaults
    for p in tf.paragraphs:
        p.font.name = "Calibri"
        p.font.size = Pt(18 if not title else 40)
        p.font.color.rgb = RGBColor(25, 25, 25)

def _add_title_slide(prs: Presentation, title: str, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[0])  # Title
    slide.shapes.title.text = _trim(title) or "Untitled"
    _shape_textframe(slide.shapes.title.text_frame, title=True)
    if slide.placeholders and len(slide.placeholders) > 1:
        sub = slide.placeholders[1]
        sub.text = _trim(subtitle)
        _shape_textframe(sub.text_frame)
        for p in sub.text_frame.paragraphs:
            p.alignment = PP_ALIGN.LEFT
    return slide

def _add_title_content_slide(prs: Presentation, title: str, content: str):
    slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title & Content
    slide.shapes.title.text = _trim(title)
    _shape_textframe(slide.shapes.title.text_frame, title=True)
    body = slide.shapes.placeholders[1].text_frame
    body.clear()
    p = body.paragraphs[0]
    p.text = _trim(content)
    p.font.name = "Calibri"
    p.font.size = Pt(20)
    return slide

def _add_bullets_slide(prs: Presentation, title: str, bullets: List[str], max_per_slide: int = 8):
    # Split across slides if needed
    chunks = _split_chunks([b for b in bullets if _trim(b)], max_per_slide)
    slides = []
    for i, part in enumerate(chunks, start=1):
        t = title if len(chunks) == 1 else f"{title} (Part {i})"
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = _trim(t)
        _shape_textframe(slide.shapes.title.text_frame, title=True)
        tf = slide.shapes.placeholders[1].text_frame
        tf.clear()
        for j, bullet in enumerate(part):
            if j == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = _trim(bullet)
            p.level = 0
            p.font.name = "Calibri"
            p.font.size = Pt(20)
        slides.append(slide)
    return slides

def _add_section_slide(prs: Presentation, title: str, bullets: List[str], max_per_slide: int = 7):
    return _add_bullets_slide(prs, title, bullets, max_per_slide=max_per_slide)

def _add_table_slide(prs: Presentation, title: str, headers: List[str], rows: List[Tuple[str, str]], col_widths: Tuple[float, float] = (5.0, 7.0)):
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only
    slide.shapes.title.text = _trim(title)
    _shape_textframe(slide.shapes.title.text_frame, title=True)

    # add table
    rows_n = max(1, len(rows)) + 1  # + header
    cols_n = max(2, len(headers))
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(12.0)
    height = Inches(6.0)

    table = slide.shapes.add_table(rows_n, cols_n, left, top, width, height).table
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = _trim(h)
        _shape_textframe(cell.text_frame)
        for p in cell.text_frame.paragraphs:
            p.font.bold = True

    # set column widths
    if len(col_widths) == cols_n:
        for i, w in enumerate(col_widths):
            table.columns[i].width = Inches(w)

    for r_idx, (c1, c2) in enumerate(rows, start=1):
        table.cell(r_idx, 0).text = _trim(c1)
        table.cell(r_idx, 1).text = _trim(c2)
        _shape_textframe(table.cell(r_idx, 0).text_frame)
        _shape_textframe(table.cell(r_idx, 1).text_frame)

    return slide

def _add_mcq_slide(prs: Presentation, q: Dict[str, Any], reveal_inline: bool = True):
    stem = _trim(q.get("stem") or q.get("question") or "")
    options = _as_list(q.get("options"))
    answer = _trim(q.get("answer") or "")
    explanation = _trim(q.get("explanation") or "")

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = stem or "Question"
    _shape_textframe(slide.shapes.title.text_frame, title=True)

    tf = slide.shapes.placeholders[1].text_frame
    tf.clear()

    # options
    for i, opt in enumerate(options):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = _trim(opt)
        p.level = 0
        p.font.name = "Calibri"
        p.font.size = Pt(20)

    if reveal_inline and (answer or explanation):
        p = tf.add_paragraph()
        p.text = ""
        p.level = 0
        p = tf.add_paragraph()
        p.text = f"Answer: {answer}"
        p.font.bold = True
        p.font.size = Pt(20)
        if explanation:
            p = tf.add_paragraph()
            p.text = f"Why: {explanation}"
            p.font.size = Pt(18)

    return slide


# =========================
# Schema adapters
# =========================
def _extract_from_generate_all(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    For objects produced by app.services.generator.generate_all(...)
    """
    topic = result.get("topic") or "Untitled"
    level = result.get("level", "beginner")
    style = result.get("style", "concise")

    notes = result.get("notes") or {}
    summary = result.get("summary") or {}
    mcqs = result.get("mcqs") or {}

    overview = _trim(notes.get("summary") or summary.get("summary") or summary.get("overview") or "")
    key_points = _as_list(notes.get("key_points") or summary.get("key_points"))

    sections = []
    for sec in notes.get("sections") or []:
        title = _trim(sec.get("title") or "")
        bullets = [b for b in _as_list(sec.get("bullets")) if _trim(b)]
        if title and bullets:
            sections.append((title, bullets))

    glossary_rows = []
    for g in notes.get("glossary") or []:
        term = _trim(g.get("term") or "")
        definition = _trim(g.get("definition") or "")
        if term and definition:
            glossary_rows.append((term, definition))

    misconceptions = []
    for m in notes.get("misconceptions") or []:
        st = _trim(m.get("statement") or "")
        corr = _trim(m.get("correction") or "")
        if st and corr:
            misconceptions.append(f"{st} → {corr}")

    questions = mcqs.get("questions") or []

    return {
        "topic": topic,
        "level": level,
        "style": style,
        "overview": overview,
        "key_points": key_points,
        "sections": sections,
        "glossary_rows": glossary_rows,
        "misconceptions": misconceptions,
        "questions": questions,
    }

def _extract_from_plan_content(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    For objects produced by app.main.main_topic_name.generate_content_from_plan(...)
    """
    topic = result.get("topic") or "Untitled"
    level = result.get("level", "beginner")
    style = result.get("style", "concise")

    notes = result.get("notes") or {}
    summary = result.get("summary") or {}
    mcqs = result.get("mcqs") or {}

    overview = _trim(notes.get("summary") or summary.get("overview") or "")
    key_points = _as_list(notes.get("key_points") or summary.get("key_points"))

    sections = []
    for sec in notes.get("sections") or []:
        title = _trim(sec.get("title") or "")
        bullets = [b for b in _as_list(sec.get("bullets")) if _trim(b)]
        if title and bullets:
            sections.append((title, bullets))

    glossary_rows = []
    for g in notes.get("glossary") or []:
        term = _trim(g.get("term") or "")
        definition = _trim(g.get("definition") or "")
        if term and definition:
            glossary_rows.append((term, definition))

    misconceptions = []
    for m in notes.get("misconceptions") or []:
        st = _trim(m.get("statement") or "")
        corr = _trim(m.get("correction") or "")
        if st and corr:
            misconceptions.append(f"{st} → {corr}")

    questions = mcqs.get("questions") or []

    return {
        "topic": topic,
        "level": level,
        "style": style,
        "overview": overview,
        "key_points": key_points,
        "sections": sections,
        "glossary_rows": glossary_rows,
        "misconceptions": misconceptions,
        "questions": questions,
    }


# =========================
# Public API
# =========================
def build_ppt_from_result(result: Dict[str, Any], output_path: Optional[str] = None, reveal_answers_inline: bool = True) -> str:
    """
    Create a PowerPoint file (.pptx) from the model result dict.
    Accepts both shapes of result:
      - app.services.generator.generate_all
      - app.main.main_topic_name.generate_content_from_plan

    Returns: output file path (str)
    """
    # Normalize schema
    if "notes" in result and "summary" in result and "mcqs" in result:
        data = _extract_from_generate_all(result)
    else:
        data = _extract_from_plan_content(result)

    topic = data["topic"]
    level = data["level"]
    style = data["style"]

    prs = Presentation()

    # Title slide
    _add_title_slide(
        prs,
        title=topic,
        subtitle=f"Level: {level.title()}  •  Style: {style.replace('-', ' ').title()}"
    )

    # Overview / Summary
    if data["overview"]:
        _add_title_content_slide(prs, "Overview", data["overview"])

    # Key Points
    if data["key_points"]:
        _add_bullets_slide(prs, "Key Points", data["key_points"], max_per_slide=8)

    # Sections
    for sec_title, bullets in data["sections"]:
        _add_section_slide(prs, sec_title, bullets, max_per_slide=7)

    # Glossary as a table (term, definition)
    if data["glossary_rows"]:
        # If too many rows, split into multiple slides
        rows = data["glossary_rows"]
        for chunk in _split_chunks(rows, 10):
            _add_table_slide(
                prs,
                title="Glossary",
                headers=["Term", "Definition"],
                rows=chunk,
                col_widths=(4.0, 8.0)
            )

    # Misconceptions
    if data["misconceptions"]:
        _add_bullets_slide(prs, "Common Misconceptions", data["misconceptions"], max_per_slide=7)

    # MCQs: one per slide
    if data["questions"]:
        for q in data["questions"]:
            _add_mcq_slide(prs, q, reveal_inline=reveal_answers_inline)

    # Save
    out_dir = _ensure_outputs_dir()
    ts = time.strftime("%Y%m%d_%H%M%S")
    default_name = f"{_slugify(topic)}_{ts}.pptx"
    out_path = Path(output_path) if output_path else (out_dir / default_name)
    prs.save(str(out_path))
    return str(out_path)
