"""Generate PPT speech script as LaTeX PDF."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scholarflow.generator.latex_compiler import compile_latex
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

    tex_content = tmpl.render(
        title=_escape_latex(content.meta.title),
        authors=_escape_latex(", ".join(content.meta.authors)),
        body=_md_to_latex(script_text),
        lang=lang,
    )

    tex_path = output_dir / "script.tex"
    tex_path.write_text(tex_content, encoding="utf-8")

    try:
        return compile_latex(tex_path, output_dir)
    except RuntimeError:
        return tex_path


def _escape_latex(text: str) -> str:
    if not text:
        return ""
    for char, repl in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                        ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                        ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        text = text.replace(char, repl)
    return text


def _md_to_latex(md: str) -> str:
    """Simple Markdown-to-LaTeX conversion for the script body."""
    lines = md.split("\n")
    result = []
    for line in lines:
        if line.startswith("### "):
            heading = line[4:].strip()
            result.append(f"\\subsection*{{{_escape_latex(heading)}}}")
        elif line.startswith("## "):
            heading = line[3:].strip()
            result.append(f"\\section*{{{_escape_latex(heading)}}}")
        elif line.startswith("# "):
            heading = line[2:].strip()
            result.append(f"\\section*{{{_escape_latex(heading)}}}")
        elif line.startswith("---"):
            result.append("\\vspace{1em}\\noindent\\rule{\\textwidth}{0.4pt}\\vspace{1em}")
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            bullet = line.strip()[2:]
            result.append(f"\\begin{{itemize}}\\item {_escape_latex(bullet)}\\end{{itemize}}")
        elif line.strip():
            result.append(_escape_latex(line))
        else:
            result.append("\\vspace{0.5em}")
    return "\n".join(result)
