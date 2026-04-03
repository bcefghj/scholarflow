"""Extract text, figures, metadata, and structure from academic paper PDFs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from scholarflow.models import PaperContent, PaperFigure, PaperMeta, PaperSection

SECTION_HEADINGS = [
    "abstract",
    "introduction",
    "related work",
    "background",
    "method",
    "methodology",
    "approach",
    "model",
    "architecture",
    "experiment",
    "experiments",
    "results",
    "evaluation",
    "discussion",
    "analysis",
    "ablation",
    "conclusion",
    "conclusions",
    "future work",
    "acknowledgment",
    "acknowledgments",
    "acknowledgements",
    "references",
    "appendix",
]

_HEADING_RE = re.compile(
    r"^(?:\d+\.?\s*)?(" + "|".join(SECTION_HEADINGS) + r")\b",
    re.IGNORECASE,
)


def parse_pdf(pdf_path: Path, figures_dir: Optional[Path] = None) -> PaperContent:
    """Parse an academic PDF and return structured PaperContent."""
    doc = fitz.open(str(pdf_path))
    content = PaperContent(pdf_path=pdf_path, num_pages=len(doc))

    full_text_parts: list[str] = []
    for page in doc:
        full_text_parts.append(page.get_text("text"))
    content.full_text = "\n".join(full_text_parts)

    content.meta = _extract_metadata(doc, content.full_text)
    content.sections = _detect_sections(content.full_text)

    if figures_dir:
        content.figures = _extract_figures(doc, figures_dir)

    doc.close()
    return content


def _extract_metadata(doc: fitz.Document, full_text: str) -> PaperMeta:
    meta = PaperMeta()

    pdf_meta = doc.metadata or {}
    meta.title = pdf_meta.get("title", "") or ""
    meta.authors = [a.strip() for a in (pdf_meta.get("author", "") or "").split(",") if a.strip()]

    if not meta.title or len(meta.title) < 5:
        meta.title = _guess_title_from_text(full_text)

    if not meta.authors:
        meta.authors = _guess_authors_from_text(full_text)

    meta.abstract = _extract_abstract(full_text)

    year_match = re.search(r"(19|20)\d{2}", pdf_meta.get("creationDate", ""))
    if year_match:
        meta.year = year_match.group(0)

    return meta


def _guess_title_from_text(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    skip_patterns = [
        r"(?i)(provided|permission|copyright|licensed|arxiv|preprint|submitted|accepted)",
        r"(?i)(reproduce|distribution|granted|journal|work\b)",
        r"^https?://",
        r"^[\d\s\-/.,@]+$",
        r"@[a-zA-Z]",  # email addresses
    ]
    for line in lines[:20]:
        if len(line) < 8:
            continue
        if any(re.search(p, line) for p in skip_patterns):
            continue
        if not re.search(r"[A-Z]", line):
            continue
        return line
    if lines:
        return lines[0]
    return "Untitled Paper"


def _guess_authors_from_text(text: str) -> list[str]:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines[:10]):
        if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", line) and not _HEADING_RE.match(line):
            if i > 0 and len(line) > 10:
                authors = re.split(r"[,;·∗†‡\d]", line)
                authors = [a.strip() for a in authors if a.strip() and len(a.strip()) > 3]
                if 1 <= len(authors) <= 20:
                    return authors
    return []


def _extract_abstract(text: str) -> str:
    m = re.search(r"(?i)\babstract\b[.\s:—\-]*\n?(.*?)(?=\n\s*\n|\b(?:1\.?\s*)?introduction\b)", text, re.DOTALL)
    if m:
        abstract = m.group(1).strip()
        abstract = re.sub(r"\s+", " ", abstract)
        if len(abstract) > 50:
            return abstract
    return ""


def _detect_sections(text: str) -> list[PaperSection]:
    sections: list[PaperSection] = []
    lines = text.split("\n")
    current_heading = "Preamble"
    current_text: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_text.append("")
            continue

        m = _HEADING_RE.match(stripped)
        if m and len(stripped) < 80:
            if current_text:
                sections.append(PaperSection(
                    heading=current_heading,
                    text="\n".join(current_text).strip(),
                ))
            current_heading = stripped
            current_text = []
        else:
            current_text.append(stripped)

    if current_text:
        sections.append(PaperSection(
            heading=current_heading,
            text="\n".join(current_text).strip(),
        ))

    return sections


def _extract_figures(doc: fitz.Document, figures_dir: Path) -> list[PaperFigure]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    figures: list[PaperFigure] = []

    for page_num, page in enumerate(doc):
        image_list = page.get_images(full=True)
        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                w, h = pix.width, pix.height
                if w < 50 or h < 50:
                    continue

                fname = f"fig_p{page_num + 1}_{img_idx + 1}.png"
                fpath = figures_dir / fname
                pix.save(str(fpath))
                figures.append(PaperFigure(path=fpath, page=page_num + 1))
            except Exception:
                continue

    return figures
