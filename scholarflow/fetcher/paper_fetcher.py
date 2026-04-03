"""Fetch paper PDFs via Semantic Scholar, OpenAlex, Unpaywall, CrossRef with arXiv mirror fallback."""

from __future__ import annotations

import logging
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import requests

log = logging.getLogger(__name__)

# arXiv mirrors — tried with very short timeouts; most are blocked in China
ARXIV_PDF_MIRRORS = [
    "https://export.arxiv.org/pdf/{arxiv_id}.pdf",
    "https://arxiv.org/pdf/{arxiv_id}.pdf",
]

S2_API = "https://api.semanticscholar.org/graph/v1"
OPENALEX_API = "https://api.openalex.org/works"
CROSSREF_API = "https://api.crossref.org/works"
UNPAYWALL_EMAIL = "scholarflow@example.com"

_ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
_DOI_RE = re.compile(r"10\.\d{4,}/[^\s]+")

_SESSION = requests.Session()
_SESSION.headers["User-Agent"] = "ScholarFlow/0.2 (academic-tool; mailto:scholarflow@example.com)"


def _get(url: str, timeout: int = 15, retries: int = 1, **kwargs) -> requests.Response:
    """GET with retry. Short timeouts to fail fast on unreachable hosts."""
    last_exc = None
    for attempt in range(retries):
        try:
            resp = _SESSION.get(url, timeout=timeout, allow_redirects=True, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            last_exc = e
            log.warning("GET %s attempt %d failed: %s", url, attempt + 1, e)
            if attempt < retries - 1:
                time.sleep(0.5)
    raise last_exc  # type: ignore[misc]


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


# ── arXiv fetch: API-first strategy ─────────────────────────

def _fetch_arxiv(raw: str, out: Path) -> Path:
    """Fetch arXiv paper. Uses API sources first (reliable in China), direct mirrors last."""
    arxiv_id = _extract_arxiv_id(raw)
    dest = out / f"{arxiv_id.replace('/', '_')}.pdf"
    if dest.exists():
        return dest

    # Strategy 1: Semantic Scholar ARXIV lookup (fast, works in China)
    pdf_url = _s2_find_pdf_by_arxiv(arxiv_id)
    if pdf_url:
        try:
            return _download_pdf(pdf_url, out, arxiv_id.replace("/", "_"))
        except Exception as e:
            log.warning("S2 PDF download failed: %s", e)

    # Strategy 2: OpenAlex DOI lookup for arXiv
    pdf_url = _openalex_find_pdf(doi=f"10.48550/arXiv.{arxiv_id}")
    if pdf_url:
        try:
            return _download_pdf(pdf_url, out, arxiv_id.replace("/", "_"))
        except Exception as e:
            log.warning("OpenAlex PDF download failed: %s", e)

    # Strategy 3: Unpaywall via arXiv DOI
    pdf_url = _unpaywall_find_pdf(f"10.48550/arXiv.{arxiv_id}")
    if pdf_url:
        try:
            return _download_pdf(pdf_url, out, arxiv_id.replace("/", "_"))
        except Exception as e:
            log.warning("Unpaywall PDF download failed: %s", e)

    # Strategy 4: Direct arXiv mirrors (often blocked in China, short timeout)
    for mirror_tpl in ARXIV_PDF_MIRRORS:
        url = mirror_tpl.format(arxiv_id=arxiv_id)
        try:
            resp = _get(url, timeout=8, retries=1)
            if len(resp.content) > 1000:
                dest.write_bytes(resp.content)
                log.info("Downloaded arXiv %s from mirror %s", arxiv_id, url)
                return dest
        except requests.RequestException as e:
            log.warning("Mirror %s failed: %s", url, e)
            continue

    raise RuntimeError(
        f"无法获取 arXiv 论文 {arxiv_id}，所有来源均失败。请直接上传 PDF 文件。"
    )


def _fetch_by_doi(doi: str, out: Path) -> Path:
    m = _DOI_RE.search(doi)
    doi_clean = m.group(0) if m else doi

    if "arxiv" in doi_clean.lower():
        arxiv_id = doi_clean.split("arXiv.")[-1] if "arXiv." in doi_clean else doi_clean
        return _fetch_arxiv(arxiv_id, out)

    safe_name = doi_clean.replace("/", "_")

    for finder in [
        lambda: _s2_find_pdf(doi=doi_clean),
        lambda: _openalex_find_pdf(doi=doi_clean),
        lambda: _unpaywall_find_pdf(doi_clean),
    ]:
        try:
            pdf_url = finder()
            if pdf_url:
                return _download_pdf(pdf_url, out, safe_name)
        except Exception as e:
            log.warning("DOI finder failed: %s", e)

    raise RuntimeError(
        f"无法找到 DOI {doi_clean} 的开放获取 PDF。请直接上传 PDF 文件。"
    )


def _fetch_by_title(title: str, out: Path) -> Path:
    safe_name = re.sub(r"[^\w\s-]", "", title)[:60].strip().replace(" ", "_")

    # Try API-based searches first (more reliable in China)
    for finder in [
        lambda: _s2_find_pdf(query=title),
        lambda: _openalex_find_pdf(query=title),
        lambda: _crossref_to_pdf(title),
    ]:
        try:
            pdf_url = finder()
            if pdf_url:
                return _download_pdf(pdf_url, out, safe_name)
        except Exception as e:
            log.warning("Title finder failed: %s", e)

    # Last resort: arXiv API search -> fetch
    arxiv_result = _search_arxiv(title)
    if arxiv_result:
        try:
            return _fetch_arxiv(arxiv_result, out)
        except RuntimeError:
            log.warning("arXiv fetch also failed after search hit")

    raise RuntimeError(
        f"无法找到论文 '{title}' 的 PDF。请直接上传 PDF 文件。"
    )


# ── arXiv API search ─────────────────────────────────────────

def _search_arxiv(title: str) -> Optional[str]:
    """Search arXiv API by title. May time out in China."""
    params = {
        "search_query": f'ti:"{title}"',
        "max_results": 3,
        "sortBy": "relevance",
    }
    try:
        resp = _get("https://export.arxiv.org/api/query", timeout=10, retries=1, params=params)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(resp.text)
        for entry in root.findall("atom:entry", ns):
            entry_id = entry.find("atom:id", ns)
            if entry_id is not None:
                arxiv_id = entry_id.text.strip().split("/abs/")[-1]
                return arxiv_id
    except Exception as e:
        log.warning("arXiv API search failed: %s", e)
    return None


# ── Semantic Scholar ─────────────────────────────────────────

def _s2_find_pdf(query: Optional[str] = None, doi: Optional[str] = None) -> Optional[str]:
    try:
        if doi:
            url = f"{S2_API}/paper/DOI:{doi}?fields=openAccessPdf"
        elif query:
            url = f"{S2_API}/paper/search?query={requests.utils.quote(query)}&limit=3&fields=openAccessPdf"
        else:
            return None

        resp = _get(url, timeout=12, retries=1)
        data = resp.json()

        pdf_url = _extract_s2_pdf(data)
        if pdf_url:
            return pdf_url

        for paper in data.get("data", []):
            pdf_url = _extract_s2_pdf(paper)
            if pdf_url:
                return pdf_url
    except Exception as e:
        log.warning("Semantic Scholar lookup failed: %s", e)
    return None


def _s2_find_pdf_by_arxiv(arxiv_id: str) -> Optional[str]:
    try:
        url = f"{S2_API}/paper/ARXIV:{arxiv_id}?fields=openAccessPdf"
        resp = _get(url, timeout=12, retries=1)
        return _extract_s2_pdf(resp.json())
    except Exception as e:
        log.warning("S2 arXiv lookup failed: %s", e)
    return None


def _extract_s2_pdf(data: dict) -> Optional[str]:
    oa = data.get("openAccessPdf")
    if oa and isinstance(oa, dict) and oa.get("url"):
        return oa["url"]
    return None


# ── OpenAlex ─────────────────────────────────────────────────

def _openalex_find_pdf(query: Optional[str] = None, doi: Optional[str] = None) -> Optional[str]:
    try:
        params: dict = {"per_page": 3, "mailto": UNPAYWALL_EMAIL}
        if doi:
            params["filter"] = f"doi:{doi}"
        elif query:
            params["search"] = query
            params["filter"] = "open_access.is_oa:true"
            params["sort"] = "cited_by_count:desc"
        else:
            return None

        resp = _get(OPENALEX_API, timeout=12, retries=1, params=params)
        for work in resp.json().get("results", []):
            oa = work.get("open_access", {})
            oa_url = oa.get("oa_url")
            if oa_url:
                return oa_url
            best_loc = work.get("best_oa_location", {})
            if best_loc:
                pdf_url = best_loc.get("pdf_url") or best_loc.get("landing_page_url")
                if pdf_url:
                    return pdf_url
    except Exception as e:
        log.warning("OpenAlex lookup failed: %s", e)
    return None


# ── Unpaywall ────────────────────────────────────────────────

def _unpaywall_find_pdf(doi: str) -> Optional[str]:
    try:
        url = f"https://api.unpaywall.org/v2/{doi}"
        resp = _get(url, timeout=12, retries=1, params={"email": UNPAYWALL_EMAIL})
        data = resp.json()
        if data.get("is_oa"):
            loc = data.get("best_oa_location", {})
            return loc.get("url_for_pdf") or loc.get("url")
    except Exception as e:
        log.warning("Unpaywall lookup failed: %s", e)
    return None


# ── CrossRef -> DOI -> Unpaywall chain ───────────────────────

def _crossref_to_pdf(title: str) -> Optional[str]:
    try:
        resp = _get(CROSSREF_API, timeout=12, retries=1, params={"query": title, "rows": 3})
        for item in resp.json().get("message", {}).get("items", []):
            doi = item.get("DOI")
            if doi:
                pdf_url = _unpaywall_find_pdf(doi)
                if pdf_url:
                    return pdf_url
    except Exception as e:
        log.warning("CrossRef chain failed: %s", e)
    return None


# ── Download helper ──────────────────────────────────────────

def _download_pdf(url: str, out: Path, name: str) -> Path:
    dest = out / f"{name}.pdf"
    if dest.exists():
        return dest
    resp = _get(url, timeout=60, retries=2)
    content_type = resp.headers.get("content-type", "")
    if len(resp.content) < 1000 and "pdf" not in content_type.lower():
        raise RuntimeError(f"Downloaded file too small ({len(resp.content)} bytes), likely not a PDF")
    dest.write_bytes(resp.content)
    log.info("Downloaded PDF (%d bytes) to %s from %s", len(resp.content), dest, url)
    return dest
