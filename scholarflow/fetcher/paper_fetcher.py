"""Fetch paper PDFs from arXiv, Semantic Scholar, or DOI."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import requests

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_PDF = "https://arxiv.org/pdf/{arxiv_id}"
S2_API = "https://api.semanticscholar.org/graph/v1"

_ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
_DOI_RE = re.compile(r"10\.\d{4,}/[^\s]+")


def fetch_paper(
    pdf_path: Optional[str] = None,
    title: Optional[str] = None,
    arxiv: Optional[str] = None,
    doi: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Resolve any input type to a local PDF file path."""
    if pdf_path:
        p = Path(pdf_path)
        if not p.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        return p

    out = output_dir or Path(".")
    out.mkdir(parents=True, exist_ok=True)

    if arxiv:
        return _fetch_arxiv(arxiv, out)
    if doi:
        return _fetch_by_doi(doi, out)
    if title:
        return _fetch_by_title(title, out)

    raise ValueError("Provide at least one of: pdf_path, title, arxiv, doi")


def _extract_arxiv_id(raw: str) -> str:
    m = _ARXIV_ID_RE.search(raw)
    if m:
        return m.group(1)
    return raw.strip().rstrip("/").split("/")[-1]


def _fetch_arxiv(raw: str, out: Path) -> Path:
    arxiv_id = _extract_arxiv_id(raw)
    dest = out / f"{arxiv_id.replace('/', '_')}.pdf"
    if dest.exists():
        return dest

    url = ARXIV_PDF.format(arxiv_id=arxiv_id)
    resp = requests.get(url, timeout=60, allow_redirects=True)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest


def _fetch_by_doi(doi: str, out: Path) -> Path:
    m = _DOI_RE.search(doi)
    doi_clean = m.group(0) if m else doi

    if "arxiv" in doi_clean.lower():
        arxiv_id = doi_clean.split("arXiv.")[-1] if "arXiv." in doi_clean else doi_clean
        return _fetch_arxiv(arxiv_id, out)

    pdf_url = _s2_find_pdf(query=None, doi=doi_clean)
    if pdf_url:
        return _download_pdf(pdf_url, out, doi_clean.replace("/", "_"))

    raise RuntimeError(
        f"Cannot find open-access PDF for DOI {doi_clean}. Please provide the PDF file directly."
    )


def _fetch_by_title(title: str, out: Path) -> Path:
    arxiv_result = _search_arxiv(title)
    if arxiv_result:
        return _fetch_arxiv(arxiv_result, out)

    pdf_url = _s2_find_pdf(query=title)
    if pdf_url:
        safe_name = re.sub(r"[^\w\s-]", "", title)[:60].strip().replace(" ", "_")
        return _download_pdf(pdf_url, out, safe_name)

    raise RuntimeError(
        f"Cannot find open-access PDF for '{title}'. Please provide the PDF file directly."
    )


def _search_arxiv(title: str) -> Optional[str]:
    params = {
        "search_query": f'ti:"{title}"',
        "max_results": 3,
        "sortBy": "relevance",
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=15)
        resp.raise_for_status()
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(resp.text)
        for entry in root.findall("atom:entry", ns):
            entry_title = entry.find("atom:title", ns)
            if entry_title is not None:
                entry_id = entry.find("atom:id", ns)
                if entry_id is not None:
                    arxiv_id = entry_id.text.strip().split("/abs/")[-1]
                    return arxiv_id
    except Exception:
        pass
    return None


def _s2_find_pdf(query: Optional[str] = None, doi: Optional[str] = None) -> Optional[str]:
    try:
        if doi:
            url = f"{S2_API}/paper/DOI:{doi}?fields=openAccessPdf"
            resp = requests.get(url, timeout=15)
        elif query:
            url = f"{S2_API}/paper/search?query={requests.utils.quote(query)}&limit=3&fields=openAccessPdf"
            resp = requests.get(url, timeout=15)
        else:
            return None

        resp.raise_for_status()
        data = resp.json()

        if "openAccessPdf" in data and data["openAccessPdf"]:
            return data["openAccessPdf"]["url"]

        if "data" in data:
            for paper in data["data"]:
                oa = paper.get("openAccessPdf")
                if oa and oa.get("url"):
                    return oa["url"]
    except Exception:
        pass
    return None


def _download_pdf(url: str, out: Path, name: str) -> Path:
    dest = out / f"{name}.pdf"
    if dest.exists():
        return dest
    resp = requests.get(url, timeout=60, allow_redirects=True)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest
