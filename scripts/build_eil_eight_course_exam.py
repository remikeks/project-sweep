"""Build the offline EIL mixed-exam blueprint for ParaLearn review."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from schools.exam_blueprints import validate_blueprint

CODES = [f'SWP-{number:03}' for number in range(97, 105)]
BATCH = ROOT / 'production_courseware/phase_sixteen/eil_batch_01'

SHORT = [
    ((0, 1), 'Afirin Ridge moves a road during early works. A gate count covers dry weekdays and excludes vendors travelling on wet-season market days. Give five corrections before the route decision.',
     'Map affected users outside the project boundary. Set a comparable seasonal baseline. Trace the access and earnings pathway. Offer safe participation and show how input will influence the decision. Assign the assessment review and date.',
     ('Affected users', 'Comparable baseline', 'Pathway', 'Practical participation', 'Review authority')),
    ((2,), 'The closure plan offers training to 30 people and forecasts ten jobs. Food sellers are absent from the eligibility list. Give five changes to the transition plan.',
     'Map indirect work and seasonality. Verify demand and timing. Compare alternative support and employment conditions. Check access and practical affordability. Monitor net livelihoods and sustained work against baseline.',
     ('Group and baseline', 'Work feasibility', 'Support comparison', 'Access', 'Sustained recovery')),
    ((3,), 'Residents report a smell and seek health support. Of 20 referrals, 16 are accepted and 12 attend. Give five parts of a safe follow-up.',
     'Separate reported hazard from assessment. Refer timely clinical support and site evidence separately. Explain consent and necessary sharing. Report 80 percent accepted and 60 percent attended among all referred. Verify barriers and a safe follow-up.',
     ('Evidence status', 'Qualified routes', 'Protected information', 'Rates and denominator', 'Continuity check')),
    ((4,), 'A planned fence restricts seasonal use and an operator offers a communal hall. Give five requirements for reviewing the displacement and benefits proposal.',
     'Recognise economic displacement and omitted users. Compare an avoidance option. Separate remedy for eligible harm from the hall benefit. Enable independent support and clarify the decision process. Verify access restoration and actual benefit use.',
     ('Displacement scope', 'Avoidance', 'Separate obligations', 'Fair participation', 'Verified outcomes')),
    ((5,), 'The official desk uses one daytime channel and sends complaints to the manager named in them. A reply says the file is closed because a contractor approved an alternative route. Give five improvements.',
     'Provide equivalent safe routes and confidentiality information. Refer retaliation concerns appropriately and preserve alternatives. Disclose conflicts and provide independent review. Separate approval and implementation. Verify use before closure.',
     ('Safe entry', 'Safeguarding', 'Fair review', 'Process distinctions', 'Remedy verification')),
    ((6, 7), 'An operator announces a committed budget as full service delivery. An Afirin Ridge trial serves eight of ten typical users and zero of two low-access users. Give five entries in a decision memo.',
     'Reconcile commitments against current receipt, service and user evidence. Show both rates and denominators. Keep the failed route visible. Compare revision or pause to the earlier proposal. Set an owner, verification criterion and review date.',
     ('Reconciliation', 'Group denominator', 'Failure evidence', 'Bounded decision', 'Corrective review')),
]
ESSAYS = [
    ('Prepare a phased response to a fictional project winding down at Afirin Ridge. A fence may remove access to seasonal land and a clinic route, informal vendors are excluded from the transition plan, and a complainant fears retaliation. The operator promises a district training hall and cites its well-attended meeting. Use all eight EIL courses and specify what evidence could change the decision.',
     'Map affected groups and project stage. Compare matched access baselines, impact pathways and alternatives. Address paid and informal livelihoods and transition quality. Set protected referral and authorised environmental review. Compare avoidance, restoration and benefits separately. Give a safe grievance route and independent review. Reconcile commitments with delivery. Recommend bounded steps, owners, trigger and retest.'),
    ('Review Afirin Ridge’s statement that the closure transition is fair and complete. It cites a gate traffic count, training certificates, an environmental report from another location, compensation forms, a closed-complaint count and promised funds. A simulated transport trial failed low-access users. Use all eight EIL courses to explain the limits, propose better evidence and defend the next action.',
     'Describe whose participation and stage are visible. Compare route boundaries and outcome evidence. Verify seasonal and sustained livelihoods and reasons for missing coverage. Separate historical or site evidence and clinical support. Review eligible loss, access and benefits. Examine remedy outcomes and protected review. Trace promised funds and actual use. Keep failed trial cases visible and attach a justified corrective decision.'),
]


def rubric(criteria, marks, scoring):
    return [dict(criterion=name, marks=marks, scoring=scoring) for name in criteria]


def blueprint():
    items = [
        dict(id=f'EIL8-{code}-MCQ-{slot:02}', type='MCQ', marks=1, course_codes=[code], question_binding=None)
        for code in CODES for slot in range(1, 6)
    ]
    for number, (coverage, prompt, model, criteria) in enumerate(SHORT, 1):
        items.append(dict(id=f'EIL8-SA-{number:02}', type='SHORT_ANSWER', marks=5,
                          course_codes=[CODES[index] for index in coverage], prompt=prompt,
                          model_answer=model, human_marking_required=True,
                          rubric=rubric(criteria, 1, '0 missing or unsound. 1 accurate reasoning applied to the case.')))
    criteria = [
        'Affected people, project stage, meaningful participation and impact evidence (097 and 098)',
        'Livelihood feasibility, protection and sustained recovery (099)',
        'Bounded health evidence and protected coordination (100)',
        'Displacement, independent review and verified remedy (101 and 102)',
        'Disclosure, actual delivery and a justified decision with review triggers (103 and 104)',
    ]
    scoring = '0 missing or unsafe. 1 limited relevant point. 2 sound reasoning with a gap. 3 coherent applied reasoning with accountable next action.'
    for number, (prompt, model) in enumerate(ESSAYS, 1):
        items.append(dict(id=f'EIL8-ESSAY-{number:02}', type='ESSAY', marks=15, course_codes=CODES,
                          prompt=prompt, model_answer=model, rubric=rubric(criteria, 3, scoring),
                          human_marking_required=True))
    return dict(
        status='draft_for_review', school_code='EIL', curriculum_version='EIL-proposed-eight-course-0.1.0',
        provider='ParaLearn CBT', provider_assessment_id=None, provider_contract_verified=False,
        required_courses=CODES, programme_target_course_count=8, draft_catalogue_complete=True,
        curriculum_complete=False, remaining_curriculum_titles=[], retained_course_domains={},
        scope_note='Five MCQ slots per course. Six short answers collectively cover all eight courses. Both essays integrate all eight.',
        proposed_duration_minutes=210, duration_status='Proposed timing for learner and accessibility piloting.',
        marking_policy=dict(
            proposed_pass_percent=70, moderation_required=True, ai_only_finalisation=False,
            rubric_rule='Record human criterion scores, reasons, rubric version and the independent moderator.',
            appeals='Retain responses, criteria, reasons, moderation and dated appeal and amendment outcomes.',
        ),
        certification=dict(authorised=False, requirements=[
            'Complete every approved course and pass the final verified mixed ParaLearn exam.',
            'Human marking and independent moderation for written responses.',
            'Authorised signatures from the Head of Learning and Founder Prof. Mina Ogbanga.',
        ]),
        items=items,
    )


if __name__ == '__main__':
    data = blueprint()
    print(validate_blueprint(data))
    (BATCH / 'school_exam_blueprint.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
