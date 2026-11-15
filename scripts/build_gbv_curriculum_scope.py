"""Map full GBV breadth without pretending four drafts are a school exam."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/"production_courseware/phase_seven/gbv_batch_01"

def scope():
    manifest=json.loads((ROOT/"schools/refactor_2026_11.json").read_text(encoding="utf-8"))
    school=next(s for s in manifest["schools"] if s["code"]=="GBV")
    package=json.loads((BATCH/"review_package.json").read_text(encoding="utf-8"))
    authored={c["title"]:c["code"] for c in package["courses"]}
    assert not school["existing"] and school["target"]==8 and len(school["new"])==8
    assert set(authored)==set(school["new"][:4])
    return dict(school_code="GBV",status="draft_for_review",version="0.1.0",evidence_checked_on="2026-11-15",
        target_course_count=8,authored_draft_count=4,draft_catalogue_complete=False,curriculum_approved=False,
        courses=[dict(title=title,course_code=authored.get(title),status="inactive_review_draft" if title in authored else "not_authored") for title in school["new"]],
        benchmark=dict(source_ids=["S10","S11","S12","S13"],selected_domains=["Gender power and inclusion","Survivor-centred first response","Specialist casework and referral boundaries","Non-clinical psychosocial support and coordination","Prevention and social norms","Harmful practices and age-appropriate safeguarding","Technology-facilitated abuse","Ethical information and programme evaluation"],
            limit="Sixteen inter-agency programme standards are a domain benchmark, not an eight-course accreditation mandate. Four courses remain unwritten; specialist review, adequate depth, Nigerian procedures and observed skills remain pending."),
        exam_plan=dict(status="not_authored_or_provisioned",provider="ParaLearn CBT",provider_assessment_id=None,provider_contract_verified=False,
            coverage="Every course in the final approved eight-course GBV curriculum, including the four not yet authored",
            proposed_items=dict(MCQ=40,SHORT_ANSWER=6,ESSAY=2),proposed_marks=100,human_written_marking_required=True,moderation_required=True,ai_only_finalisation=False,
            next_gate="Author the remaining courses, then develop and independently review a full-curriculum blueprint and question bindings; verify live mixed-exam capabilities and pilot before launch"),
        certification=dict(authorised=False,requirements=["Every approved curriculum course completed through verified ParaLearn course-CBT passes","Passed final full-curriculum ParaLearn MCQ/short-answer/essay exam after human marking and moderation","Authorised Head of Learning and Founder signatures"],
            head_of_learning="Name and signature pending",founder="Prof. Mina Ogbanga"),
        review=dict(academic="pending",specialist_GBV_and_safeguarding="pending",Nigerian_practice_and_legal="pending",accessibility_and_pilot="pending",supervised_skills="pending"))

if __name__=="__main__":
    data=scope()
    (BATCH/"school_exam_scope.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("GBV scope: four authored drafts, target eight; no school exam or certificate authorised.")
