"""Produce the one-page owner report and key-free review ZIP after live checks."""
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile,ZIP_DEFLATED
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
proof=json.loads((ROOT/"production_courseware/private/phase-six/post-upload-verification.json").read_text())
assert proof["preexisting_parity"] and proof["private_resources_verified"]==12
assert len(proof["public_checks"])==16 and all(c["passed"] for c in proof["public_checks"])
assert (proof["total_courses"],proof["active_courses"],proof["total_assets"],proof["school_courses"])==(48,34,328,8)
release=ROOT/"production_courseware/phase_six/ert_media_02"
manifest=json.loads((release/"upload_manifest.json").read_text())
out=ROOT.parent/"output/academy_phase_six"
out.mkdir(parents=True,exist_ok=True)
bundle=out/"SWEEP_ERT_Phase_6_Review_Materials.zip"
with ZipFile(bundle,"w",ZIP_DEFLATED) as archive:
    for row in manifest:
        raw=(release/row["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row["sha256"]
        archive.writestr(row["path"],raw)
    archive.write(release/"README.md","README.md")
with ZipFile(bundle) as archive:
    assert archive.testzip() is None and len(archive.namelist())==13
    assert set(archive.namelist())=={r["path"] for r in manifest}|{"README.md"}
    for row in manifest:assert hashlib.sha256(archive.read(row["path"])).hexdigest()==row["sha256"]

title=ParagraphStyle("Title",fontName="Helvetica-Bold",fontSize=19,leading=23,textColor=colors.HexColor("#0B2C7A"),spaceAfter=12)
body=ParagraphStyle("Body",fontName="Helvetica",fontSize=12,leading=15,spaceAfter=10,allowWidows=0,allowOrphans=0)
parts=[
"To: Prof. Mina Ogbanga, Founder, SWEEP Academy | 14 November 2026",
"Phase 6 completes ERT's planned draft catalogue with SWP-046 Climate Displacement and Livelihood Adaptation; SWP-047 Indigenous Knowledge and Community Stewardship; and SWP-048 Evaluating Ecosocial Interventions. ERT now has eight courses: one retained active introduction and seven inactive drafts. Catalogue breadth is complete; academic approval and learner release remain pending.",
"The new batch provides nine teaching modules, forty-five original course MCQs and twelve designed resources: three learner-guide PDFs, three worksheets, three editable slide decks and three matching slide PDFs. Guides use 12-point body text. All 78 final PDF pages, including forty-eight slides, were rendered and visually checked. Source coverage, school identity, editable teaching points and file-integrity checks passed.",
"Evidence includes open-access displacement, Indigenous knowledge, participation and 2026 climate-services/adaptation reviews, IJSDS Nigerian context, Global Protection Cluster guidance, GIDA knowledge governance and OECD evaluation guidance. Appraisals record methods, evidence periods, access and rights. Publisher-reported Q2/Q1 metrics are distinguished from article validity. No source supports a universal practice, individual legal status or untested local effect.",
"The updated ParaLearn school-exam blueprint covers all eight ERT courses: forty MCQ slots, six short answers and two essays, totalling 100 marks. Every course has five MCQ slots and written coverage; both essays integrate the full curriculum. Written rubrics require human marking and moderation. Duration 210 minutes and pass mark 70 percent are proposals. Question binding, live provider support and provisioning remain pending; the exam has not launched.",
"Validation passed: 175 isolated tests, twelve private resource hashes, retained-record fingerprints and sixteen public-access checks. The platform has 48 courses: 34 active originals and fourteen inactive drafts, with 328 assets. Existing content, CBT mappings, previous drafts/resources and learner records remain unchanged. New assets are private and in review. All 25 coded schools stay closed to full-school enrolment and certification.",
"Next phase: develop the GBV school's first aligned batch against its eight-course plan, researching current curricula and evidence before authoring. Across the programme, fourteen of 150 proposed additions are authored and 136 remain. Continue independent academic, Nigerian practice/legal and accessibility/pilot review, then verified ParaLearn integration. Maintain PDF/slide materials; actual videos and checked captions/transcripts follow later.",
"Badges require approved courses and verified ParaLearn course-CBT passes. School certificates require all approved curriculum courses and a passed final mixed ParaLearn exam after human marking and moderation. The Head of Learning's name and authorised signatures remain pending. Founder: Prof. Mina Ogbanga.",
]
def footer(canvas,doc):
    canvas.setFont("Helvetica",9);canvas.setFillColor(colors.HexColor("#52617D"))
    canvas.drawString(48,25,"ERT eight-course draft catalogue | Independent review and ParaLearn verification pending")
report=out/"SWEEP_Phase_6_Report_Prof_Mina.pdf"
SimpleDocTemplate(str(report),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=40,
    title="Phase 6 report to Prof. Mina Ogbanga",author="SWEEP Academy").build(
    [Paragraph("SWEEP Academy | Phase 6 progress",title),*[Paragraph(escape(p),body) for p in parts]],onFirstPage=footer,onLaterPages=footer)
assert len(PdfReader(report).pages)==1,"Owner report must remain one page"
print(report)
print(bundle)
print("Verified thirteen ZIP entries; twelve media hashes match the staged manifest.")
