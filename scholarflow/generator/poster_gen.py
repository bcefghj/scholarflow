"""Generate academic poster as HTML with embedded figures."""

from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scholarflow.models import PaperContent, PaperFigure
from scholarflow.parser.pdf_parser import figure_to_base64

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "poster"


def generate_poster(
    poster_text: str,
    content: PaperContent,
    output_dir: Path,
) -> Path:
    """Generate an A0 landscape academic poster HTML file with figures."""
    output_dir.mkdir(parents=True, exist_ok=True)

    poster_data = _parse_poster_json(poster_text)

    # Embed figures as base64
    figure_data_uris: list[dict] = []
    for fig in content.figures[:6]:  # max 6 figures in poster
        if fig.path.exists():
            figure_data_uris.append({
                "src": figure_to_base64(fig),
                "caption": fig.caption or f"Figure ({fig.figure_id})",
            })

    poster_data["figures"] = figure_data_uris
    poster_data.setdefault("title", content.meta.title)
    poster_data.setdefault("authors", ", ".join(content.meta.authors))

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    tmpl = env.get_template("a0_landscape.html.j2")

    html = tmpl.render(**poster_data)

    out_path = output_dir / "poster.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _parse_poster_json(text: str) -> dict:
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return {
        "title": "Paper Title",
        "authors": "Authors",
        "affiliation": "",
        "introduction": text[:500] if text else "",
        "problem": "",
        "method": "",
        "method_points": [],
        "results": "",
        "result_points": [],
        "conclusion": "",
        "references": [],
    }
