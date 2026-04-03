"""Generate PPT speech script as LaTeX PDF."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scholarflow.generator.latex_compiler import compile_latex
from scholarflow.generator.md2latex import md_to_latex

from scholarflow.models import PaperContent

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "script"


def generate_script(
    script_text: str,
    content: PaperContent,
    output_dir: Path,
    lang: str = "zh",
) -> Path:
    """Generate speech script LaTeX and compile to PDF."""
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

    body_latex = md_to_latex(script_text)

    tex_content = tmpl.render(
        title=_escape_title(content.meta.title),
        authors=_escape_title(", ".join(content.meta.authors)),
        body=body_latex,
        lang=lang,
    )

    tex_path = output_dir / "script.tex"
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
