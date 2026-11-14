"""Authoring blueprint for the ERT five-course milestone, never a live exam."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from schools.exam_blueprints import validate_blueprint

def blueprint():
    codes=["SWP-032","SWP-042","SWP-043","SWP-044","SWP-045"]
    items=[dict(id=f"ERT-{code}-MCQ-{n:02}",type="MCQ",marks=1,course_codes=[code],question_binding=None)
        for code in codes for n in range(1,9)]
    short=[
        (["SWP-032"],"Two streets have similar flood exposure but different transport and caring arrangements. Give five checks that keep a climate-justice discussion person-centred and evidence-aware.",
         "Separate physical exposure from relevant vulnerability and capacity; examine access and livelihoods; include missing perspectives; use local and technical information with uncertainty visible; and identify an authorised next action with feedback.",
         ["Exposure and social context","Access and livelihood implications","Meaningful participation","Evidence and uncertainty","Accountable next step"]),
        (["SWP-042"],"A proposed shade project may improve market access but obstruct another group's route. Give five elements of an environmental-justice analysis without inventing technical findings.",
         "Trace a provisional pathway from the condition to participation; compare benefits and burdens; ask what affected groups can influence; recognise missing or different accounts; and identify evidence and appropriate decision authority.",
         ["Provisional pathway","Distribution of benefits and burdens","Procedural influence","Recognition and missing views","Evidence and decision authority"]),
        (["SWP-043"],"Draft five protocol requirements for a participatory assessment of access during rain, including a way to avoid unsupported technical certification.",
         "Define the decision and authority; provide accessible participation; collect only justified information under approved arrangements; distinguish reports, observations and technical information; and state verification, validation and specialist limits.",
         ["Purpose and authority","Participation access","Proportionate information handling","Evidence status","Validation and scope limits"]),
        (["SWP-044"],"A fictional contact arrangement has thirty exercise units: twelve for setup and four per month for three months. Calculate total and balance, then identify three non-arithmetic readiness checks.",
         "Total is twenty-four units and balance six. These are fictional units, not prices or spending authority. Check accepted delivery/approval roles, operational/accessibility resources and an explicit dependency or fallback before readiness is claimed.",
         ["Correct total twenty-four","Correct balance six with fictional-unit scope","Accepted roles and authority","Operation and accessibility","Dependency or fallback"]),
        (["SWP-045"],"A household reports heat and nearby smoke, forwards an undated screenshot and asks about medication. Describe five appropriate social work actions.",
         "Record the experience without inventing a diagnosis; verify current official source and measurement context; identify practical access barriers; route medication or urgent health questions to authorised clinical/emergency arrangements; and agree a feasible confidential next contact and follow-up.",
         ["Accurate information status","Source and measurement check","Access barriers","Clinical scope and urgency","Feasible authorised follow-up"]),
        (["SWP-043","SWP-044","SWP-045"],"After a pilot, messages sent increase but people still report a failed access route. Describe five features of a useful joint review.",
         "Check measure definitions and information coverage; include affected and missing perspectives; separate output from support accessed; consider competing explanations and unintended burdens; and assign an authorised revision with feedback and a review date.",
         ["Evidence coverage","Participation and validation","Output versus outcome","Alternative explanations and burdens","Revision ownership and feedback"]),
    ]
    for n,(coverage,prompt,model,criteria) in enumerate(short,1):
        items.append(dict(id=f"ERT-SA-{n:02}",type="SHORT_ANSWER",marks=5,course_codes=coverage,prompt=prompt,
            model_answer=model,rubric=[dict(criterion=x,marks=1) for x in criteria],human_marking_required=True))
    essays=[
        (codes[:4],"Develop a provisional adaptation plan for a fictional learning-centre access problem during recurring rain. Explain the environmental-justice analysis, a participatory assessment protocol and risk register, two options, the operating resources and a review trigger. Keep social work, technical assessment and decision authority distinct.",
         "Accept equivalent defensible plans that preserve participation, evidence status and scope. A sound answer distinguishes the hazard from exposure, vulnerability and capacity; examines distribution, influence and recognition; includes accessible proportionate information gathering and validation; compares trade-offs and possible maladaptation; and identifies roles, resources, dependencies and review. Unsupported engineering certification or funding promises receive no relevant criterion marks.",
         ["Climate-risk context and justice analysis","Participatory protocol and information handling","Provisional register and uncertainty","Options and unintended consequences","Delivery resources authority and review"]),
        (codes,"A fictional neighbourhood service plans support during heat and pollution concerns, but residents have different housing, work and communication access. Propose an ethical and feasible pathway, including whose knowledge enters the decision, source checks, role boundaries, a safe readiness exercise and monitoring. Explain what the evidence can and cannot establish.",
         "A sound answer connects environmental and social conditions without diagnosing individuals; includes meaningful influence and missing perspectives; verifies current authorised information and clinical/technical referral roles; confirms delivery and fallback using a fictional tabletop exercise; and distinguishes contacts, access and outcomes with alternative explanations. Do not credit medication instructions, invented warning limits, unsupported interaction claims or a simulation presented as proof of health effects.",
         ["Environmental context and distribution","Participatory assessment and recognition","Authorised messages clinical and technical scope","Operational readiness and safe exercise","Monitoring interpretation and accountable revision"]),
    ]
    for n,(coverage,prompt,model,criteria) in enumerate(essays,1):
        items.append(dict(id=f"ERT-ESSAY-{n:02}",type="ESSAY",marks=15,course_codes=coverage,prompt=prompt,
            model_answer=model,rubric=[dict(criterion=x,marks=3,scoring="0 absent/unsafe; 1 limited relevant point; 2 defensible reasoning with an important omission; 3 coherent contextual reasoning with feasible action and evidence limits.") for x in criteria],human_marking_required=True))
    return dict(status="draft_for_review",school_code="ERT",curriculum_version="ERT-provisional-five-course-0.1.0",
        provider="ParaLearn CBT",provider_assessment_id=None,provider_contract_verified=False,required_courses=codes,
        programme_target_course_count=8,curriculum_complete=False,
        remaining_curriculum_titles=["Climate Displacement and Livelihood Adaptation","Indigenous Knowledge and Community Stewardship","Evaluating Ecosocial Interventions"],
        scope_note="Five-course draft breadth milestone only. Extend and re-review the blueprint for all eight approved ERT courses before launch; this file cannot authorise an exam or certificate.",
        proposed_duration_minutes=180,duration_status="Proposed; requires academic review, adjustments and learner piloting",
        marking_policy=dict(proposed_pass_percent=70,moderation_required=True,ai_only_finalisation=False,
            rubric_rule="Accept equivalent defensible reasoning. Award criterion marks with a rationale, then human moderation before finalisation.",
            appeals="Preserve original responses, rubric version, marker, moderation decision and amendment history, with an authorised appeal route."),
        certification=dict(authorised=False,requirements=["Complete all eight approved ERT courses through verified course CBT passes","Pass the final full-curriculum ParaLearn exam after human marking and moderation","Receive authorised Head of Learning and Founder signatures; Head of Learning details pending; Founder Prof. Mina Ogbanga"]),items=items)

if __name__=="__main__":
    data=blueprint();print(validate_blueprint(data))
    (ROOT/"production_courseware/phase_five/ert_batch_01/school_exam_blueprint.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
