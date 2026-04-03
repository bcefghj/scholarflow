"""Generate brief paper summary as Markdown."""

from __future__ import annotations

from pathlib import Path


def generate_summary(summary_text: str, output_dir: Path) -> Path:
    """Write summary markdown to file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "summary.md"
    out_path.write_text(summary_text, encoding="utf-8")
    return out_path
