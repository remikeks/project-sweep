"""Create print-ready PDFs for the SWEEP learner guides and worksheets."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from build_production_courseware import Course, Module, focus_list, parse_outlines, slugify


NAVY = colors.HexColor("#0B2C7A")
PALE_BLUE = colors.HexColor("#F2F6FA")
TEXT = colors.HexColor("#171717")
MUTED = colors.HexColor("#595959")
BORDER = colors.HexColor("#D9D9D9")


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=colors.black, spaceAfter=7, alignment=0),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName="Helvetica", fontSize=11, leading=14, textColor=MUTED, spaceAfter=15),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica", fontSize=10.5, leading=15, textColor=TEXT, spaceAfter=8),
        "head1": ParagraphStyle("head1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.black, spaceBefore=14, spaceAfter=8),
        "head2": ParagraphStyle("head2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=colors.black, spaceBefore=10, spaceAfter=5),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Helvetica", fontSize=10.5, leading=14, textColor=TEXT, leftIndent=14, firstLineIndent=-8, spaceAfter=3),
        "note": ParagraphStyle("note", parent=base["BodyText"], fontName="Helvetica", fontSize=8.8, leading=12, textColor=MUTED, spaceAfter=8),
        "table": ParagraphStyle("table", parent=base["BodyText"], fontName="Helvetica", fontSize=8.5, leading=11, textColor=TEXT),
        "table_header": ParagraphStyle("table_header", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white),
    }


def paragraph(value: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(html.escape(value).replace("\n", "<br/>"), style)


def notice(s: dict) -> Paragraph:
    return paragraph(
        "Practice notice: Apply the law, organisational policy, supervision requirements, and approved referral pathways that govern your setting. "
        "This material supports learning and does not replace urgent safeguarding, clinical, or legal procedures.",
        s["note"],
    )


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(letter[0] / 2, 0.42 * inch, "SWEEP Academy learning materials")
    canvas.restoreState()


def build_guide(course: Course, destination: Path) -> None:
    s = styles()
    story = [
        paragraph(course.title, s["title"]),
        paragraph(f"Learner guide  |  {course.code}  |  {course.school}", s["subtitle"]),
        paragraph(
            f"This guide supports a three-part learning sequence for {course.title}. By the end of the course, you should be able to {course.outcome[0].lower() + course.outcome[1:]}",
            s["body"],
        ),
        notice(s),
        paragraph("Learning objectives", s["head1"]),
    ]
    for item in [course.outcome, *[f"Apply the key ideas from {module.title}." for module in course.modules]]:
        story.append(paragraph(f"• {item}", s["bullet"]))
    story.extend([paragraph("Course structure", s["head1"]), Spacer(1, 2)])
    data = [[paragraph("Module", s["table_header"]), paragraph("Focus", s["table_header"]), paragraph("Suggested study time", s["table_header"])]]
    for module in course.modules:
        data.append([
            paragraph(f"{module.order}. {module.title}", s["table"]),
            paragraph(module.focus, s["table"]),
            paragraph("10 to 15 minutes", s["table"]),
        ])
    table = Table(data, colWidths=[1.95 * inch, 3.2 * inch, 1.2 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 2), (-1, 2), PALE_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    for module in course.modules:
        story.extend([PageBreak(), paragraph(f"Module {module.order}  {module.title}", s["head1"]), paragraph(
            f"This module focuses on {module.focus}. Work through the material with a current practice setting in mind, but remove identifying information from any examples you record.",
            s["body"],
        ), paragraph("What to pay attention to", s["head2"])])
        for item in focus_list(module):
            story.append(paragraph(f"• {item[:1].upper() + item[1:]}", s["bullet"]))
        story.append(paragraph("Learning sequence", s["head2"]))
        for body in [
            f"Start by defining the purpose of {module.title.lower()} in relation to the course outcome. Notice where professional judgement is needed and where a local procedure must guide the next step.",
            f"Examine the practical implications of {module.focus}. Separate observations from assumptions, identify strengths as well as concerns, and be clear about information that must be checked with a person, family, colleague, or approved source.",
            "Use a respectful, collaborative approach. Explain your role, seek informed participation where appropriate, and document only information that is relevant, accurate, and necessary for the purpose of the work.",
            "When a concern exceeds your role, supervision, competence, or authority, pause and use the correct escalation route. A prompt referral and a clear handover can protect continuity of support.",
        ]:
            story.append(paragraph(body, s["body"]))
        story.extend([paragraph("Practice reflection", s["head2"]), paragraph(
            f"Choose a de-identified practice situation. What information would help you work through {module.title.lower()} safely, and what would require consultation or a local policy check?", s["body"]
        )])
    story.extend([
        PageBreak(), paragraph("Course activity", s["head1"]), paragraph(
            "Use the accompanying worksheet to apply the course sequence to a short case. Your completed activity should show what you noticed, the action you would take within your role, and what you would escalate or verify locally.", s["body"]
        ), paragraph("Assessment preparation", s["head1"]),
    ])
    for focus in course.cbt_focus:
        story.append(paragraph(f"• Review the distinction between: {focus}.", s["bullet"]))
    story.extend([paragraph("References and local adaptation", s["head1"])])
    for reference in [
        "SWEEP Academy Course Content Outlines, production blueprint for this course.",
        "The current legislation, professional standards, safeguarding procedures, and referral directories for the delivery jurisdiction.",
        "The learner's employer or placement policy, supervision arrangements, and documentation standards.",
    ]:
        story.append(paragraph(f"• {reference}", s["bullet"]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(destination), pagesize=letter, leftMargin=0.82 * inch, rightMargin=0.82 * inch, topMargin=0.75 * inch, bottomMargin=0.72 * inch,
        title=f"{course.title} Learner Guide", author="SWEEP Academy",
    ).build(story, onFirstPage=footer, onLaterPages=footer)


def response_space() -> Table:
    cell = Paragraph("Response", styles()["note"])
    table = Table([[cell], [""], [""]], colWidths=[6.85 * inch], rowHeights=[0.22 * inch, 0.45 * inch, 0.45 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFBFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def build_worksheet(course: Course, destination: Path) -> None:
    s = styles()
    story = [
        Spacer(1, 22),
        paragraph(course.title, s["title"]),
        paragraph(f"Practice worksheet  |  {course.code}", s["subtitle"]),
        paragraph(
            "Use this de-identified learning activity after completing the three modules. Record only what is necessary for your learning. Do not include client, family, patient, student, or colleague names.", s["body"]
        ), notice(s), paragraph("Practice scenario", s["head1"]), paragraph(
            f"You are supporting a person, family, group, or community that needs help related to {course.title.lower()}. The situation contains incomplete information, competing priorities, and at least one issue that may need advice from a supervisor or partner service.", s["body"]
        ), paragraph("Activity instructions", s["head1"]),
    ]
    for item in [
        "Work through the modules in order and use the questions below to organise your response.",
        "Distinguish information you know from information you need to verify.",
        "Identify the immediate action that sits within your role and any decision that needs escalation.",
        "Use your local policy and referral information before applying this activity in practice.",
    ]:
        story.append(paragraph(f"• {item}", s["bullet"]))
    prompts = [
        ("1. What matters now", f"What information, strengths, risks, and priorities would you consider when approaching {course.modules[0].title.lower()}?"),
        ("2. Safe and collaborative response", f"How would you apply {course.modules[1].title.lower()} while communicating respectfully and within your scope?"),
        ("3. Coordination and follow-up", f"What documentation, review point, consultation, referral, or handover would be appropriate when applying {course.modules[2].title.lower()}?"),
        ("4. Reflection", "What assumption did you need to test, and how would you check it without causing harm or excluding the person's voice?"),
    ]
    for title, question in prompts:
        story.extend([paragraph(title, s["head2"]), paragraph(question, s["body"]), KeepTogether([response_space(), Spacer(1, 8)])])
    story.append(paragraph("Self-check before submission", s["head1"]))
    for item in [
        "My response uses de-identified information.",
        "I have separated observations from assumptions.",
        "I have named the action within my role and the action that needs consultation or escalation.",
        "I have considered equity, dignity, participation, and confidentiality.",
    ]:
        story.append(paragraph(f"• {item}", s["bullet"]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(destination), pagesize=letter, leftMargin=0.82 * inch, rightMargin=0.82 * inch, topMargin=0.75 * inch, bottomMargin=0.72 * inch,
        title=f"{course.title} Practice Worksheet", author="SWEEP Academy",
    ).build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    courses = parse_outlines(args.source.resolve())
    output = args.output.resolve()
    for course in courses:
        prefix = f"{course.number:02d}-{slugify(course.title)}"
        build_guide(course, output / f"{prefix}-learner-guide.pdf")
        build_worksheet(course, output / f"{prefix}-practice-worksheet.pdf")
    print(f"Built {len(courses) * 2} PDFs in {output}")


if __name__ == "__main__":
    main()
