"""Extract text, figures, metadata, and structure from academic paper PDFs."""

from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from scholarflow.models import PaperContent, PaperFigure, PaperMeta, PaperSection

SECTION_HEADINGS = [
    "abstract", "introduction", "related work", "background",
    "method", "methodology", "approach", "model", "architecture",
    "experiment", "experiments", "results", "evaluation",
    "discussion", "analysis", "ablation",
    "conclusion", "conclusions", "future work",
    "acknowledgment", "acknowledgments", "acknowledgements",
    "references", "appendix",
]

_HEADING_RE = re.compile(
    r"^(?:\d+\.?\s*)?(" + "|".join(SECTION_HEADINGS) + r")\b",
    re.IGNORECASE,
)

# Pattern to match "Figure N" captions in the text
_FIGURE_CAPTION_RE = re.compile(
    r"(?:Figure|Fig\.?)\s*(\d+)[.:]\s*(.*?)(?:\n\n|\n(?=[A-Z0-9]))",
    re.IGNORECASE | re.DOTALL,
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
        figures_dir.mkdir(parents=True, exist_ok=True)
        content.figures = _extract_figures_advanced(doc, figures_dir, content.full_text)

    doc.close()
    return content


def _extract_metadata(doc: fitz.Document, full_text: str) -> PaperMeta:
    meta = PaperMeta()

    pdf_meta = doc.metadata or {}
    meta.title = pdf_meta.get("title", "") or ""
    meta.authors = [
        a.strip()
        for a in (pdf_meta.get("author", "") or "").split(",")
        if a.strip()
    ]

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
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    skip_patterns = [
        r"(?i)(provided|permission|copyright|licensed|arxiv|preprint|submitted|accepted)",
        r"(?i)(reproduce|distribution|granted|journal|work\b)",
        r"^https?://",
        r"^[\d\s\-/.,@]+$",
        r"@[a-zA-Z]",
    ]
    for line in lines[:20]:
        if len(line) < 8:
            continue
        if any(re.search(p, line) for p in skip_patterns):
            continue
        if not re.search(r"[A-Z]", line):
            continue
        return line
    return lines[0] if lines else "Untitled Paper"


def _guess_authors_from_text(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for i, line in enumerate(lines[:10]):
        if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", line) and not _HEADING_RE.match(line):
            if i > 0 and len(line) > 10:
                authors = re.split(r"[,;·∗†‡\d]", line)
                authors = [a.strip() for a in authors if a.strip() and len(a.strip()) > 3]
                if 1 <= len(authors) <= 20:
                    return authors
    return []


def _extract_abstract(text: str) -> str:
    m = re.search(
        r"(?i)\babstract\b[.\s:—\-]*\n?(.*?)(?=\n\s*\n|\b(?:1\.?\s*)?introduction\b)",
        text,
        re.DOTALL,
    )
    if m:
        abstract = re.sub(r"\s+", " ", m.group(1).strip())
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
                sections.append(
                    PaperSection(heading=current_heading, text="\n".join(current_text).strip())
                )
            current_heading = stripped
            current_text = []
        else:
            current_text.append(stripped)

    if current_text:
        sections.append(
            PaperSection(heading=current_heading, text="\n".join(current_text).strip())
        )
    return sections


def _extract_captions(full_text: str) -> dict[int, str]:
    """Extract figure captions mapped by figure number."""
    captions: dict[int, str] = {}
    for m in _FIGURE_CAPTION_RE.finditer(full_text):
        fig_num = int(m.group(1))
        caption_text = re.sub(r"\s+", " ", m.group(2).strip())
        if fig_num not in captions or len(caption_text) > len(captions[fig_num]):
            captions[fig_num] = caption_text
    return captions


def _extract_figures_advanced(
    doc: fitz.Document, figures_dir: Path, full_text: str
) -> list[PaperFigure]:
    """Extract figures using two strategies and match with captions."""
    captions = _extract_captions(full_text)
    figures: list[PaperFigure] = []

    # --- Strategy 1: Extract embedded images via xref ---
    seen_xrefs: set[int] = set()
    embedded_count = 0
    for page_num, page in enumerate(doc):
        image_list = page.get_images(full=True)
        for img_info in image_list:
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                w, h = pix.width, pix.height
                # Filter small icons / logos (< 100px either side)
                if w < 100 or h < 80:
                    continue
                # Filter very narrow strips (aspect > 10)
                aspect = max(w, h) / max(min(w, h), 1)
                if aspect > 10:
                    continue

                embedded_count += 1
                fname = f"fig{embedded_count}_p{page_num + 1}.png"
                fpath = figures_dir / fname
                pix.save(str(fpath))

                caption = captions.get(embedded_count, "")
                figures.append(PaperFigure(
                    path=fpath,
                    caption=caption,
                    page=page_num + 1,
                    figure_id=f"fig{embedded_count}",
                    width=w,
                    height=h,
                ))
            except Exception:
                continue

    # --- Strategy 2: Render full pages as high-res PNG (fallback) ---
    # If we got very few embedded images, render each page
    if len(figures) < 2:
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for clarity
            pix = page.get_pixmap(matrix=mat)
            fname = f"page_{page_num + 1}.png"
            fpath = figures_dir / fname
            pix.save(str(fpath))

            page_figs = []
            for fig_num, cap in captions.items():
                if not any(f.figure_id == f"fig{fig_num}" for f in figures):
                    page_figs.append((fig_num, cap))

            if page_figs and page_num == 0:
                for fig_num, cap in sorted(page_figs):
                    figures.append(PaperFigure(
                        path=fpath,
                        caption=cap,
                        page=page_num + 1,
                        figure_id=f"fig{fig_num}",
                        width=pix.width,
                        height=pix.height,
                    ))

    # Sort by figure_id order
    figures.sort(key=lambda f: f.figure_id)
    return figures


def get_figure_list_text(figures: list[PaperFigure]) -> str:
    """Format figure information for inclusion in LLM prompts."""
    if not figures:
        return "No figures extracted."
    lines = []
    for fig in figures:
        cap = fig.caption or "(no caption)"
        lines.append(f"[{fig.figure_id.upper()}] Page {fig.page}: {cap}")
    return "\n".join(lines)


def figure_to_base64(fig: PaperFigure) -> str:
    """Convert a figure file to base64 data URI."""
    data = fig.path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"
