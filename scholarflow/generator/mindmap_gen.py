"""Generate interactive mindmap as HTML using Markmap autoloader."""

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

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)
    tmpl = env.get_template("markmap.html.j2")

    cleaned = _clean_markdown(mindmap_md)
    html = tmpl.render(title=title, markdown_content=cleaned)

    out_path = output_dir / "mindmap.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _clean_markdown(md: str) -> str:
    """Ensure the markdown is valid markmap format (bullet-list hierarchy)."""
    lines = md.strip().split("\n")
    cleaned: list[str] = []
    for line in lines:
        stripped = line.rstrip()
        # Skip empty lines (markmap prefers continuous hierarchy)
        if not stripped:
            continue
        # Ensure proper indentation format (spaces + dash)
        if stripped.lstrip().startswith("- ") or stripped.lstrip().startswith("# "):
            cleaned.append(stripped)
        elif stripped.startswith("#"):
            cleaned.append(stripped)
        else:
            # Wrap bare text as a list item
            indent = len(stripped) - len(stripped.lstrip())
            cleaned.append(" " * indent + "- " + stripped.lstrip())
    return "\n".join(cleaned)
