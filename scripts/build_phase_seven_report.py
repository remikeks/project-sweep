"""Create the owner report and key-free media bundle after phase-seven proof."""
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
proof=json.loads((ROOT/"production_courseware/private/phase-seven/post-upload-verification.json").read_text())
assert proof["preexisting_parity"] and proof["private_resources_verified"]==16
assert len(proof["public_checks"])==19 and all(c["passed"] for c in proof["public_checks"])
assert (proof["total_courses"],proof["active_courses"],proof["total_assets"],proof["school_courses"],proof["school_target"])==(52,34,344,4,8)
release=ROOT/"production_courseware/phase_seven/gbv_media_01"
manifest=json.loads((release/"upload_manifest.json").read_text())
out=ROOT.parent/"output/academy_phase_seven"
out.mkdir(parents=True,exist_ok=True)
bundle=out/"SWEEP_GBV_Phase_7_Review_Materials.zip"
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
"Phase 7 adds the first four GBV school drafts: SWP-049 Gender Power and Intersectionality; SWP-050 Survivor Centred First Response and Referral; SWP-051 GBV Case Management and Safety Planning; and SWP-052 Trauma Informed Support and Service Coordination. They provide distinct introductory practice tasks without conferring specialist caseworker, clinical or forensic competence.",
"The batch contains twelve teaching modules, sixty original course MCQs and sixteen designed resources: four learner-guide PDFs, four worksheets, four editable slide decks and four matching slide PDFs. Guides use 12-point body text. All 104 final PDF pages, including sixty-four slides, were rendered and visually checked. Fictional adult exercises require no real disclosures or survivor records.",
"Research combines inter-agency programme standards and case-management guidance, the non-specialist Pocket Guide, WHO's 2025 training overview, Nigerian 2025/2026 survey analyses and an open-access provider-perspective synthesis. Appraisals distinguish publication from evidence dates, journal metrics from study validity, and a forthcoming issue from online publication. Reporting inconsistencies and access limitations remain visible; no local effect, legal duty or medical protocol is invented.",
"GBV has four inactive drafts against its target of eight. Remaining courses cover prevention and social norms; child marriage, FGM and harmful practices; technology-facilitated abuse; and ethical data/evaluation. The full-school scope plan includes all eight. The future ParaLearn exam must test all approved courses through MCQs, short answers and essays, with human marking and moderation. A complete exam blueprint and live provider provisioning remain pending.",
"Verification passed: 180 isolated tests, sixteen private resource hashes, retained-record fingerprints and nineteen public-access checks. The platform now has 52 courses: 34 active originals and eighteen inactive drafts, with 344 assets. Existing course content, CBT mappings, earlier drafts/resources and learner records remain unchanged. New resources are private and in review. All 25 coded schools remain closed to full-school enrolment and certification.",
"Next: develop GBV's remaining four courses using current specialist evidence and guidance, then build and review its full eight-course exam. Across the programme, eighteen of 150 proposed additions are authored; 132 remain. Continue aligned PDF/slide batches and push each verified build. Actual videos and checked captions/transcripts follow later.",
"Independent academic, specialist GBV/safeguarding, Nigerian practice/legal, accessibility/pilot and supervised-skills reviews remain necessary. Badges require approved courses and verified ParaLearn course-CBT passes. School certificates require all approved curriculum courses and a passed final moderated mixed exam. Head of Learning name/signature and authorised signatures remain pending. Founder: Prof. Mina Ogbanga.",
]
def footer(canvas,doc):
    canvas.setFont("Helvetica",9);canvas.setFillColor(colors.HexColor("#52617D"))
    canvas.drawString(48,25,"GBV four-course draft milestone | Target eight | Specialist review and ParaLearn verification pending")
report=out/"SWEEP_Phase_7_Report_Prof_Mina.pdf"
SimpleDocTemplate(str(report),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=40,bottomMargin=40,
    title="Phase 7 report to Prof. Mina Ogbanga",author="SWEEP Academy").build(
    [Paragraph("SWEEP Academy | Phase 7 progress",title),*[Paragraph(escape(p),body) for p in parts]],onFirstPage=footer,onLaterPages=footer)
assert len(PdfReader(report).pages)==1,"Owner report must remain one page"
print(report);print(bundle)
print("Verified seventeen ZIP entries; all sixteen media hashes match the staged manifest.")
