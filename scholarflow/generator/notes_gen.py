"""Generate study notes as LaTeX PDF."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scholarflow.generator.latex_compiler import compile_latex
from scholarflow.models import PaperContent

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
    }

    tex_content = tmpl.render(
        title=_escape_latex(content.meta.title),
        authors=_escape_latex(", ".join(content.meta.authors)),
        mode_label=mode_labels.get(mode, mode),
        body=_md_to_latex_notes(notes_text),
        lang=lang,
    )

    filename = f"notes_{mode}.tex"
    tex_path = output_dir / filename
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


def _md_to_latex_notes(md: str) -> str:
    """Convert Markdown notes to LaTeX, preserving math blocks."""
    lines = md.split("\n")
    result = []
    in_math = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("$$"):
            in_math = not in_math
            result.append("\\[" if in_math else "\\]")
            continue

        if in_math:
            result.append(stripped)
            continue

        if stripped.startswith("#### "):
            if in_list:
                result.append("\\end{itemize}")
                in_list = False
            result.append(f"\\paragraph{{{_escape_latex(stripped[5:])}}}")
        elif stripped.startswith("### "):
            if in_list:
                result.append("\\end{itemize}")
                in_list = False
            result.append(f"\\subsubsection*{{{_escape_latex(stripped[4:])}}}")
        elif stripped.startswith("## "):
            if in_list:
                result.append("\\end{itemize}")
                in_list = False
            result.append(f"\\subsection*{{{_escape_latex(stripped[3:])}}}")
        elif stripped.startswith("# "):
            if in_list:
                result.append("\\end{itemize}")
                in_list = False
            result.append(f"\\section*{{{_escape_latex(stripped[2:])}}}")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                result.append("\\begin{itemize}")
                in_list = True
            bullet_text = stripped[2:]
            bullet_text = _process_inline_math(bullet_text)
            result.append(f"  \\item {bullet_text}")
        elif re.match(r"^\d+\.\s", stripped):
            item = re.sub(r"^\d+\.\s", "", stripped)
            if not in_list:
                result.append("\\begin{enumerate}")
                in_list = True
            result.append(f"  \\item {_process_inline_math(item)}")
        elif stripped == "":
            if in_list:
                result.append("\\end{itemize}" if in_list else "\\end{enumerate}")
                in_list = False
            result.append("")
        else:
            if in_list:
                result.append("\\end{itemize}")
                in_list = False
            result.append(_process_inline_math(stripped))

    if in_list:
        result.append("\\end{itemize}")

    return "\n".join(result)


def _process_inline_math(text: str) -> str:
    """Keep $...$ math intact, escape the rest."""
    parts = re.split(r"(\$[^$]+\$)", text)
    processed = []
    for part in parts:
        if part.startswith("$") and part.endswith("$"):
            processed.append(part)
        else:
            processed.append(_escape_latex(part))
    return "".join(processed)
