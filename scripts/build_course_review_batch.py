"""Compile authored course batches with evidence and assessment traceability."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from courses.authored_review import digest,validate_package
from courses.assessment_review_validation import validate_review_bank


def compile_package(source):
    package=dict(version="0.1.0",status="draft_for_review",evidence_checked_on="2026-11-14",
        review=dict(subject_matter="pending",Nigerian_practice_and_legal="pending",accessibility_and_pilot="pending",publication="not_approved"),
        references=source.REFERENCES,courses=[])
    if hasattr(source,"EVIDENCE_NOTE"):
        package["evidence_note"]=source.EVIDENCE_NOTE
    for authored in source.COURSES:
        course={k:v for k,v in authored.items() if k!="modules"}
        course["modules"]=[dict(order=i,**{k:v for k,v in m.items() if k!="items"}) for i,m in enumerate(authored["modules"],1)]
        catalogue=dict(code=course["code"],title=course["title"],slug=course["slug"],modules=course["modules"])
        bank=dict(status="draft_for_review",assessment_id=None,version="0.1.0",course_code=course["code"],course_slug=course["slug"],
            title=course["title"],proposed_pass_percent=70,minimum_correct=11,source_hash_encoding="canonical-json-sorted-keys-utf8",
            authoring_source_sha256=digest(course),catalogue_sha256=digest(catalogue),modules=[],questions=[])
        for order,module in enumerate(authored["modules"],1):
            points=[]
            for n,(point,stem,correct,distractors,rationale) in enumerate(module["items"],1):
                pid=f"{course['code']}-M{order}-T{n}"
                points.append(dict(id=pid,text=point))
                options=[dict(text=d,correct=False) for d in distractors]
                options.insert((order+n)%4,dict(text=correct,correct=True))
                bank["questions"].append(dict(id=f"{course['code']}-Q{len(bank['questions'])+1:02}",type="MCQ",marks=1,
                    module_order=order,teaching_point_id=pid,question=stem,options=options,rationale=rationale))
            bank["modules"].append(dict(order=order,title=module["title"],outcome=module["outcome"],teaching_points=points))
        course["assessment"]=bank
        package["courses"].append(course)
    validate_package(package)
    return package


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--authoring",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--previous-package",type=Path,action="append",default=[])
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location("authored_course_batch",args.authoring)
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    package=compile_package(source)
    prior=[]
    for file in args.previous_package:
        old=json.loads(file.read_text(encoding="utf-8"));validate_package(old)
        prior.extend(q["question"] for c in old["courses"] for q in c["assessment"]["questions"])
    for c in package["courses"]:
        validate_review_bank(c["assessment"],dict(code=c["code"],title=c["title"],slug=c["slug"],modules=c["modules"]),existing_stems=prior)
        prior.extend(q["question"] for q in c["assessment"]["questions"])
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"review_package.json").write_text(json.dumps(package,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary=dict(**validate_package(package),package_sha256=digest(package),prior_question_stems_checked=len(prior)-15*len(package["courses"]))
    (args.output/"validation.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(summary)


if __name__=="__main__":main()
