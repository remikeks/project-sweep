"""Build an offline ParaLearn exam blueprint covering the eight DAI courses."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from schools.exam_blueprints import validate_blueprint

CODES = ['SWP-031', *(f'SWP-{number:03}' for number in range(84, 91))]
BATCH = ROOT / 'production_courseware/phase_fourteen/dai_batch_01'
RETAINED = {
    'title': 'Digital Social Work Practice',
    'modules': [
        'Digital inclusion and service design',
        'Information governance and secure practice',
        'Telepractice, AI, and professional accountability',
    ],
}

SHORT = [
    ([0, 1], 'A fictional referral portal loses applications after a connection drop. Keyboard focus disappears behind a banner. The helpline is unstaffed. Shared phones receive revealing messages. Give five improvements.',
     'Map the point of abandonment and offer recovery. Test focus through completion. Resource a comparable staffed option. Confirm the safe contact channel and use limited wording. Compare attempts, completion and response by channel.',
     ['Journey and access barrier', 'Observable keyboard test', 'Staffed alternative', 'Safe contact', 'Comparable measures']),
    ([2], 'A fictional appointment form requests full case records, requires optional recording and accepts silence. Staff share an account. A case attachment reaches an unintended inbox. Design five corrections.',
     'Minimise fields and define purpose. Offer an accessible distinct recording choice and ordinary service. Record an active decision and withdrawal route. Use individual approved accounts with multifactor authentication. Report minimum incident facts promptly to responsible staff.',
     ['Purpose and necessity', 'Separate accessible choice', 'Active choice and withdrawal', 'Protective account practice', 'Incident escalation']),
    ([3], 'A fictional model supplies a fluent but unsupported date and treats a spelling variation as a risk flag. Reviewers cannot see source evidence or reject outputs. Propose five review controls.',
     'Reconcile dates to authoritative source records. Hold relevant facts constant in a paired comparison. Record scope and severity. Give reviewers evidence and time. Allow rejection, escalation and review of significant decisions.',
     ['Source verification', 'Matched comparison', 'Scope and severity', 'Review resources', 'Authority and escalation']),
    ([4], 'A fictional source says the person asked for a private callback and declined recording. The draft calls this refusal of all help, adds a meeting date and is signed. Explain five corrections.',
     'Preserve attributed account. Restore the actual choice. Remove unsupported date. Track the authorised amendment and responsible reviewer. Review downstream effects and explain the correction route.',
     ['Source attribution', 'Actual recording and call choice', 'Unsupported fact handling', 'Traceable amendment', 'Downstream review']),
    ([5], 'An invented desk closes referrals when sent. An outage leaves two unacknowledged cases. Intake workers can edit signed assessments. Design five workflow improvements.',
     'Define received, accepted and closed states. Assign acknowledgement ownership and deadline. Use a minimum temporary record. Reconcile restored queue and escalate unmatched records. Scope edits to authorised roles with a correction history.',
     ['Case states', 'Handoff owner', 'Continuity route', 'Reconciliation and exception', 'Role and correction history']),
    ([6, 7], 'A fictional launch proposal counts 30 timely responses from 40 attempts, then 48 from 80 with changed staffing. A serious draft error reached a person. Write five elements of a decision.',
     'Report 75 and 60 percent with denominators. Identify concurrent staffing change. Assess the consequential error and approved incident route. Compare revision and staffed alternative using common criteria. Give the decision, owner, stop and retest criteria.',
     ['Correct rates', 'Causal limitation', 'Consequence response', 'Comparable alternatives', 'Reviewable decision']),
]
ESSAYS = [
    ('Design an inclusive paper-based rehearsal of a new referral and documentation workflow. A person uses a borrowed phone, the keyboard route fails, recording is optional, a draft changes a callback into refusal, an outage interrupts a referral and an adoption rate is presented as service evidence. Cover all eight courses and explain who can pause the design.',
     'Apply ethical technology choice and suitable contact from SWP-031. Specify end-to-end keyboard and staffed routes. Define purpose, minimal fields and optional recording. Test unsupported claims and unequal errors with review authority. Reconcile the draft to the source. Assign states, acknowledgement and outage reconciliation. Propose defined rates and monitoring. Give a bounded decision and retest plan.'),
    ('Assess two designs for fictional Northbank: a staffed workflow and a structured queue with optional assisted drafting. Only ordinary cases ran successfully. One example omitted a preference, a reviewer could not amend it, participation was measured in logins, and people who never connected were omitted. Recommend a next step using all eight domains.',
     'Apply digital practice ethics and continuity. Measure entry barriers and test access. Explain data purposes, safe contact and consent. Give reviewers source access, time and power to reject. Preserve voice and trace correction. Assign referral ownership and recovery. Compare rates, errors and burden using defined denominators. Select a justified limited next step with disconfirming tests.'),
]


def rubric(criteria, marks, scoring):
    return [dict(criterion=name, marks=marks, scoring=scoring) for name in criteria]


def blueprint():
    items = []
    for code in CODES:
        for number in range(1, 6):
            items.append(dict(id=f'DAI8-{code}-MCQ-{number:02}', type='MCQ', marks=1,
                              course_codes=[code], question_binding=None))
    for number, (coverage, prompt, model, criteria) in enumerate(SHORT, 1):
        items.append(dict(id=f'DAI8-SA-{number:02}', type='SHORT_ANSWER', marks=5,
                          course_codes=[CODES[index] for index in coverage], prompt=prompt,
                          model_answer=model, human_marking_required=True,
                          rubric=rubric(criteria, 1, '0 missing or unsound. 1 accurate reasoning applied to the case.')))
    criteria = [
        'Ethical digital practice and accessible service routes (031 and 084)',
        'Processing purpose, consent and accountable AI review (085 and 086)',
        'Faithful documentation and traceable workflow (087 and 088)',
        'Comparable measures and evidence limits (089)',
        'Feasible decision, ownership and retest (090)',
    ]
    scoring = '0 missing or unsafe. 1 limited relevant point. 2 sound reasoning with a gap. 3 coherent applied reasoning with responsible action.'
    for number, (prompt, model) in enumerate(ESSAYS, 1):
        items.append(dict(id=f'DAI8-ESSAY-{number:02}', type='ESSAY', marks=15, course_codes=CODES,
                          prompt=prompt, model_answer=model, rubric=rubric(criteria, 3, scoring),
                          human_marking_required=True))
    return dict(
        status='draft_for_review', school_code='DAI', curriculum_version='DAI-proposed-eight-course-0.1.0',
        provider='ParaLearn CBT', provider_assessment_id=None, provider_contract_verified=False,
        required_courses=CODES, programme_target_course_count=8, draft_catalogue_complete=True,
        curriculum_complete=False, remaining_curriculum_titles=[], retained_course_domains={'SWP-031': RETAINED},
        scope_note='Five MCQ slots per course, six short answers covering all eight courses and two integrated essays.',
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
