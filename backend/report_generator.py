import os
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import requests

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image as RLImage, HRFlowable, PageBreak
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

SEVERITY_COLORS_HEX = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#D97706",
    "Low": "#16A34A"
}

CLIENT_NAME = "Dani"
REPORT_TITLE = "Civil Infrastructure Pathology Detection Report"
DISCLAIMER = (
    "This AI-generated report is for preliminary inspection support only. "
    "All findings and recommendations must be verified and validated by a qualified, "
    "licensed civil engineer before any remediation decisions are made. The AI detection "
    "system may not identify all defects and should not be used as the sole basis for "
    "engineering or safety-critical decisions."
)


def generate_word_report(inspection: Dict, ai_report: Dict, output_path: str):
    doc = Document()

    # Page setup
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    _add_title_page(doc, inspection)
    doc.add_page_break()
    _add_project_info(doc, inspection)
    _add_detection_summary(doc, inspection)
    _add_visual_evidence(doc, inspection)
    _add_ai_sections(doc, ai_report)
    _add_disclaimer(doc)

    doc.save(output_path)


def _add_title_page(doc: Document, inspection: dict):
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(REPORT_TITLE)
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Prepared for: {CLIENT_NAME}")
    run.font.size = Pt(14)
    run.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    run.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Asset Type: {inspection.get('asset_type', 'N/A')}")
    run.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Inspection ID: {inspection.get('id', 'N/A')[:8].upper()}")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)


def _add_project_info(doc: Document, inspection: dict):
    _add_heading(doc, "1. Project Information")

    table = doc.add_table(rows=6, cols=2)
    table.style = "Table Grid"
    rows_data = [
        ("Report Date", datetime.now().strftime("%B %d, %Y %H:%M UTC")),
        ("Client", CLIENT_NAME),
        ("Asset Type", inspection.get("asset_type", "N/A")),
        ("Detection Model", inspection.get("model_name", "N/A")),
        ("Image File", inspection.get("original_filename", "N/A")),
        ("Inspection ID", inspection.get("id", "N/A")[:8].upper()),
    ]
    for i, (label, value) in enumerate(rows_data):
        table.rows[i].cells[0].text = label
        table.rows[i].cells[1].text = value
        table.rows[i].cells[0].paragraphs[0].runs[0].font.bold = True
    doc.add_paragraph()


def _add_detection_summary(doc: Document, inspection: dict):
    _add_heading(doc, "2. Detection Summary")

    detections = inspection.get("detections", [])
    severity = inspection.get("severity_summary", {})

    p = doc.add_paragraph()
    run = p.add_run(f"Total defects detected: {len(detections)}")
    run.font.bold = True

    # Severity table
    sev_table = doc.add_table(rows=2, cols=4)
    sev_table.style = "Table Grid"
    headers = ["Critical", "High", "Medium", "Low"]
    for i, h in enumerate(headers):
        sev_table.rows[0].cells[i].text = h
        sev_table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True
        sev_table.rows[1].cells[i].text = str(severity.get(h, 0))

    doc.add_paragraph()

    if detections:
        _add_heading(doc, "Detection Details", level=2)
        det_table = doc.add_table(rows=1, cols=4)
        det_table.style = "Table Grid"
        hdr = det_table.rows[0].cells
        for i, h in enumerate(["#", "Defect Class", "Confidence", "Severity"]):
            hdr[i].text = h
            hdr[i].paragraphs[0].runs[0].font.bold = True

        for idx, det in enumerate(detections, 1):
            row = det_table.add_row().cells
            row[0].text = str(idx)
            row[1].text = det.get("class", "").replace("_", " ").title()
            row[2].text = f"{det.get('confidence', 0):.1%}"
            row[3].text = det.get("severity", "N/A")

    doc.add_paragraph()


def _add_visual_evidence(doc: Document, inspection: dict):
    _add_heading(doc, "3. Visual Evidence")

    upload_dir = Path("uploads")
    output_dir = Path("outputs")
    image_id = inspection.get("image_id", "")

    orig_path = None
    for f in upload_dir.iterdir():
        if f.stem == image_id:
            orig_path = f
            break

    annotated_url = inspection.get("annotated_image", "")
    annotated_path = None
    if annotated_url:
        local_path = Path(annotated_url.lstrip("/"))
        if local_path.exists():
            annotated_path = local_path

    for label, path in [("Original Image", orig_path), ("Annotated Image (AI Detection)", annotated_path)]:
        if path and Path(path).exists():
            p = doc.add_paragraph(label)
            p.runs[0].font.bold = True
            try:
                doc.add_picture(str(path), width=Inches(5.5))
                doc.add_paragraph()
            except Exception:
                doc.add_paragraph(f"[Image: {path}]")


def _add_ai_sections(doc: Document, ai_report: dict):
    sections = [
        ("4. AI Civil Engineering Interpretation", "executive_summary"),
        ("5. Defect Descriptions", "defect_descriptions"),
        ("6. Possible Causes", "possible_causes"),
        ("7. Severity Assessment", "severity_assessment"),
        ("8. Risk Assessment", "risk_explanation"),
        ("9. Recommended Actions", "recommended_actions"),
        ("10. Priority Level", "priority_level"),
        ("11. Final Conclusion", "final_conclusion"),
    ]
    for heading, key in sections:
        _add_heading(doc, heading)
        content = ai_report.get(key, "Not available.")
        doc.add_paragraph(content)
        doc.add_paragraph()


def _add_disclaimer(doc: Document):
    doc.add_page_break()
    _add_heading(doc, "Disclaimer")
    p = doc.add_paragraph(DISCLAIMER)
    p.runs[0].font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
    p.runs[0].font.italic = True


def _add_heading(doc: Document, text: str, level: int = 1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)


def generate_pdf_report(inspection: Dict, ai_report: Dict, output_path: str):
    if not REPORTLAB_AVAILABLE:
        _generate_pdf_fallback(inspection, ai_report, output_path)
        return

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    BLUE = colors.HexColor("#1E40AF")
    GRAY = colors.HexColor("#6B7280")

    title_style = ParagraphStyle("Title", parent=styles["Title"],
                                  fontSize=20, textColor=BLUE, spaceAfter=12, alignment=TA_CENTER)
    h1_style = ParagraphStyle("H1", parent=styles["Heading1"],
                               fontSize=14, textColor=BLUE, spaceAfter=6, spaceBefore=12)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
                               fontSize=11, textColor=BLUE, spaceAfter=4, spaceBefore=8)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
                                 fontSize=10, spaceAfter=6, leading=14, alignment=TA_JUSTIFY)
    bold_style = ParagraphStyle("Bold", parent=styles["Normal"],
                                 fontSize=10, fontName="Helvetica-Bold")
    disclaimer_style = ParagraphStyle("Disclaimer", parent=styles["Normal"],
                                       fontSize=9, textColor=GRAY, fontName="Helvetica-Oblique", alignment=TA_JUSTIFY)
    center_style = ParagraphStyle("Center", parent=styles["Normal"],
                                   fontSize=11, alignment=TA_CENTER)

    story = []

    # Title page
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(REPORT_TITLE, title_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"Prepared for: <b>{CLIENT_NAME}</b>", center_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", center_style))
    story.append(Paragraph(f"Asset Type: {inspection.get('asset_type', 'N/A')}", center_style))
    story.append(Spacer(1, 2 * cm))
    story.append(PageBreak())

    # Project info
    story.append(Paragraph("1. Project Information", h1_style))
    info_data = [
        ["Field", "Value"],
        ["Report Date", datetime.now().strftime("%B %d, %Y %H:%M UTC")],
        ["Client", CLIENT_NAME],
        ["Asset Type", inspection.get("asset_type", "N/A")],
        ["Detection Model", inspection.get("model_name", "N/A")],
        ["Image File", inspection.get("original_filename", "N/A")],
        ["Inspection ID", inspection.get("id", "N/A")[:8].upper()],
    ]
    t = Table(info_data, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    # Detection summary
    story.append(Paragraph("2. Detection Summary", h1_style))
    detections = inspection.get("detections", [])
    severity = inspection.get("severity_summary", {})
    story.append(Paragraph(f"<b>Total defects detected: {len(detections)}</b>", body_style))

    sev_data = [
        ["Critical", "High", "Medium", "Low"],
        [str(severity.get("Critical", 0)), str(severity.get("High", 0)),
         str(severity.get("Medium", 0)), str(severity.get("Low", 0))]
    ]
    sev_t = Table(sev_data, colWidths=[4.25 * cm] * 4)
    sev_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#DC2626")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#EA580C")),
        ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#D97706")),
        ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#16A34A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sev_t)
    story.append(Spacer(1, 0.3 * cm))

    if detections:
        story.append(Paragraph("Detection Details", h2_style))
        det_data = [["#", "Defect Class", "Confidence", "Severity"]]
        for i, d in enumerate(detections, 1):
            det_data.append([
                str(i),
                d.get("class", "").replace("_", " ").title(),
                f"{d.get('confidence', 0):.1%}",
                d.get("severity", "N/A")
            ])
        det_t = Table(det_data, colWidths=[1 * cm, 7 * cm, 4 * cm, 5 * cm])
        det_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(det_t)

    story.append(Spacer(1, 0.5 * cm))

    # Visual Evidence
    story.append(Paragraph("3. Visual Evidence", h1_style))
    image_id = inspection.get("image_id", "")
    upload_dir = Path("uploads")
    orig_path = None
    for f in upload_dir.iterdir():
        if f.stem == image_id:
            orig_path = f
            break

    annotated_url = inspection.get("annotated_image", "")
    annotated_path = None
    if annotated_url:
        local = Path(annotated_url.lstrip("/"))
        if local.exists():
            annotated_path = local

    for label, path in [("Original Image", orig_path), ("Annotated Image (AI Detection)", annotated_path)]:
        if path and Path(path).exists():
            story.append(Paragraph(f"<b>{label}</b>", body_style))
            try:
                img = RLImage(str(path), width=15 * cm, height=9 * cm, kind="proportional")
                story.append(img)
                story.append(Spacer(1, 0.3 * cm))
            except Exception:
                story.append(Paragraph(f"[Image unavailable: {path}]", body_style))

    # AI sections
    ai_sections = [
        ("4. AI Civil Engineering Interpretation", "executive_summary"),
        ("5. Defect Descriptions", "defect_descriptions"),
        ("6. Possible Causes", "possible_causes"),
        ("7. Severity Assessment", "severity_assessment"),
        ("8. Risk Assessment", "risk_explanation"),
        ("9. Recommended Actions", "recommended_actions"),
        ("10. Priority Level", "priority_level"),
        ("11. Final Conclusion", "final_conclusion"),
    ]
    for heading, key in ai_sections:
        story.append(Paragraph(heading, h1_style))
        content = ai_report.get(key, "Not available.")
        story.append(Paragraph(content, body_style))
        story.append(Spacer(1, 0.3 * cm))

    # Disclaimer
    story.append(PageBreak())
    story.append(Paragraph("Disclaimer", h1_style))
    story.append(Paragraph(DISCLAIMER, disclaimer_style))

    doc.build(story)


def _generate_pdf_fallback(inspection: dict, ai_report: dict, output_path: str):
    """Simple text-based PDF fallback when ReportLab is not available."""
    try:
        import subprocess
        html = _build_html_report(inspection, ai_report)
        html_path = output_path.replace(".pdf", "_temp.html")
        with open(html_path, "w") as f:
            f.write(html)
        subprocess.run(["wkhtmltopdf", html_path, output_path], check=True, capture_output=True)
        os.remove(html_path)
    except Exception:
        with open(output_path, "wb") as f:
            f.write(b"%PDF-1.4\n%Report generation requires ReportLab\n")


def _build_html_report(inspection: dict, ai_report: dict) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
    <title>{REPORT_TITLE}</title></head><body>
    <h1>{REPORT_TITLE}</h1>
    <p>Prepared for: {CLIENT_NAME}</p>
    <p>Date: {datetime.now().strftime('%B %d, %Y')}</p>
    <h2>Summary</h2>
    <p>{ai_report.get('executive_summary', 'N/A')}</p>
    <p><em>{DISCLAIMER}</em></p>
    </body></html>"""
