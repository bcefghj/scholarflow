"""Generate study notes as LaTeX PDF with embedded figures."""

from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scholarflow.generator.latex_compiler import compile_latex
from scholarflow.generator.md2latex import md_to_latex
from scholarflow.models import PaperContent, PaperFigure

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "notes"


def generate_notes(
    notes_text: str,
    content: PaperContent,
    output_dir: Path,
    mode: str = "deep",
    lang: str = "zh",
) -> Path:
    """Generate study notes LaTeX and compile to PDF."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy figures to output dir and build path mapping
    figure_paths = _prepare_figures(content.figures, output_dir)

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

    mode_labels = {
        "deep": "深度学习笔记" if lang == "zh" else "Deep Study Notes",
        "exam": "考试复习笔记" if lang == "zh" else "Exam Review Notes",
        "quick": "快速笔记" if lang == "zh" else "Quick Notes",
        "grandma": "老奶奶通俗讲解" if lang == "zh" else "ELI5 Grandma Explains",
    }

    body_latex = md_to_latex(notes_text, figure_paths=figure_paths)

    tex_content = tmpl.render(
        title=_escape_title(content.meta.title),
        authors=_escape_title(", ".join(content.meta.authors)),
        mode_label=mode_labels.get(mode, mode),
        body=body_latex,
        lang=lang,
    )

    filename = f"notes_{mode}.tex"
    tex_path = output_dir / filename
    tex_path.write_text(tex_content, encoding="utf-8")

    try:
        return compile_latex(tex_path, output_dir)
    except RuntimeError:
        return tex_path


def _escape_title(text: str) -> str:
    if not text:
        return ""
    for char, repl in [
        ("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
        ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
        ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
    ]:
        text = text.replace(char, repl)
    return text


def _prepare_figures(figures: list[PaperFigure], output_dir: Path) -> dict[str, str]:
    """Copy figure files to output dir; return {fig_id: relative_path}."""
    mapping: dict[str, str] = {}
    for fig in figures:
        if not fig.path.exists():
            continue
        dest = output_dir / fig.path.name
        if not dest.exists():
            shutil.copy2(fig.path, dest)
        mapping[fig.figure_id] = fig.path.name
    return mapping
