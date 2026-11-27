"""Build an offline ParaLearn exam blueprint covering the six BLU courses."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from schools.exam_blueprints import validate_blueprint

CODES = [f'SWP-{number:03}' for number in range(91, 97)]
BATCH = ROOT / 'production_courseware/phase_fifteen/blu_batch_01'

SHORT = [
    ([0], 'A seawall and walkway proposal counts boat sales only and closes the morning walking route. A group claims it owns the shore. Give five corrections before recommending an option.',
     'Map owners, crew, processors and household uses. Trace closure effects on work and food. Identify ecological dependencies. Compare feasible access options. Record reported rights and refer unresolved authority questions.',
     ['Livelihood map', 'Access effects', 'Ecological dependence', 'Options comparison', 'Authority and evidence']),
    ([1], 'A fictional grant serves 12 of 18 applicants from 30 eligible workers. A named crew member reports delayed payment. Explain how to measure protection and handle the concern.',
     'Calculate 40 percent of eligible workers and about 67 percent of applicants. Explore barriers before application. Record a safe support request. Use authorised labour referral. Track receipt and the outcome.',
     ['Rates and denominator', 'Missing applicants', 'Confidential response', 'Appropriate referral', 'Service follow-up']),
    ([2], 'Flooding closes the route and power fails. An SMS reaches ten workers and only six of 20 can act. A drainage proposal pushes water toward homes. Give five review steps.',
     'Identify hazard and exposed work. Explain a cascade through preservation and sales. Add an accessible alert and assisted route. Compare delivery, understanding and action. Seek qualified assessment of displaced risk and set a review trigger.',
     ['Risk components', 'Cascade', 'Accessible response', 'Staged drill measures', 'Transferred risk and review']),
    ([3], 'A proposed marine zone omits seasonal shore use. Its meeting is inaccessible and a proposed replacement path has been counted as a completed remedy. Give five corrections.',
     'Recognise the omitted use and verify claims. State open choices and responsible authority. Provide accessible participation. Record responses and an impartial review route. Verify practical remedy delivery at the relevant time.',
     ['Recognised uses', 'Scope and authority', 'Procedural access', 'Feedback and grievance', 'Delivered remedy']),
    ([4], 'A grant covers a cold room but leaves eight running-cost units unfunded. The promoter calls every available slot a community benefit and claims net environmental gain without energy or nearby-site evidence. Give five corrections.',
     'Separate capital and recurring commitments. Verify the operating owner and timing. Distinguish offered, booked and used slots. Check access and distribution. Require baseline, energy and displaced-activity evidence.',
     ['Funding gap', 'Owner and timing', 'Benefits pathway', 'Distribution', 'Environmental evidence']),
    ([5], 'An Oru Reach pilot serves eight of ten ordinary cases and misses every low-cost user who was tested. A sponsor asks for expansion. Write five parts of the decision memo.',
     'State a bounded revision or pause. Identify the group and denominator. Preserve access failure and compare the fallback. Set an owner and retest condition. Keep decisions, scope and next review date traceable.',
     ['Decision', 'Comparable measures', 'Adverse result and alternative', 'Owner and retest', 'Evidence record']),
]
ESSAYS = [
    ('Design a phased fictional coastal livelihoods response. Flooding closes a landing route, workers outside the owner register miss support and a cold-room plan charges unaffordable fees. A nearby conservation zone affects shore harvesters. Use all six courses to compare alternatives and identify who can make the next decision.',
     'Map activities and dependencies. Track labour and protection access with defined denominators. Connect coastal risk and continuity and test displaced burdens. Recognise shore rights and accessible participation and remedy. Verify recurring costs and effective benefits. Present a conditional choice, staffed fallback, evidence tests and accountable review.'),
    ('Critique a claim that new shoreline investments prove sustainable and equitable development. Boat sales rose, warnings were sent, a site was designated, money was committed and ten ordinary demonstrations worked. Use all six BLU domains to explain what to measure and when to revise or pause.',
     'Distinguish earnings, food, work and which groups benefit. Compare effective labour and protection access. Follow alerts to achievable action and examine transferred risk. Test conservation outcomes and fair governance. Separate commitment, recurring funding and delivered benefits. Identify exceptions, decision roles and retest conditions.'),
]


def rubric(criteria, marks, scoring):
    return [dict(criterion=name, marks=marks, scoring=scoring) for name in criteria]


def blueprint():
    items = []
    for code, slots in zip(CODES, (7, 7, 7, 7, 6, 6), strict=True):
        for number in range(1, slots + 1):
            items.append(dict(id=f'BLU6-{code}-MCQ-{number:02}', type='MCQ', marks=1,
                              course_codes=[code], question_binding=None))
    for number, (coverage, prompt, model, criteria) in enumerate(SHORT, 1):
        items.append(dict(id=f'BLU6-SA-{number:02}', type='SHORT_ANSWER', marks=5,
                          course_codes=[CODES[index] for index in coverage], prompt=prompt,
                          model_answer=model, human_marking_required=True,
                          rubric=rubric(criteria, 1, '0 missing or unsound. 1 accurate reasoning applied to the case.')))
    criteria = [
        'Coastal livelihoods, work and effective protection (091 and 092)',
        'Compound risk, warning access and displaced burden (093)',
        'Equity, participation and grievance follow-up (094)',
        'Finance feasibility and actual community benefit (095)',
        'Justified option, accountability and review conditions (096)',
    ]
    scoring = '0 missing or unsafe. 1 limited relevant point. 2 sound reasoning with a gap. 3 coherent applied reasoning with responsible action.'
    for number, (prompt, model) in enumerate(ESSAYS, 1):
        items.append(dict(id=f'BLU6-ESSAY-{number:02}', type='ESSAY', marks=15, course_codes=CODES,
                          prompt=prompt, model_answer=model, rubric=rubric(criteria, 3, scoring),
                          human_marking_required=True))
    return dict(
        status='draft_for_review', school_code='BLU', curriculum_version='BLU-proposed-six-course-0.1.0',
        provider='ParaLearn CBT', provider_assessment_id=None, provider_contract_verified=False,
        required_courses=CODES, programme_target_course_count=6, draft_catalogue_complete=True,
        curriculum_complete=False, remaining_curriculum_titles=[], retained_course_domains={},
        scope_note='Forty MCQ slots distributed 7, 7, 7, 7, 6 and 6. Each short answer covers one course and both essays integrate all six.',
        proposed_duration_minutes=210, duration_status='Proposed duration for learner and accessibility piloting.',
        marking_policy=dict(
            proposed_pass_percent=70, moderation_required=True, ai_only_finalisation=False,
            rubric_rule='Record human criterion scores and reasons, rubric version and independent named moderator.',
            appeals='Retain the response, criteria, reasons, moderation and dated appeal and amendment outcomes.',
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
