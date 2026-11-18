"""
report_generator.py - Corporate Strategic Intelligence PDF Report Generator
===========================================================================
Generates multi-page corporate PDF dossiers using ReportLab with dynamic NumberedCanvas,
executive summary, 6 strategic pillars, 4-quadrant SWOT tables, and news digests.
"""

import io
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas renderer for accurate 'Page X of Y' footers and headers."""
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
        
        # Primary Color: Slate Blue (#1A365D)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D"))
        self.drawString(54, 750, "AI COMPETITIVE INTELLIGENCE & MARKET STRATEGY DOSSIER")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawRightString(558, 750, datetime.now().strftime("%B %d, %Y"))

        # Header rule
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)

        # Footer rule
        self.line(54, 50, 558, 50)

        # Footer text
        self.setFont("Helvetica", 8)
        self.drawString(54, 38, "CONFIDENTIAL - Prepared for Academic & Strategic Portfolio Presentation")
        self.drawRightString(558, 38, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def clean_md_inline(text: str) -> str:
    """Escapes HTML entities and translates basic Markdown to ReportLab XML tags."""
    if not text:
        return ""
    text = str(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.*?)`", r'<font face="Courier" size="9">\1</font>', text)
    return text

def markdown_to_flowables(md_text: str, styles: Dict[str, ParagraphStyle]) -> List[Any]:
    """Converts multi-line Markdown text into a list of ReportLab Flowables."""
    flowables = []
    if not md_text:
        return flowables

    for line in md_text.splitlines():
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 4))
            continue

        if stripped.startswith("### "):
            flowables.append(Paragraph(clean_md_inline(stripped[4:]), styles["ReportH3"]))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(clean_md_inline(stripped[3:]), styles["ReportH2"]))
        elif stripped.startswith("# "):
            flowables.append(Paragraph(clean_md_inline(stripped[2:]), styles["ReportH1"]))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            flowables.append(Paragraph(f"&bull; {clean_md_inline(stripped[2:])}", styles["ReportBullet"]))
        else:
            flowables.append(Paragraph(clean_md_inline(stripped), styles["ReportBody"]))

    return flowables

def generate_pdf_report(
    company_name: str,
    url: str,
    analysis_data: Dict[str, Any],
    news_articles: List[Dict[str, Any]],
    swot_data: Optional[Dict[str, Any]] = None,
    engine_used: str = "Extractive NLP & Strategic Analysis"
) -> bytes:
    """
    Generates an executive-style multi-page PDF intelligence dossier.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    base_styles = getSampleStyleSheet()
    primary = colors.HexColor("#1A365D")
    secondary = colors.HexColor("#2563EB")
    charcoal = colors.HexColor("#1E293B")
    bg_light = colors.HexColor("#F8FAFC")

    styles = {
        "ReportBody": ParagraphStyle("ReportBody", parent=base_styles["Normal"], fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=charcoal, spaceAfter=5),
        "ReportBullet": ParagraphStyle("ReportBullet", parent=base_styles["Normal"], fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=charcoal, leftIndent=14, firstLineIndent=-8, spaceAfter=3),
        "ReportH1": ParagraphStyle("ReportH1", parent=base_styles["Heading1"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=primary, spaceBefore=12, spaceAfter=4, keepWithNext=True),
        "ReportH2": ParagraphStyle("ReportH2", parent=base_styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=secondary, spaceBefore=8, spaceAfter=3, keepWithNext=True),
        "ReportH3": ParagraphStyle("ReportH3", parent=base_styles["Heading3"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=charcoal, spaceBefore=6, spaceAfter=2, keepWithNext=True),
        "BannerTitle": ParagraphStyle("BannerTitle", parent=base_styles["Normal"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.white, alignment=TA_CENTER),
        "BannerSub": ParagraphStyle("BannerSub", parent=base_styles["Normal"], fontName="Helvetica", fontSize=10, leading=14, textColor=colors.HexColor("#E2E8F0"), alignment=TA_CENTER),
        "MetaLabel": ParagraphStyle("MetaLabel", parent=base_styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=primary),
        "MetaVal": ParagraphStyle("MetaVal", parent=base_styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, textColor=charcoal),
        "SwotHead": ParagraphStyle("SwotHead", parent=base_styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=colors.white, alignment=TA_CENTER),
        "SwotText": ParagraphStyle("SwotText", parent=base_styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=charcoal),
    }

    story = []

    # 1. Header Banner
    banner_data = [
        [Paragraph("STRATEGIC COMPETITIVE INTELLIGENCE DOSSIER", styles["BannerTitle"])],
        [Paragraph(f"Corporate Profile & Strategic Positioning: {company_name.upper()}", styles["BannerSub"])]
    ]
    banner = Table(banner_data, colWidths=[504])
    banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), primary),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 16),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 16),
    ]))
    story.append(banner)
    story.append(Spacer(1, 10))

    # 2. Metadata Block
    meta_table_data = [
        [
            Paragraph("Competitor Name:", styles["MetaLabel"]),
            Paragraph(company_name, styles["MetaVal"]),
            Paragraph("Date Generated:", styles["MetaLabel"]),
            Paragraph(datetime.now().strftime("%B %d, %Y"), styles["MetaVal"])
        ],
        [
            Paragraph("Target Website:", styles["MetaLabel"]),
            Paragraph(f"<a href='{url}' color='#2563EB'><u>{url}</u></a>", styles["MetaVal"]),
            Paragraph("Intelligence Engine:", styles["MetaLabel"]),
            Paragraph(engine_used, styles["MetaVal"])
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[100, 152, 100, 152])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Executive Summary
    story.append(Paragraph("1. Executive Summary", styles["ReportH1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=primary, spaceAfter=6, spaceBefore=1))
    exec_summary = (
        f"This competitive intelligence dossier synthesizes public web surfaces, news announcements, and market signals "
        f"for <b>{company_name}</b>. The evaluation covers six strategic dimensions, identifies core product vectors, "
        f"and outlines a forward-looking 12–24 month strategic outlook."
    )
    story.append(Paragraph(exec_summary, styles["ReportBody"]))
    story.append(Spacer(1, 10))

    # 4. Six Pillars
    pillars = [
        ("company_overview", "2. Company Overview"),
        ("current_business_focus", "3. Current Business Focus"),
        ("hiring_product_trends", "4. Hiring & Product Trends"),
        ("market_opportunities", "5. Market Opportunities"),
        ("potential_risks", "6. Potential Risks"),
        ("predicted_future_direction", "7. Predicted Future Direction"),
    ]

    for key, title in pillars:
        content = analysis_data.get(key, "Information unavailable for this section.")
        story.append(Paragraph(title, styles["ReportH1"]))
        story.append(HRFlowable(width="100%", thickness=0.75, color=primary, spaceAfter=6, spaceBefore=1))
        story.extend(markdown_to_flowables(content, styles))
        story.append(Spacer(1, 8))

    # 5. SWOT Analysis Table (if provided)
    if swot_data and isinstance(swot_data, dict):
        story.append(PageBreak())
        story.append(Paragraph("8. SWOT Strategic Matrix", styles["ReportH1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=primary, spaceAfter=8, spaceBefore=1))
        
        str_points = "<br/>".join([f"&bull; {clean_md_inline(p)}" for p in swot_data.get("strengths", {}).get("points", ["Established market visibility"])])
        weak_points = "<br/>".join([f"&bull; {clean_md_inline(p)}" for p in swot_data.get("weaknesses", {}).get("points", ["Intensifying peer pressure"])])
        opp_points = "<br/>".join([f"&bull; {clean_md_inline(p)}" for p in swot_data.get("opportunities", {}).get("points", ["AI automation & expansion"])])
        thr_points = "<br/>".join([f"&bull; {clean_md_inline(p)}" for p in swot_data.get("threats", {}).get("points", ["Regulatory headwinds"])])

        swot_matrix_data = [
            [
                Paragraph("STRENGTHS (Internal)", styles["SwotHead"]),
                Paragraph("WEAKNESSES (Internal)", styles["SwotHead"])
            ],
            [
                Paragraph(str_points, styles["SwotText"]),
                Paragraph(weak_points, styles["SwotText"])
            ],
            [
                Paragraph("OPPORTUNITIES (External)", styles["SwotHead"]),
                Paragraph("THREATS (External)", styles["SwotHead"])
            ],
            [
                Paragraph(opp_points, styles["SwotText"]),
                Paragraph(thr_points, styles["SwotText"])
            ]
        ]
        
        swot_table = Table(swot_matrix_data, colWidths=[252, 252])
        swot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#1E3A5F")),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#991B1B")),
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor("#065F46")),
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor("#92400E")),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor("#F1F5F9")),
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor("#F1F5F9")),
            ('BACKGROUND', (0, 3), (0, 3), colors.HexColor("#F1F5F9")),
            ('BACKGROUND', (1, 3), (1, 3), colors.HexColor("#F1F5F9")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        story.append(swot_table)
        story.append(Spacer(1, 12))

    # 6. News & Press Coverage
    if news_articles:
        story.append(Spacer(1, 8))
        story.append(Paragraph("9. Recent Public News & Press Coverage", styles["ReportH1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=primary, spaceAfter=8, spaceBefore=1))
        for art in news_articles[:5]:
            news_block = [
                Paragraph(f"<b>{clean_md_inline(art.get('title', ''))}</b>", styles["ReportH3"]),
                Paragraph(f"<i>Source: {clean_md_inline(art.get('source', 'Public News'))} | Date: {art.get('published_date', art.get('date', 'Recent'))}</i>", styles["MetaVal"]),
                Paragraph(clean_md_inline(art.get("description", "")), styles["ReportBody"]),
                Spacer(1, 4)
            ]
            story.append(KeepTogether(news_block))

    # 7. Methodology & Integrity Notice
    story.append(Spacer(1, 10))
    story.append(Paragraph("10. Methodology & Analysis Governance", styles["ReportH1"]))
    story.append(HRFlowable(width="100%", thickness=0.75, color=primary, spaceAfter=6, spaceBefore=1))
    method_text = (
        "<b>Data Sources:</b> Scraped public domain pages and public RSS syndication. "
        "<b>Processing Pipeline:</b> TF-IDF vectorization, NLTK VADER sentiment analysis, and structured synthesis. "
        "<b>Integrity Disclaimer:</b> All analytical scores and projections are internal research heuristics, "
        "not audited financial statements or legally verified market share data."
    )
    story.append(Paragraph(method_text, styles["ReportBody"]))

    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
