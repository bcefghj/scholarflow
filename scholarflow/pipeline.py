"""Main pipeline: input -> parse -> analyze -> generate all outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scholarflow.analyzer.paper_analyzer import (
    analyze_for_mindmap,
    analyze_for_notes,
    analyze_for_poster,
    analyze_for_script,
    analyze_for_slides,
    analyze_for_summary,
    analyze_for_translation,
)
from scholarflow.config import SFConfig
from scholarflow.fetcher.paper_fetcher import fetch_paper
from scholarflow.generator.beamer_gen import generate_beamer
from scholarflow.generator.mindmap_gen import generate_mindmap
from scholarflow.generator.notes_gen import generate_notes
from scholarflow.generator.poster_gen import generate_poster
from scholarflow.generator.pptx_gen import generate_pptx
from scholarflow.generator.script_gen import generate_script
from scholarflow.generator.summary_gen import generate_summary
from scholarflow.generator.translate_gen import generate_translation
from scholarflow.models import AnalyzedPaper, PaperContent
from scholarflow.parser.pdf_parser import parse_pdf

console = Console()


def run_full_pipeline(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    output_dir: str = "./output",
    model: Optional[str] = None,
    lang: Optional[str] = None,
    verbosity: Optional[str] = None,
    ppt_theme: Optional[str] = None,
    beamer_theme: Optional[str] = None,
    notes_mode: str = "deep",
    generate: Optional[list[str]] = None,
) -> dict[str, Path]:
    """Run the complete pipeline and return paths to generated files.

    Args:
        generate: list of outputs to generate. None = all.
            Options: summary, slides, beamer, script, notes, mindmap, poster, translate
    """
    cfg = SFConfig.load()
    model = model or cfg.model
    lang = lang or cfg.lang
    verbosity = verbosity or cfg.verbosity
    ppt_theme = ppt_theme or cfg.ppt_theme
    beamer_theme = beamer_theme or cfg.beamer_theme

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    figures_dir = out / "figures"

    targets = set(generate) if generate else {
        "summary", "slides", "beamer", "script", "notes", "mindmap", "poster", "translate"
    }

    results: dict[str, Path] = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console,
    ) as progress:
        # Step 1: Fetch paper
        task = progress.add_task("Fetching paper...", total=None)
        local_pdf = fetch_paper(
            pdf_path=pdf_path, title=title, arxiv=arxiv, doi=doi, output_dir=out
        )
        progress.update(task, completed=True, description="[green]Paper fetched")

        # Step 2: Parse PDF
        task = progress.add_task("Parsing PDF...", total=None)
        content = parse_pdf(local_pdf, figures_dir=figures_dir)
        progress.update(task, completed=True, description="[green]PDF parsed")
        console.print(f"  Title: [bold]{content.meta.title}[/bold]")
        console.print(f"  Pages: {content.num_pages} | Sections: {len(content.sections)}")

        # Step 3: Analyze & Generate
        analyzed = AnalyzedPaper(content=content)

        if "summary" in targets:
            task = progress.add_task("Generating summary...", total=None)
            text, score, reason = analyze_for_summary(content, model, lang, verbosity)
            analyzed.summary_text = text
            analyzed.recommendation_score = score
            analyzed.recommendation_reason = reason
            results["summary"] = generate_summary(text, out)
            progress.update(task, completed=True, description="[green]Summary done")

        slides = []
        if targets & {"slides", "beamer", "script"}:
            task = progress.add_task("Generating slides...", total=None)
            slides = analyze_for_slides(content, model, lang, verbosity)
            analyzed.slides = slides
            progress.update(task, completed=True, description="[green]Slides content ready")

        if "slides" in targets and slides:
            task = progress.add_task("Building PPTX...", total=None)
            results["slides"] = generate_pptx(slides, content, out, ppt_theme)
            progress.update(task, completed=True, description="[green]PPTX done")

        if "beamer" in targets and slides:
            task = progress.add_task("Building Beamer...", total=None)
            results["beamer"] = generate_beamer(slides, content, out, beamer_theme, lang)
            progress.update(task, completed=True, description="[green]Beamer done")

        if "script" in targets and slides:
            task = progress.add_task("Generating script...", total=None)
            script_text = analyze_for_script(content, slides, model, lang)
            analyzed.script_text = script_text
            results["script"] = generate_script(script_text, content, out, lang)
            progress.update(task, completed=True, description="[green]Script done")

        if "notes" in targets:
            task = progress.add_task(f"Generating notes ({notes_mode})...", total=None)
            notes_text = analyze_for_notes(content, model, lang, notes_mode)
            analyzed.notes_text = notes_text
            results["notes"] = generate_notes(notes_text, content, out, notes_mode, lang)
            progress.update(task, completed=True, description="[green]Notes done")

        if "mindmap" in targets:
            task = progress.add_task("Generating mindmap...", total=None)
            mm = analyze_for_mindmap(content, model, lang)
            analyzed.mindmap_markdown = mm
            results["mindmap"] = generate_mindmap(mm, out, content.meta.title)
            progress.update(task, completed=True, description="[green]Mindmap done")

        if "poster" in targets:
            task = progress.add_task("Generating poster...", total=None)
            poster = analyze_for_poster(content, model, lang)
            analyzed.poster_text = poster
            results["poster"] = generate_poster(poster, content, out)
            progress.update(task, completed=True, description="[green]Poster done")

        if "translate" in targets:
            task = progress.add_task("Generating translation...", total=None)
            trans = analyze_for_translation(content, model)
            analyzed.translated_summary = trans
            results["translate"] = generate_translation(trans, out)
            progress.update(task, completed=True, description="[green]Translation done")

    console.print()
    console.print("[bold green]All done![/bold green] Generated files:")
    for name, path in results.items():
        console.print(f"  {name}: [cyan]{path}[/cyan]")

    return results


def run_scan(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    output_dir: str = "./output",
    model: Optional[str] = None,
    lang: Optional[str] = None,
    verbosity: Optional[str] = None,
) -> Path:
    """Quick scan: generate only the brief summary."""
    results = run_full_pipeline(
        pdf_path=pdf_path,
        title=title,
        arxiv=arxiv,
        doi=doi,
        output_dir=output_dir,
        model=model,
        lang=lang,
        verbosity=verbosity,
        generate=["summary"],
    )
    return results["summary"]


def run_batch(
    input_dir: str,
    output_dir: str = "./output",
    model: Optional[str] = None,
    lang: Optional[str] = None,
    notes_mode: str = "deep",
    generate: Optional[list[str]] = None,
) -> dict[str, dict[str, Path]]:
    """Process all PDFs in a directory."""
    in_path = Path(input_dir)
    if not in_path.is_dir():
        raise NotADirectoryError(f"{input_dir} is not a directory")

    pdfs = sorted(in_path.glob("*.pdf"))
    if not pdfs:
        console.print(f"[yellow]No PDF files found in {input_dir}[/yellow]")
        return {}

    console.print(f"[bold]Found {len(pdfs)} PDF files[/bold]")
    all_results = {}

    for i, pdf in enumerate(pdfs, 1):
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold]Processing [{i}/{len(pdfs)}]: {pdf.name}[/bold]")
        paper_out = Path(output_dir) / pdf.stem
        try:
            results = run_full_pipeline(
                pdf_path=str(pdf),
                output_dir=str(paper_out),
                model=model,
                lang=lang,
                notes_mode=notes_mode,
                generate=generate,
            )
            all_results[pdf.name] = results
        except Exception as e:
            console.print(f"[red]Error processing {pdf.name}: {e}[/red]")

    console.print(f"\n[bold green]Batch complete! Processed {len(all_results)}/{len(pdfs)} papers.[/bold green]")
    return all_results
