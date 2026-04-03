"""ScholarFlow CLI - The ultimate academic paper processing tool."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    name="sf",
    help="ScholarFlow - The ultimate academic paper processing tool.\n\n"
    "PDF -> Summary + PPT + Script + Notes + Mindmap + Poster + Translation",
    no_args_is_help=True,
)
console = Console()


def _input_options(
    pdf: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
) -> dict:
    """Validate and return input options."""
    if not any([pdf, title, arxiv, doi]):
        raise typer.BadParameter("Provide at least one input: PDF file, --title, --arxiv, or --doi")
    return {"pdf_path": pdf, "title": title, "arxiv": arxiv, "doi": doi}


@app.command()
def full(
    pdf: Optional[str] = typer.Argument(None, help="Path to paper PDF file"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Paper title (auto-search & download)"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a", help="arXiv ID or URL"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d", help="DOI"),
    output: str = typer.Option("./output", "--output", "-o", help="Output directory"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model (e.g. openai/gpt-4o)"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="Output language: zh or en"),
    verbosity: Optional[str] = typer.Option(None, "--verbosity", "-v", help="concise/normal/detailed"),
    theme: Optional[str] = typer.Option(None, "--theme", help="PPT theme"),
    beamer_theme: Optional[str] = typer.Option(None, "--beamer-theme", help="Beamer theme"),
    notes_mode: str = typer.Option("deep", "--notes-mode", "-n", help="Notes mode: deep/exam/quick"),
) -> None:
    """Generate ALL outputs from a paper (summary + PPT + script + notes + mindmap + poster + translation)."""
    from scholarflow.pipeline import run_full_pipeline

    inputs = _input_options(pdf, title, arxiv, doi)
    run_full_pipeline(
        **inputs,
        output_dir=output,
        model=model,
        lang=lang,
        verbosity=verbosity,
        ppt_theme=theme,
        beamer_theme=beamer_theme,
        notes_mode=notes_mode,
    )


@app.command()
def scan(
    pdf: Optional[str] = typer.Argument(None, help="Path to paper PDF file"),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
) -> None:
    """Quick scan - generate only a brief summary to decide if the paper is worth reading."""
    from scholarflow.pipeline import run_scan

    inputs = _input_options(pdf, title, arxiv, doi)
    path = run_scan(**inputs, output_dir=output, model=model, lang=lang)
    summary = path.read_text(encoding="utf-8")
    console.print()
    console.print(summary)


@app.command()
def slides(
    pdf: Optional[str] = typer.Argument(None, help="Path to paper PDF file"),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
    beamer: bool = typer.Option(False, "--beamer", help="Generate Beamer (LaTeX) instead of PPTX"),
    theme: Optional[str] = typer.Option(None, "--theme", help="Theme name"),
) -> None:
    """Generate presentation slides (PPTX or Beamer)."""
    from scholarflow.pipeline import run_full_pipeline

    inputs = _input_options(pdf, title, arxiv, doi)
    gen = ["beamer"] if beamer else ["slides"]
    run_full_pipeline(
        **inputs, output_dir=output, model=model, lang=lang,
        ppt_theme=theme, beamer_theme=theme, generate=gen,
    )


@app.command()
def script(
    pdf: Optional[str] = typer.Argument(None),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
) -> None:
    """Generate PPT speech script (LaTeX PDF)."""
    from scholarflow.pipeline import run_full_pipeline

    inputs = _input_options(pdf, title, arxiv, doi)
    run_full_pipeline(**inputs, output_dir=output, model=model, lang=lang, generate=["script"])


@app.command()
def notes(
    pdf: Optional[str] = typer.Argument(None),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
    mode: str = typer.Option("deep", "--mode", "-n", help="deep / exam / quick"),
) -> None:
    """Generate study notes (LaTeX PDF). Modes: deep, exam, quick."""
    from scholarflow.pipeline import run_full_pipeline

    inputs = _input_options(pdf, title, arxiv, doi)
    run_full_pipeline(**inputs, output_dir=output, model=model, lang=lang, notes_mode=mode, generate=["notes"])


@app.command()
def mindmap(
    pdf: Optional[str] = typer.Argument(None),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
) -> None:
    """Generate interactive mindmap (HTML)."""
    from scholarflow.pipeline import run_full_pipeline

    inputs = _input_options(pdf, title, arxiv, doi)
    run_full_pipeline(**inputs, output_dir=output, model=model, lang=lang, generate=["mindmap"])


@app.command()
def poster(
    pdf: Optional[str] = typer.Argument(None),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
) -> None:
    """Generate academic poster (HTML)."""
    from scholarflow.pipeline import run_full_pipeline

    inputs = _input_options(pdf, title, arxiv, doi)
    run_full_pipeline(**inputs, output_dir=output, model=model, lang=lang, generate=["poster"])


@app.command()
def translate(
    pdf: Optional[str] = typer.Argument(None),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    arxiv: Optional[str] = typer.Option(None, "--arxiv", "-a"),
    doi: Optional[str] = typer.Option(None, "--doi", "-d"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
) -> None:
    """Generate bilingual (Chinese + English) summary."""
    from scholarflow.pipeline import run_full_pipeline

    inputs = _input_options(pdf, title, arxiv, doi)
    run_full_pipeline(**inputs, output_dir=output, model=model, generate=["translate"])


@app.command()
def batch(
    input_dir: str = typer.Argument(..., help="Directory containing PDF files"),
    output: str = typer.Option("./output", "--output", "-o"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l"),
    notes_mode: str = typer.Option("deep", "--notes-mode", "-n"),
) -> None:
    """Batch process all PDFs in a directory."""
    from scholarflow.pipeline import run_batch

    run_batch(input_dir, output_dir=output, model=model, lang=lang, notes_mode=notes_mode)


@app.command()
def config(
    action: str = typer.Argument(..., help="set / show"),
    key: Optional[str] = typer.Argument(None, help="Config key (for 'set')"),
    value: Optional[str] = typer.Argument(None, help="Config value (for 'set')"),
) -> None:
    """Manage ScholarFlow configuration."""
    from scholarflow.config import SFConfig

    cfg = SFConfig.load()
    if action == "show":
        console.print("[bold]Current configuration:[/bold]")
        console.print(f"  model:        {cfg.model}")
        console.print(f"  lang:         {cfg.lang}")
        console.print(f"  verbosity:    {cfg.verbosity}")
        console.print(f"  ppt_theme:    {cfg.ppt_theme}")
        console.print(f"  beamer_theme: {cfg.beamer_theme}")
        console.print(f"  api_keys:     {list(cfg.api_keys.keys())}")
    elif action == "set":
        if not key or value is None:
            raise typer.BadParameter("Usage: sf config set <key> <value>")
        cfg.set_value(key, value)
        console.print(f"[green]Set {key} = {value}[/green]")
    else:
        raise typer.BadParameter("Action must be 'set' or 'show'")


if __name__ == "__main__":
    app()
