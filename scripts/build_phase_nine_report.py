"""Local and live proof-gated owner report; key-free private review bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph

ROOT=Path(__file__).resolve().parents[1]
proof=json.loads((ROOT/"production_courseware/private/phase-nine/local-build-verification.json").read_text())
assert proof["protected_source_unchanged"] and proof["tests"]>=191
assert proof["media_files"]==16 and proof["pdf_pages"]==105
live=json.loads((ROOT/"production_courseware/private/phase-nine/post-upload-verification.json").read_text())
assert live["preexisting_parity"] and live["private_resources_verified"]==16
assert len(live["public_checks"])==33 and all(row["passed"] for row in live["public_checks"])
assert (live["total_courses"],live["active_courses"],live["total_assets"],live["school_courses"],live["school_target"],live["closed_coded_schools"])==(60,34,376,10,10,25)
release=ROOT/"production_courseware/phase_nine/mhp_media_01"
manifest=json.loads((release/"upload_manifest.json").read_text())
out=ROOT.parent/"output/academy_phase_nine"
out.mkdir(parents=True,exist_ok=True)
bundle=out/"SWEEP_MHP_Phase_9_Private_Review_Materials.zip"
secret=re.compile(rb"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sb_secret_[A-Za-z0-9]+|gh[pousr]_[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{30,}|eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,})")
with ZipFile(bundle,"w",ZIP_DEFLATED) as archive:
    for row in manifest:
        path=release/row["path"]
        raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row["sha256"]
        if path.suffix==".pdf":
            text="\n".join(p.extract_text() for p in PdfReader(path).pages).encode()
        else:
            with ZipFile(path) as pptx:
                text=b"\n".join(pptx.read(n) for n in pptx.namelist() if n.endswith(".xml"))
        assert not secret.search(text),"Possible secret found in learner file"
        assert b'"correct":' not in text and b'"model_answer":' not in text and b'is_correct' not in text
        archive.writestr(row["path"],raw)
    archive.write(release/"README.md","README.md")
with ZipFile(bundle) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist())==17
    assert set(archive.namelist())=={r["path"] for r in manifest}|{"README.md"}
    for row in manifest:
        assert hashlib.sha256(archive.read(row["path"])).hexdigest()==row["sha256"]

parser=argparse.ArgumentParser()
parser.add_argument("--font-regular",type=Path,required=True)
parser.add_argument("--font-bold",type=Path,required=True)
args=parser.parse_args()
pdfmetrics.registerFont(TTFont("ReportSans",str(args.font_regular)))
pdfmetrics.registerFont(TTFont("ReportSans-Bold",str(args.font_bold)))
title=ParagraphStyle("Title",fontName="ReportSans-Bold",fontSize=19,leading=23,textColor=colors.HexColor("#0B2C7A"),spaceAfter=12)
body=ParagraphStyle("Body",fontName="ReportSans",fontSize=12,leading=15,spaceAfter=10,allowWidows=0,allowOrphans=0)
parts=[
"To: Prof. Mina Ogbanga, Founder, SWEEP Academy | 16 November 2026",
"Phase 9 completes the ten-title MHP draft catalogue. Six original courses SWP-004–009 remain unchanged. Four additions cover trauma-informed and culturally responsive care (057), community rights and recovery (058), child/adolescent/family support (059), and safe service coordination (060). Cloud authoring was independently verified and privately staged through the existing local publishing connection.",
f"The additions contain twelve modules and sixty original MCQs checked against 330 prior stems. Sixteen resources comprise four guides (8/7/7/7 pages), four three-page worksheets, four editable sixteen-slide decks and matching slide PDFs. All {proof['pdf_pages']} final PDF pages were rendered and visually reviewed. Guides use embedded fonts and 12-point body text. Exercises use fictional cases and invented aggregates; no personal trauma histories, real child interviews or health records.",
"Evidence appraisal remains dated 15 November. WHO/UNICEF service guidance and six appraised studies retain search dates, methods, rights and access limitations. Conceptual, qualitative and scoping findings do not prove treatment effects or Nigerian service availability. The small IJSDS provider survey has inconsistent reporting; its numerical findings and reserved-rights source material are not reproduced.",
"The full-school exam blueprint covers all ten courses: forty unbound MCQ slots, six short answers and two essays, 100 marks. It requires human written marking, independent moderation and appeal history. Proposed 210 minutes and 70% pass need review and piloting. Provider assessment IDs remain null, ParaLearn mixed-item support unverified and certification unauthorised, even for a perfect offline result.",
f"Verification passed: {proof['tests']} isolated tests, sixteen private remote resource hashes, retained-record fingerprints and 33 public-access checks. Protected checkpoint source files match Git after Windows text-newline normalisation; prior binary media remain byte-identical. The platform now has 60 courses: 34 active originals and 26 inactive drafts, with 376 assets. MHP has six retained active courses and four inactive additions. Original teaching, CBT mappings, earlier drafts/resources and learner/credential records remain unchanged.",
"Keep additions inactive, resources private/in review and all 25 coded schools closed. Badges require approved courses and verified course-CBT passes; certificates additionally require all approved school courses and the final moderated mixed-exam pass. Academic, clinical/child-safeguarding, Nigerian practice/legal, lived-experience, supervised-skills and accessibility/pilot reviews remain pending. Head of Learning name/signature pending; Founder: Prof. Mina Ogbanga. Authorised signatures are required.",
"Next build: PCEI, target eight courses, retaining its three originals and developing five researched additions, aligned PDFs/slides and a full-school mixed exam. Verify and push each accurate phase. Authored progress: 26 of 150 additions; 124 remain. Actual videos and checked captions/transcripts follow later. The seventeen-entry private review ZIP excludes staff keys, exam rubrics, raw papers and operational receipts.",
]
def footer(canvas,doc):
    canvas.setFont("ReportSans",9)
    canvas.setFillColor(colors.HexColor("#52617D"))
    canvas.drawString(48,25,"MHP ten-course draft catalogue complete | Private academic review | ParaLearn verification pending")
report=out/"SWEEP_Phase_9_Report_Prof_Mina.pdf"
SimpleDocTemplate(str(report),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=35,bottomMargin=40,
                  title="Phase 9 report to Prof. Mina Ogbanga",author="SWEEP Academy").build(
    [Paragraph("SWEEP Academy | MHP Phase 9",title),*[Paragraph(escape(p),body) for p in parts]],onFirstPage=footer,onLaterPages=footer)
assert len(PdfReader(report).pages)==1,"Owner report must remain one legible page"
print(report)
print(bundle)
print("Reopened ZIP: 17 allowlisted entries, sixteen matching hashes, no staff keys or detected secrets.")
