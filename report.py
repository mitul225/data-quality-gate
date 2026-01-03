from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor, grey

def generate_pdf(summary, completeness_df, schema_df, uniqueness_info,
                 naming_df, recommendations, date_profile=None):

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=40,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # ---------------- CUSTOM STYLES 1 ----------------
    footer_style = ParagraphStyle(
    "FooterStyle",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=9,
    textColor=HexColor("#6b7280"),
    spaceBefore=12
)

    # ---------------- CUSTOM STYLES 2 ----------------
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=HexColor("#0f172a"),
        spaceAfter=12
    )

    # ---------------- CUSTOM STYLES 3 ----------------
    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=HexColor("#475569"),
        spaceAfter=20
    )

    # ---------------- CUSTOM STYLES 4 ----------------
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        textColor=HexColor("#111827"),
        spaceBefore=18,
        spaceAfter=8
    )

    # ---------------- CUSTOM STYLES 5 ----------------
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        textColor=HexColor("#1f2937"),
        spaceAfter=6
    )

    # ---------------- CUSTOM STYLES 6 ----------------
    note_style = ParagraphStyle(
        "NoteStyle",
        parent=styles["Italic"],
        textColor=HexColor("#374151"),
        spaceAfter=10
    )

    elements = []

    # ---------------- TITLE ----------------
    elements.append(Paragraph(
        "Data Quality Gate",
        title_style
    ))
    elements.append(Paragraph(
        "Data Quality & Analytics Readiness Assessment",
        subtitle_style
    ))

    # ---------------- EXECUTIVE SUMMARY ----------------
    elements.append(Paragraph("Executive Summary", section_style))
    elements.append(Paragraph(
        "This report presents an independent review of dataset quality prior to its "
        "use in analytics, dashboards, or decision-making processes. The assessment "
        "highlights data risks that may impact accuracy, trust, and long-term maintainability.",
        body_style
    ))

    # ---------------- DATASET OVERVIEW ----------------
    elements.append(Paragraph("Dataset Overview", section_style))
    for k, v in summary.items():
        elements.append(Paragraph(f"• <b>{k}:</b> {v}", body_style))

    # ---------------- COMPLETENESS ----------------
    elements.append(Paragraph("Data Completeness Assessment", section_style))
    elements.append(Paragraph(
        "Columns with high completeness are suitable for analytics. Columns with high "
        "missing values may indicate unused fields or upstream data issues.",
        note_style
    ))

    elements.append(_styled_table(completeness_df))

    # ---------------- SCHEMA ----------------
    elements.append(Paragraph("Schema & Data Type Validation", section_style))
    elements.append(Paragraph(
        "Detected data types are inferred using column naming conventions and value "
        "patterns to support reliable analytical usage.",
        note_style
    ))
    elements.append(_styled_table(schema_df))

    # ---------------- DATE PROFILE ----------------
    if date_profile:
        elements.append(Paragraph("Date Coverage & Temporal Validity Review", section_style))
        elements.append(Paragraph(
            f"• Date Column Assessed: <b>{date_profile['column']}</b>",
            body_style
        ))
        elements.append(Paragraph(
            f"• Date Range (YYYY-MM-DD): {date_profile['min_date']} to {date_profile['max_date']}",
            body_style
        ))
        if date_profile:
            elements.append(Paragraph(
                f"• Invalid Date Records: {date_profile.get('invalid_date_count', 0)} "
                f"({date_profile.get('invalid_pct', 0)}%)",
                body_style
            ))
        

    # ---------------- NAMING ----------------
    elements.append(Paragraph("Column Naming & Governance Review", section_style))
    elements.append(Paragraph(
        "Inconsistent naming increases query complexity and governance risk. "
        "Standardization to lowercase snake_case is recommended.",
        note_style
    ))
    elements.append(_styled_table(naming_df))

    # ---------------- RECOMMENDATIONS ----------------
    elements.append(Paragraph("Advisory Notes & Recommended Actions", section_style))
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", body_style))

    
    
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "Built by a Data Engineer focused on data quality and analytics reliability.",
        footer_style
    ))
    
    elements.append(Paragraph(
        '<link href="https://www.linkedin.com/in/mitul-luhar">linkedin.com/in/mitul-luhar</link>',
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def _styled_table(df):
    table = Table(
        [df.columns.tolist()] + df.values.tolist(),
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#e5e7eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#111827")),
        ("GRID", (0, 0), (-1, -1), 0.5, grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    return table
    