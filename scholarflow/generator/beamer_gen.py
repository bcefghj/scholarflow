"""Generate Beamer (LaTeX) presentation slides."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scholarflow.generator.latex_compiler import compile_latex
from scholarflow.models import PaperContent, SlideData

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "beamer"


def generate_beamer(
    slides: list[SlideData],
    content: PaperContent,
    output_dir: Path,
    theme: str = "Madrid",
    lang: str = "zh",
) -> Path:
    """Generate Beamer LaTeX slides and compile to PDF."""
    output_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
    )
    tmpl = env.get_template("base.tex.j2")

    slides_data = []
    for s in slides:
        slides_data.append({
            "title": _escape_latex(s.title),
            "bullets": [_escape_latex(b) for b in s.bullets],
        })

    tex_content = tmpl.render(
        title=_escape_latex(content.meta.title),
        authors=_escape_latex(", ".join(content.meta.authors)),
        year=content.meta.year,
        venue=_escape_latex(content.meta.venue),
        theme=theme,
        slides=slides_data,
        lang=lang,
    )

    tex_path = output_dir / "beamer.tex"
    tex_path.write_text(tex_content, encoding="utf-8")

    try:
        return compile_latex(tex_path, output_dir)
    except RuntimeError:
        return tex_path


def _escape_latex(text: str) -> str:
    if not text:
        return ""
    chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    result = text
    result = result.replace("\\", r"\textbackslash{}")
    for char, replacement in chars.items():
        result = result.replace(char, replacement)
    return result
