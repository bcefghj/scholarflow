"""Robust Markdown -> LaTeX converter for ScholarFlow.

Handles: headings, bold, italic, code, tables, blockquotes, horizontal rules,
lists (ordered + unordered), math blocks ($...$, $$...$$), and figure
placeholders like [FIGURE:fig1].
"""

from __future__ import annotations

import re


_FIGURE_PLACEHOLDER_RE = re.compile(r"\[FIGURE:(fig\d+)\]", re.IGNORECASE)


def md_to_latex(md: str, figure_paths: dict[str, str] | None = None) -> str:
    """Convert Markdown text to LaTeX body content.

    Args:
        md: Markdown source text.
        figure_paths: Optional mapping of figure_id -> absolute file path
                      for embedding \\includegraphics.
    """
    if figure_paths is None:
        figure_paths = {}

    # Protect math blocks from processing
    math_blocks: list[str] = []
    inline_maths: list[str] = []

    def _save_display_math(m: re.Match) -> str:
        math_blocks.append(m.group(1))
        return f"%%DISPLAYMATH{len(math_blocks) - 1}%%"

    def _save_inline_math(m: re.Match) -> str:
        inline_maths.append(m.group(1))
        return f"%%INLINEMATH{len(inline_maths) - 1}%%"

    text = re.sub(r"\$\$(.*?)\$\$", _save_display_math, md, flags=re.DOTALL)
    text = re.sub(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", _save_inline_math, text)

    lines = text.split("\n")
    result: list[str] = []
    in_itemize = False
    in_enumerate = False
    in_code_block = False
    in_table = False
    table_rows: list[list[str]] = []
    table_header_done = False

    def _close_list():
        nonlocal in_itemize, in_enumerate
        if in_itemize:
            result.append("\\end{itemize}")
            in_itemize = False
        if in_enumerate:
            result.append("\\end{enumerate}")
            in_enumerate = False

    def _close_table():
        nonlocal in_table, table_rows, table_header_done
        if not in_table:
            return
        if table_rows:
            ncols = max(len(r) for r in table_rows)
            col_spec = "|" + "l|" * ncols
            result.append("\\begin{center}")
            result.append(f"\\begin{{tabular}}{{{col_spec}}}")
            result.append("\\hline")
            for i, row in enumerate(table_rows):
                while len(row) < ncols:
                    row.append("")
                cells = " & ".join(_escape_and_format(c) for c in row)
                result.append(f"{cells} \\\\")
                result.append("\\hline")
            result.append("\\end{tabular}")
            result.append("\\end{center}")
        in_table = False
        table_rows = []
        table_header_done = False

    for line in lines:
        stripped = line.strip()

        # Code blocks
        if stripped.startswith("```"):
            if in_code_block:
                result.append("\\end{verbatim}")
                in_code_block = False
            else:
                _close_list()
                _close_table()
                result.append("\\begin{verbatim}")
                in_code_block = True
            continue

        if in_code_block:
            result.append(line)
            continue

        # Empty line
        if not stripped:
            _close_list()
            _close_table()
            result.append("")
            continue

        # Table: lines containing |
        if "|" in stripped and not stripped.startswith("#"):
            # Check if it's a separator line like |---|---|
            if re.match(r"^\|?\s*[-:]+\s*(\|\s*[-:]+\s*)*\|?\s*$", stripped):
                table_header_done = True
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                _close_list()
                in_table = True
                table_rows = []
                table_header_done = False
            table_rows.append(cells)
            continue

        if in_table:
            _close_table()

        # Figure placeholder: [FIGURE:fig1]
        fig_match = _FIGURE_PLACEHOLDER_RE.search(stripped)
        if fig_match:
            _close_list()
            fig_id = fig_match.group(1).lower()
            if fig_id in figure_paths:
                fpath = figure_paths[fig_id].replace("\\", "/")
                result.append("\\begin{figure}[htbp]")
                result.append("\\centering")
                result.append(f"\\includegraphics[width=0.8\\textwidth]{{{fpath}}}")
                result.append("\\end{figure}")
            continue

        # Headings
        if stripped.startswith("#### "):
            _close_list()
            result.append(f"\\paragraph{{{_escape_and_format(stripped[5:])}}}")
            continue
        if stripped.startswith("### "):
            _close_list()
            result.append(f"\\subsubsection*{{{_escape_and_format(stripped[4:])}}}")
            continue
        if stripped.startswith("## "):
            _close_list()
            result.append(f"\\subsection*{{{_escape_and_format(stripped[3:])}}}")
            continue
        if stripped.startswith("# "):
            _close_list()
            result.append(f"\\section*{{{_escape_and_format(stripped[2:])}}}")
            continue

        # Horizontal rule
        if re.match(r"^[-*_]{3,}\s*$", stripped):
            _close_list()
            result.append("\\vspace{0.5em}\\noindent\\rule{\\textwidth}{0.4pt}\\vspace{0.5em}")
            continue

        # Blockquote
        if stripped.startswith("> "):
            _close_list()
            quote_text = _escape_and_format(stripped[2:])
            result.append("\\begin{quote}")
            result.append(f"\\textit{{{quote_text}}}")
            result.append("\\end{quote}")
            continue

        # Unordered list
        if re.match(r"^[-*+]\s", stripped):
            if in_enumerate:
                result.append("\\end{enumerate}")
                in_enumerate = False
            if not in_itemize:
                result.append("\\begin{itemize}")
                in_itemize = True
            bullet_text = re.sub(r"^[-*+]\s", "", stripped)
            result.append(f"  \\item {_escape_and_format(bullet_text)}")
            continue

        # Ordered list
        ol_match = re.match(r"^(\d+)\.\s(.+)", stripped)
        if ol_match:
            if in_itemize:
                result.append("\\end{itemize}")
                in_itemize = False
            if not in_enumerate:
                result.append("\\begin{enumerate}")
                in_enumerate = True
            result.append(f"  \\item {_escape_and_format(ol_match.group(2))}")
            continue

        # Regular paragraph
        _close_list()
        result.append(_escape_and_format(stripped))

    _close_list()
    _close_table()

    output = "\n".join(result)

    # Restore math blocks
    for i, block in enumerate(math_blocks):
        output = output.replace(f"%%DISPLAYMATH{i}%%", f"\\[\n{block}\n\\]")
    for i, expr in enumerate(inline_maths):
        output = output.replace(f"%%INLINEMATH{i}%%", f"${expr}$")

    return output


def _escape_latex(text: str) -> str:
    """Escape LaTeX special characters, preserving math placeholders."""
    if not text:
        return ""
    text = text.replace("\\", "\\textbackslash{}")
    for char, repl in [
        ("&", r"\&"), ("%", r"\%"), ("#", r"\#"),
        ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
        ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
    ]:
        text = text.replace(char, repl)
    return text


def _escape_and_format(text: str) -> str:
    """Escape LaTeX special chars AND convert inline bold/italic/code."""
    # Process inline code first (before escaping)
    segments: list[str] = []
    parts = re.split(r"(`[^`]+`)", text)
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            code_content = part[1:-1]
            segments.append(f"\\texttt{{{_escape_latex(code_content)}}}")
        else:
            segments.append(part)
    text = "".join(segments)

    # Process bold: **text** or __text__
    def _bold_replace(m: re.Match) -> str:
        return f"\\textbf{{{_escape_latex(m.group(1))}}}"

    text = re.sub(r"\*\*(.+?)\*\*", _bold_replace, text)
    text = re.sub(r"__(.+?)__", _bold_replace, text)

    # Process italic: *text* or _text_
    def _italic_replace(m: re.Match) -> str:
        return f"\\textit{{{_escape_latex(m.group(1))}}}"

    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", _italic_replace, text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", _italic_replace, text)

    # Escape remaining special chars (skip already-processed LaTeX commands)
    final_parts = re.split(r"(\\text(?:bf|it|tt|backslash)\{[^}]*\}|%%\w+\d+%%)", text)
    result = []
    for p in final_parts:
        if re.match(r"\\text(?:bf|it|tt|backslash)\{", p) or p.startswith("%%"):
            result.append(p)
        else:
            result.append(_escape_latex(p))
    return "".join(result)
