---
name: scholarflow
description: "All-in-one academic paper processor. Paper PDF/title/arXiv/DOI → summary, PPT slides, speech script (LaTeX PDF), study notes (LaTeX PDF), mindmap, poster, translation."
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - sf
      env:
        - OPENAI_API_KEY
    primaryEnv: OPENAI_API_KEY
    emoji: "📚"
    homepage: https://github.com/bcefghj/scholarflow
---

# ScholarFlow - Academic Paper Processing Skill

When the user asks to analyze, summarize, process, or generate presentations/notes from an academic paper, use the `sf` CLI tool.

## When to Use This Skill

- User asks to summarize or analyze a paper
- User wants to generate slides/PPT from a paper
- User needs a speech script for presenting a paper
- User wants study notes (deep/exam/quick modes)
- User asks to create a mindmap or poster from a paper
- User wants to batch-process multiple papers

## Commands

### Quick Scan (Is this paper worth reading?)

```bash
sf scan paper.pdf
sf scan --title "Attention Is All You Need"
sf scan --arxiv 1706.03762
```

### Generate ALL Outputs

```bash
sf full paper.pdf
sf full --title "Paper Title"
sf full --arxiv 1706.03762 --lang zh --notes-mode deep
```

### Individual Outputs

```bash
sf slides paper.pdf                    # PowerPoint PPT
sf slides paper.pdf --beamer           # LaTeX Beamer PDF
sf script paper.pdf                    # Speech script (LaTeX PDF)
sf notes paper.pdf --mode deep         # Deep study notes
sf notes paper.pdf --mode exam         # Exam review notes
sf notes paper.pdf --mode quick        # Quick 1-2 page notes
sf mindmap paper.pdf                   # Interactive mindmap (HTML)
sf poster paper.pdf                    # Academic poster (HTML)
sf translate paper.pdf                 # Bilingual summary
```

### Batch Processing

```bash
sf batch ./papers/                     # Process all PDFs in folder
```

### Configuration

```bash
sf config set model minimax/MiniMax-M2.7
sf config set lang zh
sf config show
```

## Input Methods

- **PDF file**: `sf full paper.pdf`
- **Paper title**: `sf full --title "Paper Title"` (auto-search and download)
- **arXiv**: `sf full --arxiv 1706.03762` (auto-download)
- **DOI**: `sf full --doi 10.xxxx/yyyy`

## Options

- `--model`: LLM model (openai/gpt-4o, minimax/MiniMax-M2.7, deepseek/deepseek-chat, etc.)
- `--lang`: Output language (zh / en)
- `--verbosity`: Detail level (concise / normal / detailed)
- `--theme`: PPT theme (academic_blue / minimal_white / dark_modern)
- `--beamer-theme`: Beamer theme (Madrid / Berlin / Singapore)
- `--notes-mode`: Notes mode (deep / exam / quick)
- `--output`: Output directory

## Installation

```bash
pip install scholarflow
```

## Notes

- At least one LLM API key must be set: OPENAI_API_KEY, MINIMAX_API_KEY, DEEPSEEK_API_KEY, etc.
- LaTeX output requires a LaTeX compiler (tectonic recommended: `cargo install tectonic`)
- PDF parsing uses PyMuPDF, no additional tools needed
