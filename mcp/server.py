"""ScholarFlow MCP Server - expose paper processing as MCP tools."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP(
    "ScholarFlow",
    description="The ultimate academic paper processing tool. "
    "Paper PDF → summary, slides, speech script, study notes, mindmap, poster, translation.",
)


@mcp.tool()
def scan_paper(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    lang: str = "zh",
    model: Optional[str] = None,
) -> str:
    """Quick scan a paper - generate a brief summary to decide if it's worth reading.

    Provide ONE of: pdf_path (local file), title (paper title to search),
    arxiv (arXiv ID like 1706.03762), or doi.
    """
    from scholarflow.pipeline import run_scan

    path = run_scan(
        pdf_path=pdf_path, title=title, arxiv=arxiv, doi=doi,
        output_dir="./sf_output", model=model, lang=lang,
    )
    return path.read_text(encoding="utf-8")


@mcp.tool()
def generate_slides(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    lang: str = "zh",
    model: Optional[str] = None,
    format: str = "pptx",
    theme: Optional[str] = None,
) -> str:
    """Generate presentation slides from a paper.

    Args:
        format: 'pptx' for PowerPoint or 'beamer' for LaTeX Beamer PDF.
        theme: PPT theme (academic_blue/minimal_white/dark_modern) or
               Beamer theme (Madrid/Berlin/Singapore).
    """
    from scholarflow.pipeline import run_full_pipeline

    gen = ["beamer"] if format == "beamer" else ["slides"]
    results = run_full_pipeline(
        pdf_path=pdf_path, title=title, arxiv=arxiv, doi=doi,
        output_dir="./sf_output", model=model, lang=lang,
        ppt_theme=theme, beamer_theme=theme, generate=gen,
    )
    key = "beamer" if format == "beamer" else "slides"
    return f"Generated: {results[key]}"


@mcp.tool()
def generate_script(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    lang: str = "zh",
    model: Optional[str] = None,
) -> str:
    """Generate PPT speech script (LaTeX PDF) for a paper."""
    from scholarflow.pipeline import run_full_pipeline

    results = run_full_pipeline(
        pdf_path=pdf_path, title=title, arxiv=arxiv, doi=doi,
        output_dir="./sf_output", model=model, lang=lang, generate=["script"],
    )
    return f"Generated: {results['script']}"


@mcp.tool()
def generate_notes(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    lang: str = "zh",
    model: Optional[str] = None,
    mode: str = "deep",
) -> str:
    """Generate study notes (LaTeX PDF) for a paper.

    Args:
        mode: 'deep' (comprehensive), 'exam' (exam review), or 'quick' (1-2 pages).
    """
    from scholarflow.pipeline import run_full_pipeline

    results = run_full_pipeline(
        pdf_path=pdf_path, title=title, arxiv=arxiv, doi=doi,
        output_dir="./sf_output", model=model, lang=lang,
        notes_mode=mode, generate=["notes"],
    )
    return f"Generated: {results['notes']}"


@mcp.tool()
def generate_all(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    lang: str = "zh",
    model: Optional[str] = None,
    notes_mode: str = "deep",
    output_dir: str = "./sf_output",
) -> str:
    """Generate ALL outputs from a paper: summary, PPT, Beamer, script, notes, mindmap, poster, translation."""
    from scholarflow.pipeline import run_full_pipeline

    results = run_full_pipeline(
        pdf_path=pdf_path, title=title, arxiv=arxiv, doi=doi,
        output_dir=output_dir, model=model, lang=lang, notes_mode=notes_mode,
    )
    lines = ["Generated files:"]
    for name, path in results.items():
        lines.append(f"  {name}: {path}")
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
