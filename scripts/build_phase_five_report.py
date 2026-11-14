"""Create a legible one-page owner report after successful phase-five verification."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
proof=json.loads((ROOT/"production_courseware/private/phase-five/post-upload-verification.json").read_text())
assert proof["preexisting_parity"] and proof["private_resources_verified"]==16 and all(c["passed"] for c in proof["public_checks"])
out=ROOT.parent/"output/academy_phase_five/SWEEP_Phase_5_Report_Prof_Mina.pdf"
out.parent.mkdir(parents=True,exist_ok=True)
title=ParagraphStyle("Title",fontName="Helvetica-Bold",fontSize=19,leading=23,textColor=colors.HexColor("#0B2C7A"),spaceAfter=12)
body=ParagraphStyle("Body",fontName="Helvetica",fontSize=12,leading=15,spaceAfter=10,allowWidows=0,allowOrphans=0)
parts=[
"To: Prof. Mina Ogbanga, Founder, SWEEP Academy | 14 November 2026",
"Phase 5 adds four ERT foundation drafts: SWP-042 Ecosocial Systems and Environmental Justice; SWP-043 Participatory Ecological Vulnerability Assessment; SWP-044 Community Adaptation and Resilience Planning; and SWP-045 Heat Pollution and Environmental Health Inequity. They deepen the retained SWP-032 introduction through distinct practice outputs.",
"ERT now has five catalogue courses: one retained active course and four inactive drafts. Its target remains eight. The remaining courses cover displacement and livelihoods, Indigenous knowledge and community stewardship, and evaluation. These must be authored and reviewed before the full curriculum can be considered ready.",
"This batch contains twelve teaching modules, sixty draft course MCQs and sixteen designed resources: four learner guides, four worksheets, four editable slide decks and four matching slide PDFs. Guides use a 12-point body font. All 104 final PDF pages, including sixty-four slides, were visually checked. Source text, teaching-point coverage, file integrity and school identity checks passed.",
"Research includes recent open-access ecosocial and participation studies, a 2026 African pollution review, IJSDS Nigerian contextual evidence, IPCC synthesis, WHO 2026 heat guidance and adopted curriculum benchmarks. Appraisals state design, context, rights and limits. Indexed SJR Q1 records are distinguished from unverified ranking tables and JCR claims; journal rank does not certify article quality.",
"The provisional five-course exam map contains forty MCQ slots, six short answers and two essays, with written rubrics and required human marking/moderation. It must expand to all eight approved ERT courses before launch. School MCQs remain unbound and live ParaLearn support/provisioning remains pending.",
"Execution checks passed: 171 isolated tests, private resource hashes and retained-record fingerprints. The platform has 45 courses: 34 active originals and eleven inactive drafts. The sixteen new resources are in review, bringing assets to 316. Existing course content, CBT mappings and learner records remain unchanged. All 25 coded schools stay closed to full-school enrolment.",
"Next: develop the remaining three ERT courses and expand its exam map, while independent academic, Nigerian practice and accessibility/pilot reviews proceed. Across the programme, eleven of 150 proposed additions are authored; 139 remain. Continue aligned PDF/slide batches and push each verified phase. Actual videos and checked captions/transcripts follow later.",
"Badges require approved courses and verified ParaLearn course-CBT passes. School certificates require the entire approved curriculum and a passed, human-marked and moderated final mixed ParaLearn exam. The Head of Learning's name and authorised signatures remain pending. Founder: Prof. Mina Ogbanga.",
]
def footer(canvas,doc):
    canvas.setFont("Helvetica",9);canvas.setFillColor(colors.HexColor("#52617D"))
    canvas.drawString(48,25,"ERT foundation milestone | Drafts require review and full-curriculum completion")
SimpleDocTemplate(str(out),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=40,
    title="Phase 5 report to Prof. Mina Ogbanga",author="SWEEP Academy").build([Paragraph("SWEEP Academy | Phase 5 progress",title),*[Paragraph(escape(p),body) for p in parts]],onFirstPage=footer,onLaterPages=footer)
assert len(PdfReader(out).pages)==1,"Owner report must remain one page"
print(out)
