"""Generate PowerPoint presentation from slide data."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from scholarflow.models import PaperContent, SlideData

THEMES = {
    "academic_blue": {
        "bg": RGBColor(0xFF, 0xFF, 0xFF),
        "title_color": RGBColor(0x1A, 0x3C, 0x6E),
        "text_color": RGBColor(0x33, 0x33, 0x33),
        "accent": RGBColor(0x2E, 0x75, 0xB6),
        "footer_bg": RGBColor(0x1A, 0x3C, 0x6E),
    },
    "minimal_white": {
        "bg": RGBColor(0xFA, 0xFA, 0xFA),
        "title_color": RGBColor(0x22, 0x22, 0x22),
        "text_color": RGBColor(0x44, 0x44, 0x44),
        "accent": RGBColor(0xE8, 0x4D, 0x39),
        "footer_bg": RGBColor(0x22, 0x22, 0x22),
    },
    "dark_modern": {
        "bg": RGBColor(0x1E, 0x1E, 0x2E),
        "title_color": RGBColor(0xCD, 0xD6, 0xF4),
        "text_color": RGBColor(0xBA, 0xC2, 0xDE),
        "accent": RGBColor(0x89, 0xB4, 0xFA),
        "footer_bg": RGBColor(0x11, 0x11, 0x1B),
    },
}


def generate_pptx(
    slides: list[SlideData],
    content: PaperContent,
    output_dir: Path,
    theme: str = "academic_blue",
) -> Path:
    """Generate a .pptx presentation file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    colors = THEMES.get(theme, THEMES["academic_blue"])

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for i, slide_data in enumerate(slides):
        if i == 0:
            _add_title_slide(prs, slide_data, content, colors)
        else:
            _add_content_slide(prs, slide_data, colors, i)

    out_path = output_dir / "slides.pptx"
    prs.save(str(out_path))
    return out_path


def _add_title_slide(
    prs: Presentation,
    slide_data: SlideData,
    content: PaperContent,
    colors: dict,
) -> None:
    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)

    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = colors["footer_bg"]

    title_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(11), Inches(2))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = content.meta.title or slide_data.title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p.alignment = PP_ALIGN.CENTER

    info_box = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(1.5))
    tf2 = info_box.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = ", ".join(content.meta.authors) if content.meta.authors else ""
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    p2.alignment = PP_ALIGN.CENTER

    if content.meta.year or content.meta.venue:
        p3 = tf2.add_paragraph()
        parts = [x for x in [content.meta.venue, content.meta.year] if x]
        p3.text = " | ".join(parts)
        p3.font.size = Pt(16)
        p3.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        p3.alignment = PP_ALIGN.CENTER


def _add_content_slide(
    prs: Presentation,
    slide_data: SlideData,
    colors: dict,
    slide_num: int,
) -> None:
    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)

    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = colors["bg"]

    accent_bar = slide.shapes.add_shape(
        1, Inches(0), Inches(0), Inches(0.15), Inches(7.5)
    )
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = colors["accent"]
    accent_bar.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(0.9))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = slide_data.title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = colors["title_color"]

    if slide_data.bullets:
        body_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.5), Inches(5))
        tf = body_box.text_frame
        tf.word_wrap = True
        for j, bullet in enumerate(slide_data.bullets):
            if j == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"  {bullet}"
            p.font.size = Pt(18)
            p.font.color.rgb = colors["text_color"]
            p.space_after = Pt(12)

    page_box = slide.shapes.add_textbox(Inches(12), Inches(7), Inches(1), Inches(0.4))
    tf = page_box.text_frame
    p = tf.paragraphs[0]
    p.text = str(slide_num + 1)
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    p.alignment = PP_ALIGN.RIGHT
