"""Compile LaTeX files to PDF using tectonic or pdflatex."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def compile_latex(tex_path: Path, output_dir: Path | None = None) -> Path:
    """Compile a .tex file to PDF. Returns the path to the generated PDF."""
    if output_dir is None:
        output_dir = tex_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("tectonic"):
        return _compile_tectonic(tex_path, output_dir)
    elif shutil.which("xelatex"):
        return _compile_xelatex(tex_path, output_dir)
    elif shutil.which("pdflatex"):
        return _compile_pdflatex(tex_path, output_dir)
    else:
        raise RuntimeError(
            "No LaTeX compiler found. Install one of:\n"
            "  - tectonic: cargo install tectonic  (recommended, no TeX Live needed)\n"
            "  - pdflatex: install TeX Live or MiKTeX\n"
            "  - xelatex: install TeX Live or MiKTeX"
        )


def _compile_tectonic(tex_path: Path, output_dir: Path) -> Path:
    result = subprocess.run(
        ["tectonic", "-o", str(output_dir), str(tex_path)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"tectonic compilation failed:\n{result.stderr}")
    pdf_name = tex_path.stem + ".pdf"
    return output_dir / pdf_name


def _compile_pdflatex(tex_path: Path, output_dir: Path) -> Path:
    for _ in range(2):
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                f"-output-directory={output_dir.resolve()}",
                tex_path.name,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(tex_path.parent.resolve()),
        )
    pdf_name = tex_path.stem + ".pdf"
    pdf_path = output_dir / pdf_name
    if not pdf_path.exists():
        raise RuntimeError(f"pdflatex failed:\n{result.stderr[-2000:]}")
    return pdf_path


def _compile_xelatex(tex_path: Path, output_dir: Path) -> Path:
    for _ in range(2):
        result = subprocess.run(
            [
                "xelatex",
                "-interaction=nonstopmode",
                f"-output-directory={output_dir.resolve()}",
                tex_path.name,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(tex_path.parent.resolve()),
        )
    pdf_name = tex_path.stem + ".pdf"
    pdf_path = output_dir / pdf_name
    if not pdf_path.exists():
        raise RuntimeError(f"xelatex failed:\n{result.stderr[-2000:]}")
    return pdf_path
