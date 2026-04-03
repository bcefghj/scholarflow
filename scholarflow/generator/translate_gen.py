"""Generate bilingual (Chinese + English) summary."""

from __future__ import annotations

from pathlib import Path


def generate_translation(translated_text: str, output_dir: Path) -> Path:
    """Write bilingual summary to markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "translate.md"
    out_path.write_text(translated_text, encoding="utf-8")
    return out_path
