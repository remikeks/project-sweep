"""Build readable course-review documents with the bundled artifact runtime."""
import argparse
import json
from pathlib import Path
import re

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"production_courseware/phase_two/fsw_batch_01"
OUT=ROOT.parent/"output/academy_phase_two"


def heading(text):
    return re.sub(r"[^\w\s]", " ", text).strip()


def new_doc(label):
    doc=Document()
    section=doc.sections[0]
    section.page_width=Inches(8.27)
    section.page_height=Inches(11.69)
    section.top_margin=section.bottom_margin=Inches(.75)
    section.left_margin=section.right_margin=Inches(.8)
    for style in ("Normal","Title","Subtitle","Heading 1","Heading 2"):
        s=doc.styles[style]
        s.font.name="Arial"
        s.font.color.rgb=RGBColor(0,0,0)
        s.paragraph_format.space_after=Pt(7)
    normal=doc.styles["Normal"]
    normal.font.size=Pt(12)
    normal.paragraph_format.line_spacing=1.08
    for name,size in [("Title",22),("Heading 1",16),("Heading 2",13),("Subtitle",12)]:
        doc.styles[name].font.size=Pt(size)
    header=section.header.paragraphs[0]
    header.text="SWEEP Academy   |   FSW   |   Draft for academic review"
    header.style="Normal"
    header.runs[0].font.size=Pt(10)
    footer=section.footer.paragraphs[0]
    footer.text=label+"   |   Page "
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    footer.runs[0].font.size=Pt(10)
    for part in (doc.styles.element, doc.element):
        for border in list(part.iter(qn('w:pBdr'))):
            border.getparent().remove(border)
    return doc


def course_doc(course, refs):
    doc=new_doc(course["code"]+"   |   Version 0.1.0")
    doc.add_paragraph(heading(course["title"]),"Title")
    doc.add_paragraph("School of Foundational Social Work Practice and Ethics", "Subtitle")
    doc.add_paragraph(f"{course['code']}  |  About {course['estimated_minutes']//60} hours including practice  |  14 November 2026")
    doc.add_paragraph("This learner guide is a teaching draft for academic review. It develops practical reasoning through three modules, fictional cases, exercises and feedback. It has not been approved for learner release.")
    doc.add_heading("Learning outcome",1)
    doc.add_paragraph(course["outcome"])
    doc.add_heading("Who this course is for",1)
    doc.add_paragraph(course["audience"])
    doc.add_heading("How to study",1)
    doc.add_paragraph("Read each module, work through its case and write your response to the activity before reading the feedback. Use fictional or fully de-identified situations. Check current local procedures with an authorised supervisor when applying learning in practice.")
    doc.add_heading("Assessment and recognition",1)
    doc.add_paragraph("The draft course assessment contains 15 MCQs. Its proposed pass mark is 70 percent, requiring at least 11 correct answers. Release and badge eligibility depend on an approved course and a verified ParaLearn CBT result. Reading this draft does not award a badge or school certificate.")
    doc.add_heading("Course structure",1)
    for m in course["modules"]:
        doc.add_paragraph(f"Module {m['order']}  {m['title']}")
    for m in course["modules"]:
        if m["order"] == 1:
            doc.add_page_break()
        doc.add_heading(heading(f"Module {m['order']} {m['title']}"),1)
        doc.add_paragraph("By the end of this module you should be able to: "+m["outcome"])
        for p in m["paragraphs"]:
            doc.add_paragraph(p)
        for title,key in [("Worked case","example"),("Practice activity","activity"),("Feedback","feedback")]:
            doc.add_heading(title,2);doc.add_paragraph(m[key])
    doc.add_heading("References and evidence limits",1)
    doc.add_paragraph("Reference IDs in the lessons identify the sources below. Research informs the discussion; the cases and exercises are original teaching examples. The steps taught are not an experimentally validated SWEEP intervention or a substitute for jurisdiction-specific law and professional supervision.")
    used=set(r for m in course["modules"] for r in m["sources"])
    for r in refs:
        if r["id"] not in used: continue
        doc.add_heading(heading(r["id"]+" "+r["author"]+" "+str(r["year"])),2)
        doc.add_paragraph(r["title"]+". "+r["url"])
        doc.add_paragraph("Use in this course: "+r["use"]+" Evidence limits: "+r["appraisal"])
        doc.add_paragraph("Rights: "+r["licence"]+". "+("Journal ranking: "+r["quartile"]+"." if r.get("quartile") else ""))
    doc.add_paragraph("Source review date 14 November 2026. Publisher quartiles, where stated, describe a journal metric and do not certify the quality of an individual paper. The publisher ranking table is at https://www.frontiersin.org/about/impact. No Q1 or Q2 status is claimed for IJSDS.")
    return doc


def report(staged=False):
    doc=new_doc("Phase two progress   |   14 November 2026")
    doc.styles["Title"].font.size=Pt(20)
    doc.add_paragraph("SWEEP Academy phase two progress", "Title")
    doc.add_paragraph("To Prof Mina Ogbanga   |   Founder SWEEP Academy", "Subtitle")
    doc.add_paragraph("The 25 coded schools are in place and the original 34 courses retain their content and ParaLearn course CBT mappings. This phase develops the first two additional courses and the requirements for a final mixed school examination.")
    doc.add_heading("First course development batch",1)
    doc.add_paragraph("FSW has two new teaching drafts: SWP-035 Social Work Values and Ethical Decision Making and SWP-036 Generalist Assessment and Case Management. Together they contain six modules, worked cases, practice exercises, feedback and 30 MCQs with rationales. "+("Both courses are staged as inactive records; all pre-existing academy records passed the before and after parity check." if staged else "Both courses are prepared for inactive staging; release remains closed."))
    doc.add_paragraph("The batch uses professional standards and recent open-access research, including a full-text IJSDS review with Nigerian context. Evidence records state methods, limitations, licences and the limits of publisher-reported journal quartiles. Subject-matter review, local practice review and learner piloting remain outstanding.")
    doc.add_heading("Final school examination",1)
    doc.add_paragraph("The draft FSW blueprint covers all five courses in its proposed first curriculum: 40 MCQs worth 40 marks, six short answers worth 30 marks and two essays worth 30 marks. Eight written prompts have marking guidance and rubrics. The 40 MCQ slots still require approved question bindings. The proposed pass mark is 70 percent and the proposed duration is 150 minutes, subject to academic review and piloting.")
    doc.add_paragraph("The school exam will use ParaLearn CBT. Live support for written marking, moderation and final-result reconciliation remains unverified because the integration credential could not be retrieved from Vercel. An offline validation contract rejects incomplete course coverage and unmarked written answers; it does not activate certification.")
    doc.add_heading("Next release conditions",1)
    doc.add_paragraph("Complete academic and local practice review, create the approved learning resources and ParaLearn course assessments, then publish the courses. Verify the mixed school-exam workflow end to end before opening school enrolment. Course badges require verified course CBT passes; certificates require all curriculum courses and a finalised, moderated school exam.")
    doc.add_paragraph("The certificate will name Prof Mina Ogbanga as Founder and the Head of Learning. The Head of Learning name and both approved signatures remain to be supplied. No signature has been invented and no school certificate has been enabled. Continue course development across the remaining schools against the approved 5 to 10 course targets.")
    return doc


parser=argparse.ArgumentParser()
parser.add_argument("--report-only",action="store_true")
parser.add_argument("--staged",action="store_true")
args=parser.parse_args()
OUT.mkdir(parents=True,exist_ok=True)
data=json.loads((SOURCE/"review_package.json").read_text(encoding="utf-8"))
if not args.report_only:
    for c in data["courses"]:
        path=OUT/(c["code"]+"_Learner_Guide_Draft.docx")
        course_doc(c,data["references"]).save(path)
        print(path)
path=OUT/"Phase_Two_Progress_Prof_Mina.docx"
report(args.staged).save(path)
print(path)
