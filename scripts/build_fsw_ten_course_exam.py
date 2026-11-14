"""Compile the proposed ten-course exam authoring map; no provider calls."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from schools.exam_blueprints import validate_blueprint


def blueprint():
    codes=[f"SWP-{n:03}" for n in [16,17,18,35,36,37,38,39,40,41]]
    items=[dict(id=f"FSW-{code}-MCQ-{n:02}",type="MCQ",marks=1,course_codes=[code],question_binding=None)
        for code in codes for n in range(1,5)]
    short=[
        (codes[:3],"A fictional hospital discharge plan includes ongoing support needs and input from several professions. Identify five checks that make the transition reviewable without promising clinical decisions outside the social worker's role.",
         ["Clarify the person's priorities and understanding of the discharge arrangements.","Confirm relevant support needs and the appropriate professional's responsibility for clinical advice.","Check a feasible next service or support contact and any access barrier.","Identify a named coordination role and authorised handover route.","Agree a follow-up point and how unresolved concerns will be escalated."],
         ["Person's participation","Role and scope","Access and continuity","Accountable handover","Follow-up and escalation"]),
        (["SWP-037"],"A 19-year-old learner misses training while combining caring responsibilities with irregular transport. Give a contextual explanation and a next step, distinguishing facts from a hypothesis.",
         ["Start with the learner's account and goal.","Connect relevant developmental domains without diagnosing from age or attendance.","Identify how caring, training and transport arrangements may interact.","Mark an unverified explanation as a hypothesis and state a check.","Agree a feasible support action and review point."],
         ["Person's account","Development without diagnosis","Interacting context","Uncertainty and verification","Collaborative next step"]),
        (["SWP-038"],"A relative answers every interview question while the person remains quiet. Describe five communication actions that support participation without assuming what the silence means.",
         ["Explain roles and the purpose of the conversation.","Ask the person about communication and participation preferences.","Use an accessible open question and allow time to respond.","Clarify understanding and avoid interpreting silence as agreement.","Check any need for a separate conversation or authorised support without promising absolute confidentiality."],
         ["Roles and purpose","Preferences and access","Listening and questioning","Understanding without assumption","Appropriate follow-up"]),
        (["SWP-039"],"A partner service requests an entire file for a specific transport-support decision. Describe five checks before sharing, including the distinction between consent and other authority questions.",
         ["Clarify purpose, intended recipient and the relevant information.","Check the organisation's authorised lawful-basis assessment and applicable conditions with data-protection advice where needed.","Check the person's understanding and the scope of consent where consent is relied upon.","Use minimum relevant information and an authorised secure route.","Record the reasoned decision, uncertainty and any further advice needed."],
         ["Defined purpose","Applicable authority and advice","Consent scope and understanding","Proportionate secure handling","Accountable decision record"]),
        (["SWP-040"],"An old directory entry produces a referral that is acknowledged but not accepted. Describe five network actions that clarify the pathway and prevent an unsupported claim of successful access.",
         ["Verify eligibility, access and capacity with a current contact.","Separate referral sent, receipt, acceptance and service reached.","Agree the decision owner and the person's next contact.","Use an agreed response date and fallback or escalation route.","Assign the directory correction and review the pathway with relevant feedback."],
         ["Current verification","Accurate stage definitions","Explicit ownership","Follow-up and fallback","Shared improvement"]),
        (["SWP-041"],"A worker feels more confident after a reflective group but faces an unresolved boundary concern. Describe five steps that connect reflection to authorised supervision and a reviewable learning action.",
         ["Describe the event separately from interpretation and consider alternative explanations.","Identify the boundary, policy or conflict question.","Seek an authorised supervisor's advice and check decision authority.","Use the relevant escalation route if a serious concern remains unresolved.","Agree a specific action and review evidence; confidence alone does not establish competence or effectiveness."],
         ["Structured reflection","Boundary question","Authorised supervision","Escalation","Evidence-aware learning plan"]),
    ]
    for n,(coverage,prompt,model,criteria) in enumerate(short,1):
        items.append(dict(id=f"FSW-SA-{n:02}",type="SHORT_ANSWER",marks=5,course_codes=coverage,prompt=prompt,
            model_answer=" ".join(model),rubric=[dict(criterion=x,marks=1) for x in criteria],human_marking_required=True))
    essays=[
        (["SWP-035","SWP-036","SWP-037","SWP-038","SWP-039"],
         "Using a fictional adult seeking support with training while caring for a relative, develop a generalist assessment and support plan. Explain ethical reasoning, contextual influences, an accessible interview, information-use decisions and how uncertainty will be reviewed. Do not invent clinical findings or legal authority.",
         "An acceptable answer keeps the person's goals and rights visible; distinguishes evidence from hypotheses; considers strengths and interacting barriers; explains accessible participation; identifies a justified information-use purpose and the authority/advice needed; and gives actions, owners and review points. Equivalent defensible alternatives earn marks. Unsupported diagnostic or legal claims do not earn the relevant criterion marks.",
         ["Ethical reasoning and participation","Contextual assessment and uncertainty","Accessible communication","Purposeful lawful information handling and consultation","Action ownership and review"]),
        (["SWP-016","SWP-017","SWP-018","SWP-040","SWP-041"],
         "A fictional person leaving hospital needs ongoing support and a cross-sector referral. The receiving service has changed eligibility and has not accepted the referral. Propose an accountable transition and network response, respecting clinical scope, continuity and the person's preferences. Explain how reflection, supervision and pathway feedback would inform improvement without claiming causation from referral counts.",
         "An acceptable answer distinguishes social support from clinical decisions; preserves participation and continuity; identifies professional contributions and a named coordinating role; verifies the cross-sector pathway, handover status and fallback; and uses reflection and authorised supervision with a bounded improvement and honest evidence limits. It does not treat a sent referral as access, a peer group as automatic formal supervision, or a higher count as causal proof.",
         ["Person-centred transition and appropriate clinical scope","Continuity and support needs","Interprofessional roles and communication","Verified network handover and fallback","Reflective supervised improvement and evidence limits"]),
    ]
    for n,(coverage,prompt,model,criteria) in enumerate(essays,1):
        items.append(dict(id=f"FSW-ESSAY-{n:02}",type="ESSAY",marks=15,course_codes=coverage,prompt=prompt,
            model_answer=model,rubric=[dict(criterion=x,marks=3,scoring="0 absent/unsafe; 1 limited relevant point; 2 defensible reasoning with an important omission; 3 coherent, contextual reasoning with action and limits.") for x in criteria],human_marking_required=True))
    return dict(status="draft_for_review",school_code="FSW",curriculum_version="FSW-proposed-ten-course-0.1.0",
        provider="ParaLearn CBT",provider_assessment_id=None,provider_contract_verified=False,required_courses=codes,
        proposed_duration_minutes=180,duration_status="Proposal requiring accessible learner piloting and academic review",
        marking_policy=dict(proposed_pass_percent=70,moderation_required=True,ai_only_finalisation=False,
            rubric_rule="Accept equivalent defensible reasoning and contextually justified alternatives. Award criterion marks, record written-score rationale and moderate before finalisation.",
            appeals="Preserve original responses, rubric version, marker, moderation decision and amendment history with an authorised appeal route."),
        certification=dict(authorised=False,requirements=["Every approved curriculum course passed through verified ParaLearn CBT","Final school exam passed after human marking and moderation","Head of Learning name and authorised signatures supplied","Founder signature authorised: Prof. Mina Ogbanga"]),items=items)


if __name__=="__main__":
    data=blueprint()
    print(validate_blueprint(data))
    (ROOT/"production_courseware/phase_four/fsw_batch_02/school_exam_blueprint.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
