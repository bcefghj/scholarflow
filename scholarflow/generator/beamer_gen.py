"""Generate Beamer (LaTeX) presentation slides with embedded figures."""

from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scholarflow.generator.latex_compiler import compile_latex
from scholarflow.models import PaperContent, PaperFigure, SlideData

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

    fig_lookup: dict[str, PaperFigure] = {}
    for fig in content.figures:
        fig_lookup[fig.figure_id] = fig

    # Copy figures to output dir
    for fig in content.figures:
        if fig.path.exists():
            dest = output_dir / fig.path.name
            if not dest.exists():
                shutil.copy2(fig.path, dest)

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
        fig = _resolve_figure(s, fig_lookup)
        slide_dict = {
            "title": _escape_latex(s.title),
            "bullets": [_escape_latex(b) for b in s.bullets],
            "figure_path": fig.path.name if fig else "",
            "figure_caption": _escape_latex(fig.caption[:80]) if fig and fig.caption else "",
        }
        slides_data.append(slide_dict)

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


def _resolve_figure(slide: SlideData, fig_lookup: dict[str, PaperFigure]):
    if not slide.figure_path:
        return None
    fig_id = slide.figure_path.lower().strip()
    if fig_id in fig_lookup:
        fig = fig_lookup[fig_id]
        if fig.path.exists():
            return fig
    for fid, fig in fig_lookup.items():
        if fid in fig_id or fig_id in fid:
            if fig.path.exists():
                return fig
    return None


def _escape_latex(text: str) -> str:
    if not text:
        return ""
    result = text
    result = result.replace("\\", r"\textbackslash{}")
    for char, replacement in [
        ("&", r"\&"), ("%", r"\%"), ("#", r"\#"),
        ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
        ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
    ]:
        result = result.replace(char, replacement)
    return result
