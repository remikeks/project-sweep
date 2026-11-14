"""Export an authored, reproducible draft batch and internal school exam blueprint."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from courses.authored_review import digest, validate_package
from schools.exam_blueprints import validate_blueprint

OUT = ROOT / "production_courseware/phase_two/fsw_batch_01"
spec = importlib.util.spec_from_file_location("fsw_authoring", OUT / "authoring.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
package = dict(version="0.1.0", status="draft_for_review", evidence_checked_on="2026-11-14",
               review=dict(subject_matter="pending", Nigerian_practice_and_legal="pending", accessibility_and_pilot="pending", publication="not_approved"),
               references=source.REFERENCES, courses=[])
for authored in source.COURSES:
    course = {k:v for k,v in authored.items() if k != "modules"}
    course["modules"] = [{"order":i, **{k:v for k,v in module.items() if k != "items"}} for i,module in enumerate(authored["modules"], 1)]
    bank = dict(status="draft_for_review", assessment_id=None, version="0.1.0", course_code=course["code"],
                course_slug=course["slug"], title=course["title"], proposed_pass_percent=70, minimum_correct=11,
                source_hash_encoding="canonical-json-sorted-keys-utf8", authoring_source_sha256=digest(course),
                catalogue_sha256=digest(dict(code=course["code"], title=course["title"], slug=course["slug"], modules=course["modules"])), modules=[], questions=[])
    for order,module in enumerate(authored["modules"], 1):
        points = []
        for n,(point,stem,correct,distractors,rationale) in enumerate(module["items"], 1):
            pid = f"{course['code']}-M{order}-T{n}"
            points.append(dict(id=pid,text=point))
            options = [dict(text=d,correct=False) for d in distractors]
            options.insert((order + n) % 4, dict(text=correct,correct=True))
            bank["questions"].append(dict(id=f"{course['code']}-Q{len(bank['questions'])+1:02}", type="MCQ", marks=1,
                module_order=order, teaching_point_id=pid, question=stem, options=options, rationale=rationale))
        bank["modules"].append(dict(order=order,title=module["title"], outcome=module["outcome"],teaching_points=points))
    course["assessment"] = bank
    package["courses"].append(course)

required = ["SWP-016","SWP-017","SWP-018","SWP-035","SWP-036"]
blueprint = dict(status="draft_for_review", school_code="FSW", curriculum_version="FSW-proposed-five-course-0.1.0",
    provider="ParaLearn CBT", provider_assessment_id=None, provider_contract_verified=False,
    required_courses=required, proposed_duration_minutes=150,
    marking_policy=dict(proposed_pass_percent=70, moderation_required=True, ai_only_finalisation=False,
        rubric_rule="Award criterion marks for equivalent defensible reasoning; accept contextually justified alternatives. Do not award unsupported clinical or legal claims. Record a rationale for each written score.",
        appeals="Retain original response, rubric version, marker, moderation decision and amendment history; provide an authorised appeal route."),
    items=[])
for code in required:
    for n in range(8):
        blueprint["items"].append(dict(id=f"FSW-{code}-MCQ-{n+1:02}",type="MCQ",marks=1,course_codes=[code],question_binding=None))
written = [
    ("SHORT_ANSWER",["SWP-016"],"A person is due to leave hospital but reports an unresolved housing barrier. Identify two matters to verify, the appropriate team consultation and a documented next step.",
     "Check the person's account and current housing or support situation; involve the appropriate discharge team and social support role; agree and document responsibility and follow-up without making a unilateral clinical discharge decision.",
     [("Two relevant checks with the person's participation",2),("Appropriate interdisciplinary consultation within role",1),("Agreed action owner and follow-up",2)]),
    ("SHORT_ANSWER",["SWP-017"],"A person misses a chronic-care appointment because of work hours and transport cost. Explain a respectful assessment and two collaborative support actions.",
     "Explore the person's priorities and reported barriers without assigning blame; check feasible appointment or transport options with the relevant service; agree who will follow up. Do not alter clinical treatment independently.",
     [("Non-judgemental exploration and participation",2),("Two feasible support actions within role",2),("Follow-up responsibility",1)]),
    ("SHORT_ANSWER",["SWP-018"],"Two services each assume the other will contact a family. Describe how to resolve the responsibility gap and record the handover.",
     "Clarify the outstanding need with the person and services; name the responsible role, obtain acceptance and set the contact and review arrangements; record information-sharing authority and outstanding risk as relevant.",
     [("Identify the responsibility gap and relevant need",1),("Explicit agreed responsibility and acceptance",2),("Clear documented contact and review arrangements",2)]),
    ("SHORT_ANSWER",["SWP-035"],"A partner asks for a whole case file for a narrow support decision. Give a reasoned response addressing purpose, authority, participation and proportionality.",
     "Clarify the request and authority, involve the person where appropriate, consider a relevant limited summary, consult on uncertainty and use the approved secure route. A professional request alone does not justify disclosure.",
     [("Purpose and authority checked",2),("Participation and proportionate information",2),("Consultation or secure route",1)]),
    ("SHORT_ANSWER",["SWP-036"],"A referral was sent but no response is recorded. Distinguish activity from outcome and propose a closed-loop review.",
     "Sending is activity rather than evidence of access or benefit. Check receipt and the agreed next step with the person and receiving service, identify barriers, assign responsibility and update the plan.",
     [("Accurate activity and outcome distinction",2),("Appropriate follow-through checks",2),("Owner or plan update",1)]),
    ("SHORT_ANSWER",["SWP-035","SWP-036"],"A learner claims a desk-review paper proves a local agency caused a client's exclusion. Explain the evidence limitation and a defensible assessment response.",
     "A secondary conceptual analysis does not establish the facts or causation in a particular case. Document the person's account, verify the local process and relevant evidence, and use appropriate accountability or supervision routes.",
     [("Research limitation explained",2),("Local evidence and person-centred assessment",2),("Appropriate accountability route",1)]),
    ("ESSAY",required,"Fictional case: an adult preparing for discharge has a long-term condition, transport barriers and an unclear referral handover. The person wants to participate in decisions. Develop a coordinated support plan, explain an information-sharing dilemma, and show how you would review access and outcomes. Identify the limits of your role.",
     "A defensible answer connects the person's priorities and discharge context to assessment, chronic-care support barriers, team responsibilities, proportionate information sharing and a measurable review plan. It identifies clinical decisions outside role, uncertainties and escalation or supervision needs. Alternative safe, justified plans may earn marks.",
     [("Discharge context and person-centred assessment",3),("Practical chronic-care support within role",3),("Interdisciplinary responsibilities and handover",3),("Ethical reasoning and information sharing",3),("Measurable coordination and review",3)]),
    ("ESSAY",required,"A team reports repeated unsuccessful referrals after discharge for adults with chronic conditions. Design a reflective service-improvement response that examines access barriers and responsibilities while protecting confidentiality. Explain what evidence can and cannot show and how individual plans would remain supported.",
     "Use anonymised patterns alongside individual follow-up, distinguish referral activity from outcomes, clarify team roles and service capacity, include service-user participation, establish review measures and owners, and avoid causal or misconduct claims unsupported by local evidence. Include support for staff and organisational review rather than attributing every failure to individuals.",
     [("Discharge and chronic-care continuity considered",3),("Access assessment and service-user participation",3),("Team accountability and individual follow-through",3),("Confidentiality and ethical or evidence reasoning",3),("Feasible review measures and organisational action",3)]),
]
for n,(kind,codes,prompt,answer,rubric) in enumerate(written,1):
    blueprint["items"].append(dict(id=f"FSW-WRITTEN-{n:02}",type=kind,marks=5 if kind=="SHORT_ANSWER" else 15,
        course_codes=codes,prompt=prompt,model_answer=answer,rubric=[dict(criterion=c,marks=m) for c,m in rubric],human_marking_required=True))

summary = validate_package(package)
exam_summary = validate_blueprint(blueprint)
OUT.mkdir(parents=True,exist_ok=True)
for name,data in [("review_package.json",package),("school_exam_blueprint.json",blueprint),
                  ("validation.json",dict(teaching=summary,school_exam=exam_summary,package_sha256=digest(package),school_exam_sha256=digest(blueprint)))]:
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary),json.dumps(exam_summary))
