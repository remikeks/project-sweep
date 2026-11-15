"""Proof-gated one-page owner report and answer-key-free review media ZIP."""
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
proof=json.loads((ROOT/"production_courseware/private/phase-eight/post-upload-verification.json").read_text())
assert proof["preexisting_parity"] and proof["private_resources_verified"]==16
assert len(proof["public_checks"])==23 and all(c["passed"] for c in proof["public_checks"])
assert (proof["total_courses"],proof["active_courses"],proof["total_assets"],proof["school_courses"],proof["school_target"])==(56,34,360,8,8)
release=ROOT/"production_courseware/phase_eight/gbv_media_02"
manifest=json.loads((release/"upload_manifest.json").read_text())
out=ROOT.parent/"output/academy_phase_eight";out.mkdir(parents=True,exist_ok=True)
bundle=out/"SWEEP_GBV_Phase_8_Review_Materials.zip"
with ZipFile(bundle,"w",ZIP_DEFLATED) as archive:
    for row in manifest:
        raw=(release/row["path"]).read_bytes();assert hashlib.sha256(raw).hexdigest()==row["sha256"]
        archive.writestr(row["path"],raw)
    archive.write(release/"README.md","README.md")
with ZipFile(bundle) as archive:
    assert archive.testzip() is None and len(archive.namelist())==17
    assert set(archive.namelist())=={r["path"] for r in manifest}|{"README.md"}
    for row in manifest:assert hashlib.sha256(archive.read(row["path"])).hexdigest()==row["sha256"]
title=ParagraphStyle("Title",fontName="Helvetica-Bold",fontSize=19,leading=23,textColor=colors.HexColor("#0B2C7A"),spaceAfter=12)
body=ParagraphStyle("Body",fontName="Helvetica",fontSize=12,leading=15,spaceAfter=10,allowWidows=0,allowOrphans=0)
parts=[
"To: Prof. Mina Ogbanga, Founder, SWEEP Academy | 15 November 2026",
"Phase 8 completes the proposed eight-course GBV draft catalogue. Four additions are authored: SWP-053 Community Prevention and Social Norms Change; SWP-054 Child Marriage FGM and Harmful Practices; SWP-055 Technology Facilitated Abuse and Digital Safety; and SWP-056 Ethical GBV Data and Programme Evaluation.",
"This batch adds twelve modules, sixty original MCQs and sixteen resources: four learner-guide PDFs, four three-page worksheets, four editable PowerPoints and four matching slide PDFs. Guides use 12-point body text. All 104 PDF pages, including sixty-four slides, were rendered and visually reviewed. Exercises use non-graphic fictional scenarios and aggregate data; no real survivor records, credentials or images are required.",
"Evidence combines updated child-marriage guidance, WHO's 2025 prevention framework and FGM overview, UN Women's digital-violence strategy, UNFPA's October 2026 data guidance and recent open-access reviews. Source records distinguish research dates, methods, certainty, rights and access limits. Stated knowledge or commitment is not demonstrated violence reduction; service counts are not prevalence; a listed measure is not automatically validated for Nigeria.",
"The full eight-course ParaLearn exam blueprint has forty MCQs, six short answers and two essays, totalling 100 marks. Every course has MCQ and written coverage. Human written marking, moderation and an appeal record are required. The proposed 210-minute duration and 70% pass mark need review and piloting. Provider capability, question binding and live assessment creation remain unverified; the blueprint cannot issue a certificate.",
"Verification passed: 185 isolated tests, sixteen private resource hashes, retained-record fingerprints and twenty-three public-access checks. The platform has 56 courses: 34 active originals and twenty-two inactive drafts, with 360 assets. Original teaching, CBT mappings, previous drafts/resources and learner records remain unchanged. All eight GBV courses are inactive and in review; all 25 coded schools remain closed to full-school enrolment and certification.",
"Next build: develop MHP's four additions around its six unchanged courses, research their curriculum fit, produce aligned PDFs/slides and the full ten-course mixed exam, verify parity and push. Programme progress: twenty-two of 150 proposed additions authored; 128 remain. Actual videos and checked captions/transcripts follow later.",
"Independent academic, GBV/safeguarding, Nigerian practice/legal, accessibility/pilot and supervised-skills reviews remain pending. Badges require approved courses and verified course-CBT passes. Certificates require all approved school courses and a passed final moderated mixed exam. Head of Learning name/signature and authorised signatures are pending. Founder: Prof. Mina Ogbanga.",
]
def footer(canvas,doc):
    canvas.setFont("Helvetica",9);canvas.setFillColor(colors.HexColor("#52617D"))
    canvas.drawString(48,25,"GBV eight-course draft catalogue complete | Academic review and live ParaLearn verification pending")
report=out/"SWEEP_Phase_8_Report_Prof_Mina.pdf"
SimpleDocTemplate(str(report),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=40,
    title="Phase 8 report to Prof. Mina Ogbanga",author="SWEEP Academy").build(
    [Paragraph("SWEEP Academy | Phase 8 progress",title),*[Paragraph(escape(p),body) for p in parts]],onFirstPage=footer,onLaterPages=footer)
assert len(PdfReader(report).pages)==1,"Owner report must remain one page"
print(report);print(bundle)
print("Verified seventeen ZIP entries and all sixteen staged media hashes.")
