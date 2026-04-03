"""Generate interactive mindmap as HTML using Markmap."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "mindmap"


def generate_mindmap(
    mindmap_md: str,
    output_dir: Path,
    title: str = "",
) -> Path:
    """Generate an interactive Markmap HTML file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    tmpl = env.get_template("markmap.html.j2")

    html = tmpl.render(title=title, markdown_content=mindmap_md)

    out_path = output_dir / "mindmap.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
