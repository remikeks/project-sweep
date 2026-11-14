"""Full ERT draft catalogue exam map; no live provider creation or grading."""
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from schools.exam_blueprints import validate_blueprint

def blueprint():
    spec=importlib.util.spec_from_file_location("ert_milestone",ROOT/"scripts/build_ert_five_course_exam.py")
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    data=old.blueprint()
    codes=["SWP-032",*[f"SWP-{n:03}" for n in range(42,49)]]
    items=[dict(id=f"ERT8-{code}-MCQ-{n:02}",type="MCQ",marks=1,course_codes=[code],question_binding=None)
           for code in codes for n in range(1,6)]
    short=[
        (codes[:3],"Two streets have similar flood exposure but different access, livelihoods and influence over decisions. Give five requirements for a climate-justice and participatory assessment note.",
         "Distinguish physical exposure from vulnerability and capacity; trace a provisional environmental-social pathway; examine who benefits or carries burdens; enable missing voices to influence a decision; and distinguish reports from verified information with appropriate technical authority.",
         ["Exposure vulnerability and capacity","Provisional ecosocial pathway","Distribution of benefits and burdens","Meaningful accessible participation","Evidence status and decision authority"]),
        (["SWP-044"],"A fictional plan has thirty units, twelve for setup and four monthly for three months. Give total and balance, and three non-arithmetic readiness checks.",
         "Total twenty-four and balance six fictional units. Check accepted delivery and approval roles, operating and accessibility resources, and dependencies or fallback. The balance is neither real market pricing nor spending permission.",
         ["Total twenty-four","Balance six and fictional-unit limits","Accepted roles and authority","Operation and accessibility","Dependency or fallback"]),
        (["SWP-045"],"A resident reports heat and smoke, forwards an undated screenshot and asks about medication. Give five appropriate actions within the social work role.",
         "Record the experience without diagnosis; verify official information and measurement context; identify practical access barriers; use authorised clinical or emergency arrangements for medication or urgent concerns; and agree a feasible confidential follow-up without inventing a warning threshold.",
         ["Accurate information status","Source and measurement checks","Practical access barriers","Clinical scope and urgency","Authorised confidential follow-up"]),
        (["SWP-046"],"A displaced trader wants to consider staying but lacks reliable service access. A report counts relocation as a durable solution. Give five corrections for an appropriate support review.",
         "Separate the trader's preference from constraints and revisit changing choices; investigate livelihood and care conditions; verify receiving-service capacity without promises; support informed voluntary consideration of pathways; and assess sustained rights and access rather than movement alone, using relevant protection or legal expertise.",
         ["Preference and constraint distinction","Livelihood and care conditions","Verified capacity and bounded referral","Voluntary informed pathways","Rights access and specialist limits"]),
        (["SWP-047"],"Contributors permit an internal knowledge summary but a sponsor requests a named online map. Give five requirements before any broader sharing.",
         "Clarify the new purpose and output; check appropriate collective authority and individual rights; respect restricted knowledge and attribution preferences; assess location/context identification risk and approved digital handling; and provide contributor review, correction and an accountable response with honest withdrawal limits.",
         ["Specific changed scope","Collective and individual authority","Restrictions and attribution distinct from consent","Identification risk and digital handling","Review response and realistic withdrawal limits"]),
        (["SWP-048"],"An evaluation records access for twelve of twenty respondents before an activity and eighteen of thirty later. Give five elements of a defensible findings and response note.",
         "Both proportions are sixty percent; report numerator denominator period and respondent coverage; examine missing voices and differing groups; avoid causal attribution from the uncontrolled comparison; and assign a response owner and review point for the supported finding or evidence gap.",
         ["Correct equal sixty-percent proportions","Transparent counts period and coverage","Missing perspectives and group differences","Bounded causal interpretation","Accountable response and review"]),
    ]
    for n,(coverage,prompt,model,criteria) in enumerate(short,1):
        items.append(dict(id=f"ERT8-SA-{n:02}",type="SHORT_ANSWER",marks=5,course_codes=coverage,prompt=prompt,
            model_answer=model,rubric=[dict(criterion=x,marks=1) for x in criteria],human_marking_required=True))
    essays=[
        (codes,"For a fictional flood-affected community with differing mobility preferences, propose a bounded ecosocial support and adaptation plan. Integrate climate justice, participatory assessment, options and operating resources, heat/pollution information and referral boundaries, livelihood continuity, knowledge permissions and an evaluation question. Explain what requires authority or further evidence.",
         "Credit coherent reasoning across all eight courses: environmental-social pathways and distribution; accessible assessment and influence; realistic options, resources and clinical/technical limits; informed choices, livelihood access and bounded knowledge governance; and a relevant evaluation design with denominators, missing perspectives, alternative explanations and accountable revision. Do not credit forced relocation, legal or engineering certification, medication advice, unrestricted knowledge publication or a movement count presented as a durable solution.",
         ["Climate justice ecosocial reasoning and participatory assessment (032/042/043)","Adaptation delivery and heat/pollution scope (044/045)","Voluntary mobility livelihood and durable-access review (046)","Knowledge authority permission and stewardship (047)","Evaluation evidence limits and accountable use (048)"]),
        (codes,"Critique a fictional project's claim of success: a flood intervention distributed guides, relocated households and published a community knowledge map without clear permissions. Access reports changed from twelve of twenty to eighteen of thirty respondents, while heat messages lack dates and operating support remains unconfirmed. Write a justified corrective plan and evaluation brief across the full ERT curriculum.",
         "A strong answer distinguishes outputs from outcomes, examines justice and missing voices, verifies the assessment and current information, checks resources and professional role boundaries, revisits voluntary preferences and sustained access, reviews and restricts unapproved knowledge use through appropriate authority, and correctly interprets both rates as sixty percent without causal overclaim. Recommendations need named responsible roles, dependencies, feedback and review; equivalent defensible reasoning is accepted.",
         ["Environmental justice evidence and participatory gaps (032/042/043)","Delivery readiness and authoritative health information (044/045)","Informed mobility and livelihood/access conditions (046)","Knowledge-use scope and corrective governance (047)","Correct proportions bounded judgement and follow-through (048)"]),
    ]
    for n,(coverage,prompt,model,criteria) in enumerate(essays,1):
        items.append(dict(id=f"ERT8-ESSAY-{n:02}",type="ESSAY",marks=15,course_codes=coverage,prompt=prompt,model_answer=model,
            rubric=[dict(criterion=x,marks=3,scoring="0 absent/unsafe; 1 limited relevant point; 2 defensible reasoning with an important omission; 3 coherent contextual reasoning with feasible action and evidence limits.") for x in criteria],human_marking_required=True))
    data.update(curriculum_version="ERT-proposed-eight-course-0.1.0",required_courses=codes,items=items,
        draft_catalogue_complete=True,curriculum_complete=False,remaining_curriculum_titles=[],
        scope_note="All eight planned ERT catalogue courses represented. Seven are review drafts; independent approval, question binding, piloting and verified live ParaLearn support remain pending. Historical five-course blueprint retained separately. This file cannot launch an exam or authorise a certificate.",
        proposed_duration_minutes=210,duration_status="Proposed full-curriculum duration; academic review, accessibility adjustments and learner piloting required")
    return data

if __name__=="__main__":
    data=blueprint();print(validate_blueprint(data))
    (ROOT/"production_courseware/phase_six/ert_batch_02/school_exam_blueprint.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
