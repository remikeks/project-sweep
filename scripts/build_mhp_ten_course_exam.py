"""Ten-course MHP authoring contract; no live assessment or clinical authority."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from schools.exam_blueprints import validate_blueprint


def blueprint():
    codes = [f"SWP-{n:03}" for n in [4, 5, 6, 7, 8, 9, 57, 58, 59, 60]]
    catalogue = json.loads((ROOT / "production_courseware/release-2026-10-03/course_catalogue.json").read_text())
    # Preserve the actual original domains as a review map, not a new protocol.
    retained = [{k: c[k] for k in ["code", "title", "outcome", "modules", "cbt_focus"]}
                for c in catalogue if c["code"] in codes[:6]]
    items = [dict(id=f"MHP10-{code}-MCQ-{n:02}", type="MCQ", marks=1,
                  course_codes=[code], question_binding=None)
             for code in codes for n in range(1, 5)]
    short = [
        (codes[:2],
         "Using a fictional adult who reports work stress and sleep difficulties, explain five features of a collaborative assessment and supervised CBT-informed learning formulation. Do not diagnose or prescribe treatment.",
         "Seek engagement and consent; explore biological, psychological and social concerns alongside strengths; distinguish the person's account from an inference; illustrate links between situation, thoughts, emotions, bodily responses and behaviour without diagnosis; and agree documentation, supervision and review within competence. A worksheet is not a clinical assessment or authority to deliver therapy.",
         ["Engagement and consent (004)", "Whole-person domains and strengths (004)", "Account versus inference and priority needs (004)", "Accurate CBT links without diagnosis (005)", "Collaboration supervision and review within competence (004/005)"]),
        (codes[2:4],
         "A fictional adult in distress reports substance-use concerns. A learner proposes a screening score as a diagnosis and a routine referral without checking the approved escalation route. Give five corrections, using the retained crisis and SBIRT domains without inventing thresholds or a treatment protocol.",
         "Recognise that acute concerns require the qualified local emergency/escalation pathway rather than unsupervised learner triage; use respectful de-escalating communication within role; distinguish consented validated screening from diagnosis; explain screening, brief intervention and matched referral as distinct SBIRT purposes; and use supervised collaborative safety planning, documentation and a warm handover/follow-up under approved local arrangements. Do not invent a cutoff, contact number or substance treatment.",
         ["Qualified local escalation rather than independent triage (006)", "Respectful engagement and boundaries (006)", "Consented validated screening is not diagnosis (007)", "SBIRT sequence and matched referral (007)", "Supervised safety planning documentation and handover (006/007)"]),
        (codes[4:6],
         "A fictional adult is ambivalent about a recovery goal. A worker insists on abstinence, assumes family involvement is wanted and counts a sent referral as recovery. Give five corrections connecting MI with recovery-oriented systems.",
         "Use partnership, compassion and autonomy rather than the righting reflex; demonstrate an appropriate open question and reflective response; explore the person's own change talk and goals without coercion; consider chosen recovery capital, peer and practical supports rather than assume family involvement; and distinguish referral activity from access and person-defined recovery, agreeing continuity and review. No universal outcome or independent treatment authority follows.",
         ["MI spirit autonomy and non-coercion (008)", "Appropriate OARS communication (008)", "Ambivalence and person-defined goals (008/009)", "Chosen recovery capital peer and practical supports (009)", "Continuity and defensible outcome review (009)"]),
        (codes[6:8],
         "A fictional service requires trauma disclosure and family approval before adult access. It claims a Western qualitative review proves every Nigerian adult wants faith-based support. Give five corrections using trauma-informed care and community rights/recovery.",
         "Remove compulsory trauma narration from the introductory exercise and offer choice; explain predictable respectful communication and permission rather than presume trauma; preserve adult participation and supported decisions without a universal legal-capacity ruling; ask about personally meaningful family, faith and peer support rather than assume it; and distinguish conceptual or qualitative evidence from causal treatment effects and Nigerian cultural rules. Verify local law, service capacity and qualified roles.",
         ["Choice and no forced disclosure (057)", "Predictability permission and non-diagnostic support (057)", "Rights participation and supported decisions (058)", "Individual cultural and recovery preferences (057/058)", "Evidence transfer limits and local verification (057/058)"]),
        ([codes[8]],
         "A fictional youth service asks a learner to interview a real child, assumes the accompanying adult is safe and treats assent as legal consent. Give five corrections for an introductory child/adolescent/family learning exercise.",
         "Use only a non-graphic fictional case; consider developmental fit and age-appropriate participation; distinguish assent from legal consent and seek qualified local decisions; assess caregiver involvement through qualified safeguarding rather than assume safety; and coordinate suitable services and transitions with appropriate confidentiality and supervision. Parenting evidence from voluntary adolescent programmes does not establish effectiveness for all children or compulsory safeguarding.",
         ["Fictional exercise and no real child interview", "Developmental fit and child participation", "Assent versus consent and qualified local authority", "Caregiver safety and safeguarding boundaries", "Suitable coordination confidentiality and evidence limits"]),
        ([codes[9]],
         "A fictional adult agrees to a housing referral. The receiving service has not accepted it; a worker sends the whole health record and reports successful recovery. Give five corrections for safe service coordination.",
         "Check the person's goal and purpose-specific permission; verify receiving scope, eligibility, capacity and safe contact; share the minimum authorised information securely rather than a whole record; name a responsible sender and receiver with acceptance and follow-up; and distinguish sending, access and person-defined benefit with a review owner. A scoping map does not prove a universal coordination model or grant clinical authority.",
         ["Person-defined goal and purpose-specific permission", "Verified service fit capacity and safe contact", "Minimum authorised secure information", "Accepted handover named responsibilities and follow-up", "Activity access benefit and evidence limits"]),
    ]
    for n, (coverage, prompt, model, criteria) in enumerate(short, 1):
        items.append(dict(id=f"MHP10-SA-{n:02}", type="SHORT_ANSWER", marks=5,
                          course_codes=coverage, prompt=prompt, model_answer=model,
                          rubric=[dict(criterion=x, marks=1) for x in criteria], human_marking_required=True))
    essays = [
        ("A fictional community centre supports adults with distress, substance-use concerns and housing barriers, and adolescents moving between family and community services. Develop a supervised service-learning proposal across all ten MHP courses. Address whole-person assessment and CBT concepts, approved crisis/SBIRT pathways, MI and recovery supports, cultural choice and rights, child-specific participation and safe coordination. Identify evidence limits, responsibilities and review. Do not create clinical protocols or use personal histories.",
         "Credit a coherent proposal that distinguishes account from formulation, explains CBT links within supervision, uses qualified local crisis routes without invented thresholds, distinguishes screening from diagnosis, applies MI autonomy and chosen recovery capital, avoids forced trauma disclosure and cultural assumptions, supports rights without deciding legal capacity, uses child-specific consent/assent and safeguarding expertise, and closes consented referral loops. Explain evidence transfer and accountable review; educational completion confers no clinical authority."),
        ("Critique a fictional programme that diagnoses from a screening score, assigns therapy to introductory learners, mandates trauma narratives and family/faith involvement, uses real child interviews, sends whole files to unverified services and claims attendance proves recovery. Integrate all ten MHP courses in a justified correction plan, including qualified crisis escalation and human accountability. Explain how you would review service access without collecting personal health records for coursework.",
         "Credit corrections grounded in retained assessment/CBT competence limits, approved crisis escalation and SBIRT purposes; MI partnership and person-defined recovery rather than coercion; trauma-informed choice, cultural humility and community rights; developmentally appropriate child participation with qualified consent/safeguarding decisions; and verified minimum-information handovers. Distinguish attendance, referral, access and outcomes. Use fictional or approved aggregate learning data, acknowledge uncertainty, and assign qualified owners and review rather than claim treatment effectiveness."),
    ]
    criteria = ["Collaborative assessment and supervised CBT reasoning (004/005)",
                "Qualified crisis escalation and SBIRT distinctions (006/007)",
                "MI autonomy recovery capital and continuity (008/009)",
                "Trauma-informed cultural choice and community rights with evidence limits (057/058)",
                "Child participation safeguarding and accountable safe coordination (059/060)"]
    for n, (prompt, model) in enumerate(essays, 1):
        items.append(dict(id=f"MHP10-ESSAY-{n:02}", type="ESSAY", marks=15, course_codes=codes,
                          prompt=prompt, model_answer=model, human_marking_required=True,
                          rubric=[dict(criterion=x, marks=3, scoring="0 absent/unsafe; 1 relevant limited point; 2 defensible reasoning with important omission; 3 coherent contextual reasoning with feasible action and evidence limits.") for x in criteria]))
    return dict(status="draft_for_review", school_code="MHP", curriculum_version="MHP-proposed-ten-course-0.1.0",
                provider="ParaLearn CBT", provider_assessment_id=None, provider_contract_verified=False,
                required_courses=codes, retained_catalogue_domains=retained, programme_target_course_count=10,
                draft_catalogue_complete=True, curriculum_complete=False, remaining_curriculum_titles=[],
                scope_note="Six retained courses and four introductory additions. No original clinical/addiction teaching or CBT mapping changed. Specialist clinical, safeguarding, lived-experience, Nigerian legal/practice, academic and accessibility/pilot reviews pending. No authority to practise clinically or launch an exam.",
                proposed_duration_minutes=210, duration_status="Proposed; academic review, accessibility adjustments and learner piloting required",
                marking_policy=dict(proposed_pass_percent=70, moderation_required=True, ai_only_finalisation=False,
                    rubric_rule="Human criterion-level marking and rationales, independent human moderation and equivalent defensible answers. Refer unsafe reasoning for specialist review; no unapproved automatic fail or professional competency standard is defined.",
                    appeals="Retain original responses, rubric version, marker, moderation decisions, amendments and appeal history with an authorised appeal route."),
                certification=dict(authorised=False, requirements=["Each course badge requires that approved course and its verified ParaLearn course-CBT pass; school certification requires completion of every approved MHP course", "Pass the full-curriculum ParaLearn mixed exam after human written marking and moderation", "Independent curriculum/provider approvals and authorised signatures; Head of Learning details/signature pending; Founder, SWEEP Academy: Prof. Mina Ogbanga"]), items=items)


if __name__ == "__main__":
    data = blueprint()
    print(validate_blueprint(data))
    (ROOT / "production_courseware/phase_nine/mhp_batch_01/school_exam_blueprint.json").write_text(json.dumps(data, indent=2) + "\n")
