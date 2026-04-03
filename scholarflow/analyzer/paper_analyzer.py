"""Analyze paper content with LLM to generate structured outputs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from scholarflow.analyzer.llm_client import llm_call
from scholarflow.models import AnalyzedPaper, PaperContent, SlideData
from scholarflow.parser.pdf_parser import get_figure_list_text

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _get_jinja_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(PROMPTS_DIR)), autoescape=False)


def _render_prompt(template_name: str, **kwargs) -> str:
    env = _get_jinja_env()
    tmpl = env.get_template(template_name)
    return tmpl.render(**kwargs)


def _build_paper_context(content: PaperContent) -> dict:
    """Build template context from paper content."""
    sections_text = ""
    for sec in content.sections:
        sections_text += f"\n## {sec.heading}\n{sec.text}\n"

    text_for_llm = content.full_text
    if len(text_for_llm) > 80000:
        text_for_llm = text_for_llm[:80000] + "\n... [truncated]"

    figure_list = get_figure_list_text(content.figures)

    return {
        "title": content.meta.title,
        "authors": ", ".join(content.meta.authors),
        "year": content.meta.year,
        "venue": content.meta.venue,
        "abstract": content.meta.abstract,
        "sections": sections_text,
        "full_text": text_for_llm,
        "num_pages": content.num_pages,
        "figure_list": figure_list,
    }


def analyze_for_summary(
    content: PaperContent,
    model: str = "openai/gpt-4o",
    lang: str = "zh",
    verbosity: str = "normal",
) -> tuple[str, int, str]:
    """Generate brief summary + recommendation score."""
    ctx = _build_paper_context(content)
    ctx["lang"] = lang
    ctx["verbosity"] = verbosity
    prompt = _render_prompt("summary.j2", **ctx)
    raw = llm_call(prompt, model=model)

    score = 3
    reason = ""
    score_match = re.search(r"推荐指数[：:]\s*(\d)", raw)
    if not score_match:
        score_match = re.search(r"Score[：:]\s*(\d)", raw, re.IGNORECASE)
    if score_match:
        score = int(score_match.group(1))

    reason_match = re.search(r"推荐理由[：:]\s*(.+?)(?:\n|$)", raw)
    if not reason_match:
        reason_match = re.search(r"Reason[：:]\s*(.+?)(?:\n|$)", raw, re.IGNORECASE)
    if reason_match:
        reason = reason_match.group(1).strip()

    return raw, score, reason


def analyze_for_slides(
    content: PaperContent,
    model: str = "openai/gpt-4o",
    lang: str = "zh",
    verbosity: str = "normal",
) -> list[SlideData]:
    """Generate structured slide content with figure assignments."""
    ctx = _build_paper_context(content)
    ctx["lang"] = lang
    ctx["verbosity"] = verbosity
    prompt = _render_prompt("slides_content.j2", **ctx)
    raw = llm_call(prompt, model=model, max_tokens=12000)

    slides = _parse_slides_json(raw)
    if not slides:
        slides = _parse_slides_fallback(raw)
    return slides


def analyze_for_script(
    content: PaperContent,
    slides: list[SlideData],
    model: str = "openai/gpt-4o",
    lang: str = "zh",
) -> str:
    """Generate speech script for each slide."""
    ctx = _build_paper_context(content)
    ctx["lang"] = lang
    slides_outline = ""
    for i, s in enumerate(slides, 1):
        slides_outline += f"\nSlide {i}: {s.title}\n"
        for b in s.bullets:
            slides_outline += f"  - {b}\n"
    ctx["slides_outline"] = slides_outline
    prompt = _render_prompt("script.j2", **ctx)
    return llm_call(prompt, model=model, max_tokens=12000)


def analyze_for_notes(
    content: PaperContent,
    model: str = "openai/gpt-4o",
    lang: str = "zh",
    mode: str = "deep",
) -> str:
    """Generate study notes in the given mode (deep/exam/quick/grandma)."""
    ctx = _build_paper_context(content)
    ctx["lang"] = lang
    template_name = f"notes_{mode}.j2"
    prompt = _render_prompt(template_name, **ctx)
    return llm_call(prompt, model=model, max_tokens=12000)


def analyze_for_mindmap(
    content: PaperContent,
    model: str = "openai/gpt-4o",
    lang: str = "zh",
) -> str:
    """Generate a Markmap-compatible markdown mindmap."""
    ctx = _build_paper_context(content)
    ctx["lang"] = lang
    prompt = _render_prompt("mindmap.j2", **ctx)
    return llm_call(prompt, model=model)


def analyze_for_poster(
    content: PaperContent,
    model: str = "openai/gpt-4o",
    lang: str = "zh",
) -> str:
    """Generate poster content."""
    ctx = _build_paper_context(content)
    ctx["lang"] = lang
    prompt = _render_prompt("poster.j2", **ctx)
    return llm_call(prompt, model=model, max_tokens=8000)


def analyze_for_translation(
    content: PaperContent,
    model: str = "openai/gpt-4o",
) -> str:
    """Generate bilingual summary."""
    ctx = _build_paper_context(content)
    prompt = _render_prompt("translate.j2", **ctx)
    return llm_call(prompt, model=model)


def _parse_slides_json(raw: str) -> list[SlideData]:
    json_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not json_match:
        return []
    try:
        data = json.loads(json_match.group(0))
        slides = []
        for item in data:
            slides.append(SlideData(
                title=item.get("title", ""),
                bullets=item.get("bullets", []),
                notes=item.get("notes", ""),
                figure_path=item.get("figure_path", None),
            ))
        return slides
    except (json.JSONDecodeError, TypeError):
        return []


def _parse_slides_fallback(raw: str) -> list[SlideData]:
    slides = []
    current_title = ""
    current_bullets: list[str] = []

    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("##") or line.startswith("Slide"):
            if current_title:
                slides.append(SlideData(title=current_title, bullets=current_bullets))
            current_title = re.sub(r"^#+\s*", "", line)
            current_title = re.sub(r"^Slide\s*\d+[：:.\s]*", "", current_title)
            current_bullets = []
        elif line.startswith("-") or line.startswith("*") or line.startswith("•"):
            current_bullets.append(line.lstrip("-*• ").strip())

    if current_title:
        slides.append(SlideData(title=current_title, bullets=current_bullets))

    return slides
