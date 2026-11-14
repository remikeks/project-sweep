"""Create the PDF-first learner resources from the unchanged authored source."""
import json
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("--release",type=Path,default=ROOT/"production_courseware/phase_three/fsw_media_01")
parser.add_argument("--package",type=Path,default=ROOT/"production_courseware/phase_two/fsw_batch_01/review_package.json")
args=parser.parse_args()
OUT=args.release
PACKAGE=args.package
data=json.loads(PACKAGE.read_text(encoding="utf-8"))
styles={
    "title":ParagraphStyle("Title",fontName="Helvetica-Bold",fontSize=23,leading=28,spaceAfter=18),
    "h1":ParagraphStyle("Heading1",fontName="Helvetica-Bold",fontSize=16,leading=21,spaceBefore=15,spaceAfter=9,keepWithNext=True),
    "h2":ParagraphStyle("Heading2",fontName="Helvetica-Bold",fontSize=13,leading=17,spaceBefore=11,spaceAfter=7,keepWithNext=True),
    "body":ParagraphStyle("Body",fontName="Helvetica",fontSize=12,leading=15,spaceAfter=8,splitLongWords=True,allowWidows=0,allowOrphans=0),
}


def p(text,kind="body"):
    return Paragraph(escape(text).replace("\n","<br/>"),styles[kind])


def document(path,story,code):
    def furniture(canvas,doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#17223B"))
        canvas.setFont("Helvetica",10)
        canvas.drawString(.8*inch,A4[1]-.45*inch,"SWEEP Academy   FSW   Draft for academic review")
        canvas.drawString(.8*inch,.4*inch,f"{code}   Version 0.1.0")
        canvas.drawRightString(A4[0]-.8*inch,.4*inch,f"Page {doc.page}")
        canvas.restoreState()
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=.8*inch,leftMargin=.8*inch,
        topMargin=.75*inch,bottomMargin=.7*inch,title=path.stem.replace("-"," "),author="SWEEP Academy").build(story,onFirstPage=furniture,onLaterPages=furniture)


(OUT/"pdf").mkdir(parents=True,exist_ok=True)
for c in data["courses"]:
    prefix=f"{c['code']}-{c['slug']}"
    story=[p(c["title"],"title"),p("School of Foundational Social Work Practice and Ethics"),
           p(f"{c['code']}   About {c['estimated_minutes']//60} hours including practice   Version 0.1.0"),
           p("This learner guide develops practical reasoning through three modules, fictional cases, exercises and feedback. It is a draft for academic review and has not been approved for learner release."),
           p("Learning outcome","h1"),p(c["outcome"]),p("Who this course is for","h1"),p(c["audience"]),
           p("How to study","h1"),p("Read each module and work through its case. Write your activity response before checking the feedback. Use fictional or fully de-identified situations. The slide deck provides a concise recap; this guide contains the fuller teaching and evidence notes."),
           p("Assessment and recognition","h1"),p("The draft course assessment contains 15 MCQs. Its proposed pass mark is 70 percent, requiring at least 11 correct answers. An approved course and a verified ParaLearn CBT pass are required for a course badge. A school certificate additionally requires every course in the approved school curriculum and a finalised school exam with MCQs, short answers and essays. Reading this draft does not award a credential."),
           p("Course structure","h1"),*[p(f"Module {m['order']}  {m['title']}") for m in c["modules"]],PageBreak()]
    for m in c["modules"]:
        story.extend([p(f"Module {m['order']} {m['title']}","h1"),p("Learning outcome: "+m["outcome"])])
        story.extend(p(t) for t in m["paragraphs"])
        for label,key in [("Worked case","example"),("Practice activity","activity"),("Feedback","feedback")]:
            story.extend([p(label,"h2"),p(m[key])])
    story.extend([p("References and evidence limits","h1"),p("Reference IDs identify the sources below. Cases and exercises are original fictional examples. International professional guidance is a practice benchmark; official Nigerian regulatory guidance is identified separately. Confirm applicable law and local procedures with an authorised supervisor."),p("Evidence review date 14 November 2026. Journal metrics do not certify an article's quality. Publisher metrics: https://www.frontiersin.org/about/impact and https://academic.oup.com/bjsw/pages/about. Source records distinguish reported quartiles from rank-based inferences. No Q1 or Q2 status is claimed for IJSDS.")])
    used={s for m in c["modules"] for s in m["sources"]}
    for r in data["references"]:
        if r["id"] not in used: continue
        story.append(KeepTogether([p(f"{r['id']} {r['author']} {r['year']}","h2"),p(r["title"]+". "+r["url"]),p("Use in this course: "+r["use"]+" Evidence limits: "+r["appraisal"]),p("Rights: "+r["licence"]+". "+("Journal ranking: "+r["quartile"]+"." if r.get("quartile") else ""))]))
    document(OUT/"pdf"/(prefix+"-learner-guide.pdf"),story,c["code"])
    worksheet=[]
    for m in c["modules"]:
        if worksheet: worksheet.append(PageBreak())
        worksheet.extend([p(c["title"]+" practice worksheet","title"),p(f"Module {m['order']} {m['title']}","h1"),p("Use a fictional or fully de-identified situation. Record your reasoning before consulting the learner-guide feedback."),p("Worked case","h2"),p(m["example"]),p("Your task","h2"),p(m["activity"])])
        for prompt in ["Relevant facts and uncertainties", "Your proposed action and reason", "Consultation or verification needed", "Action owner and review date"]:
            worksheet.extend([p(prompt,"h2"),Spacer(1,30)])
    document(OUT/"pdf"/(prefix+"-practice-worksheet.pdf"),worksheet,c["code"])
    print(c["code"],"learner guide and three-page practice worksheet created")
