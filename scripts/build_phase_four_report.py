"""Create the one-page owner report after live phase-four verification."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
proof=json.loads((ROOT/"production_courseware/private/phase-four/post-upload-verification.json").read_text())
assert proof["preexisting_parity"] and proof["private_resources_verified"]==20 and all(c["passed"] for c in proof["public_checks"])
out=ROOT.parent/"output/academy_phase_four/SWEEP_Phase_4_Report_Prof_Mina.pdf"
out.parent.mkdir(parents=True,exist_ok=True)
title=ParagraphStyle("Title",fontName="Helvetica-Bold",fontSize=19,leading=23,textColor=colors.HexColor("#0B2C7A"),spaceAfter=12)
body=ParagraphStyle("Body",fontName="Helvetica",fontSize=12,leading=15,spaceAfter=10,allowWidows=0,allowOrphans=0)
parts=[
    "To: Prof. Mina Ogbanga, Founder, SWEEP Academy | 14 November 2026",
    "Phase 4 completes the proposed ten-course FSW draft catalogue: three retained health-application courses and seven new foundational drafts. This phase adds SWP-037 to SWP-041, covering human development, communication, professional records, referral networks, and reflective practice and supervision.",
    "The five new courses contain 15 modules and 75 draft course MCQs. Each has a six-page learner guide, three-page worksheet, editable sixteen-slide deck and matching slide PDF. The twenty resources use consistent styling, readable 12-point PDF text and large slide text. All 125 final PDF pages were visually checked; source teaching and teaching-point coverage also passed automated checks.",
    "Research includes recent open-access communication, documentation and reflective-practice reviews; IJSDS Nigerian contextual research; professional education guidance; and the official Nigerian data-protection directive. Source records explain design, rights, context and evidence limits. Journal rankings are distinguished from article quality and from independent ranking verification.",
    "The final school-exam draft now covers all ten FSW courses: 40 MCQs, six short answers and two essays, totalling 100 marks. Written questions have rubrics and require human marking and moderation. School MCQ slots remain unbound; live ParaLearn support and provider assessment creation remain pending.",
    "Execution checks passed: 166 isolated tests, private file hashes and retained-record fingerprints. The platform has 41 courses: 34 active originals and seven inactive drafts. The twenty new assets are in review, bringing assets to 300. Original course content, CBT mappings and learner records are unchanged. All 25 coded schools remain closed to full-school enrolment.",
    "Next: independent academic and Nigerian practice review, accessibility and learner piloting, plus verified ParaLearn provisioning. Continue research-backed PDF/slide batches across the remaining schools; 143 of the 150 proposed new courses remain to be authored. ERT's next foundation batch can add four courses to its one retained course, followed by its remaining target and the other schools.",
    "Course badges require approved courses and verified course CBT passes. School certificates require all approved curriculum courses and the passed, moderated final school exam. The Head of Learning's name and authorised signatures remain pending. Founder: Prof. Mina Ogbanga. Videos and checked captions/transcripts follow later. Each completed phase is committed and pushed after verification.",
]
story=[Paragraph("SWEEP Academy | Phase 4 progress",title)]
story.extend(Paragraph(escape(p),body) for p in parts)
def footer(canvas,doc):
    canvas.setFont("Helvetica",9)
    canvas.setFillColor(colors.HexColor("#52617D"))
    canvas.drawString(48,25,"FSW draft catalogue and learning materials | Review required before release")
SimpleDocTemplate(str(out),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=40,
    title="Phase 4 report to Prof. Mina Ogbanga",author="SWEEP Academy").build(story,onFirstPage=footer,onLaterPages=footer)
assert len(PdfReader(out).pages)==1,"Owner report must remain one page"
print(out)
