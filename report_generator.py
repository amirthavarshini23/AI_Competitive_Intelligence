"""
report_generator.py - ReportLab PDF Report Compiler
=====================================================
Generates a corporate-styled PDF dossier from the analysis data.
Features a two-pass NumberedCanvas for dynamic "Page X of Y" footers,
inline Markdown-to-HTML conversion, and structured layout tables.
"""

import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to draw dynamic headers/footers with page counts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def _draw_page_elements(self, page_count):
        self.saveState()

        # Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D"))
        self.drawString(54, 750, "COMPETITIVE INTELLIGENCE REPORT")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawRightString(558, 750, datetime.now().strftime("%B %d, %Y"))

        # Lines
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        self.line(54, 55, 558, 55)

        # Footer
        self.drawString(54, 40, "CONFIDENTIAL - Prepared by AI Analyzer")
        self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()


def _clean_md_inline(text: str) -> str:
    """Convert basic inline Markdown to ReportLab-compatible HTML tags."""
    if not text:
        return ""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`', r'<font face="Courier" size="9">\1</font>', text)
    return text


def _markdown_to_flowables(md_text: str, styles: dict) -> list:
    """Convert multi-line Markdown text into a list of ReportLab Flowables."""
    flowables = []
    if not md_text:
        return flowables

    for line in md_text.splitlines():
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 4))
            continue

        if stripped.startswith("### "):
            flowables.append(Paragraph(_clean_md_inline(stripped[4:]), styles["ReportH3"]))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(_clean_md_inline(stripped[3:]), styles["ReportH2"]))
        elif stripped.startswith("# "):
            flowables.append(Paragraph(_clean_md_inline(stripped[2:]), styles["ReportH1"]))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            flowables.append(Paragraph(
                f"&bull; {_clean_md_inline(stripped[2:])}", styles["ReportBullet"]
            ))
        else:
            flowables.append(Paragraph(_clean_md_inline(stripped), styles["ReportBody"]))

    return flowables


def generate_pdf_report(
    company_name: str, url: str,
    analysis_data: dict, news_articles: list
) -> bytes:
    """
    Generates a styled PDF intelligence report.

    Args:
        company_name: The competitor company name.
        url: The competitor's website URL.
        analysis_data: Dictionary of 6 analysis sections.
        news_articles: List of news article dicts.

    Returns:
        PDF file contents as binary bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72
    )

    base_styles = getSampleStyleSheet()

    # Color palette
    primary = colors.HexColor("#1A365D")
    secondary = colors.HexColor("#2C5282")
    text_color = colors.HexColor("#2D3748")
    bg_header = colors.HexColor("#EDF2F7")

    # Custom styles
    styles = {
        "ReportBody": ParagraphStyle(
            "ReportBody", parent=base_styles["Normal"],
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=text_color, spaceAfter=6
        ),
        "ReportBullet": ParagraphStyle(
            "ReportBullet", parent=base_styles["Normal"],
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=text_color, leftIndent=15, firstLineIndent=-10, spaceAfter=4
        ),
        "ReportH1": ParagraphStyle(
            "ReportH1", parent=base_styles["Heading1"],
            fontName="Helvetica-Bold", fontSize=15, leading=19,
            textColor=primary, spaceBefore=14, spaceAfter=6, keepWithNext=True
        ),
        "ReportH2": ParagraphStyle(
            "ReportH2", parent=base_styles["Heading2"],
            fontName="Helvetica-Bold", fontSize=12, leading=16,
            textColor=secondary, spaceBefore=10, spaceAfter=4, keepWithNext=True
        ),
        "ReportH3": ParagraphStyle(
            "ReportH3", parent=base_styles["Heading3"],
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=text_color, spaceBefore=8, spaceAfter=4, keepWithNext=True
        ),
        "TitleStyle": ParagraphStyle(
            "TitleStyle", parent=base_styles["Normal"],
            fontName="Helvetica-Bold", fontSize=22, leading=26,
            textColor=colors.white, alignment=TA_CENTER
        ),
        "SubtitleStyle": ParagraphStyle(
            "SubtitleStyle", parent=base_styles["Normal"],
            fontName="Helvetica-Oblique", fontSize=11, leading=15,
            textColor=colors.HexColor("#E2E8F0"), alignment=TA_CENTER
        ),
        "MetaLabel": ParagraphStyle(
            "MetaLabel", parent=base_styles["Normal"],
            fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=primary
        ),
        "MetaVal": ParagraphStyle(
            "MetaVal", parent=base_styles["Normal"],
            fontName="Helvetica", fontSize=10, leading=12, textColor=text_color
        ),
        "NewsTitle": ParagraphStyle(
            "NewsTitle", parent=base_styles["Normal"],
            fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=secondary
        ),
        "NewsMeta": ParagraphStyle(
            "NewsMeta", parent=base_styles["Normal"],
            fontName="Helvetica", fontSize=9, leading=11,
            textColor=colors.HexColor("#4A5568")
        ),
    }

    story = []

    # --- Title Banner ---
    banner_data = [
        [Paragraph("COMPETITIVE INTELLIGENCE DOSSIER", styles["TitleStyle"])],
        [Paragraph(f"Strategic Profile for {company_name.upper()}", styles["SubtitleStyle"])]
    ]
    banner = Table(banner_data, colWidths=[504])
    banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), primary),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 18),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 18),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(banner)
    story.append(Spacer(1, 14))

    # --- Metadata Block ---
    meta = [
        [
            Paragraph("Competitor Name:", styles["MetaLabel"]),
            Paragraph(company_name, styles["MetaVal"]),
            Paragraph("Date Analyzed:", styles["MetaLabel"]),
            Paragraph(datetime.now().strftime("%B %d, %Y"), styles["MetaVal"])
        ],
        [
            Paragraph("Target Website:", styles["MetaLabel"]),
            Paragraph(f"<a href='{url}' color='#2C5282'><u>{url}</u></a>", styles["MetaVal"]),
            Paragraph("Intelligence Level:", styles["MetaLabel"]),
            Paragraph("Automated Synth (Gemini Flash)", styles["MetaVal"])
        ]
    ]
    meta_table = Table(meta, colWidths=[100, 152, 100, 152])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_header),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    # --- Analysis Sections ---
    sections = [
        ("company_overview", "1. Company Overview"),
        ("current_business_focus", "2. Current Business Focus"),
        ("hiring_product_trends", "3. Hiring & Product Trends"),
        ("market_opportunities", "4. Market Opportunities"),
        ("potential_risks", "5. Potential Risks"),
        ("predicted_future_direction", "6. Predicted Future Direction"),
    ]

    for key, title in sections:
        content = analysis_data.get(key, "No analysis available for this section.")
        story.append(Paragraph(title, styles["ReportH1"]))
        story.append(HRFlowable(
            width="100%", thickness=1, color=primary, spaceAfter=8, spaceBefore=2
        ))
        story.extend(_markdown_to_flowables(content, styles))
        story.append(Spacer(1, 14))

    # --- News Section ---
    if news_articles:
        story.append(PageBreak())
        story.append(Paragraph("Recent News & Press Coverage", styles["ReportH1"]))
        story.append(HRFlowable(
            width="100%", thickness=1, color=primary, spaceAfter=10, spaceBefore=2
        ))
        for art in news_articles:
            block = [
                Paragraph(_clean_md_inline(art.get("title", "")), styles["NewsTitle"]),
                Paragraph(
                    f"Source: {art.get('source')} | Date: {art.get('date')} | "
                    f"<a href='{art.get('url')}' color='#2C5282'><u>View Article</u></a>",
                    styles["NewsMeta"]
                ),
                Paragraph(_clean_md_inline(art.get("description", "")), styles["ReportBody"]),
                Spacer(1, 10),
            ]
            story.append(KeepTogether(block))

    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


if __name__ == "__main__":
    test_analysis = {
        "company_overview": "A **test company** overview.\n- Point 1\n- Point 2",
        "current_business_focus": "Emphasis on *awesome stuff*.",
        "hiring_product_trends": "Hiring accelerated in AI.",
        "market_opportunities": "Expanding into SaaS.",
        "potential_risks": "Strong incumbent competition.",
        "predicted_future_direction": "Major Q3 release anticipated.",
    }
    test_news = [{
        "title": "Test Article", "source": "TechCrunch",
        "date": "Nov 18, 2026", "description": "Short summary.",
        "url": "https://techcrunch.com"
    }]
    pdf = generate_pdf_report("Test Co", "https://test.com", test_analysis, test_news)
    print("Generated PDF size:", len(pdf), "bytes")
