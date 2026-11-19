"""Full PCEI internal review blueprint; no live question bindings or credentials."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from schools.exam_blueprints import validate_blueprint
CODES=['SWP-013','SWP-014','SWP-015',*[f'SWP-{n:03}' for n in range(61,66)]]

def blueprint():
    # Retained domains come from actual catalogue text, not invented protocols.
    catalogue=json.loads((ROOT/'production_courseware/release-2026-10-03/course_catalogue.json').read_text())
    rows=catalogue['courses'] if isinstance(catalogue,dict) else catalogue
    retained={r['code']:{k:r[k] for k in ('title','outcome','modules','cbt_focus')} for r in rows if r['code'] in CODES[:3]}
    items=[dict(id=f'PCEI8-{code}-MCQ-{n:02}',type='MCQ',marks=1,course_codes=[code],question_binding=None) for code in CODES for n in range(1,6)]
    short=[
      (CODES[:2],
       'A fictional needs assessment uses only coalition leaders\' views and announces the result as the whole community\'s priority. Give five corrections addressing assessment and organising.',
       'Clarify the assessment purpose and inclusion/ethics; identify absent perspectives and suitable participatory methods without unsafe recruitment; consider assets alongside needs; validate and prioritise findings with an honest account of uncertainty; and explain coalition roles, power and communication so leaders do not stand for everyone. Do not invent a retained-course protocol.',
       ['Assessment purpose and ethics (013)','Missing perspectives and suitable participatory methods (013)','Assets alongside needs (013)','Validation and transparent prioritisation (013)','Coalition power roles and communication (014)']),
      ([CODES[2],CODES[7]],
       'A fictional programme holds two sessions, records eighteen attendances and claims proven community improvement. Its rehearsal portfolio is described as a completed professional placement. Give five corrections.',
       'State a plausible needs-goals/theory-of-change link; distinguish activities/outputs from outcomes and appropriate indicators; identify baseline, missing data and alternative explanations without claiming causal proof; assign feasible implementation resources, roles and follow-up; and label rehearsal as introductory simulated learning, not a completed placement or independent competence.',
       ['Needs goals and theory of change (015)','Outputs outcomes and indicators (015)','Baseline missingness and evidence limits (015)','Feasible implementation responsibilities (015/065)','Simulation and supervised competence boundary (065)']),
      ([CODES[3]],
       'A fictional dialogue has a fixed budget, uses one app, and treats silence as consent. Give five improvements.',
       'Explain fixed and open decisions and authority; check missing perspectives; provide feasible accessible participation alternatives; preserve disagreement without treating silence as consent; and give a feedback owner, reasoned decision status and next review point.',
       ['Honest decision scope','Missing perspectives','Accessible alternatives','Disagreement and no inferred consent','Feedback responsibility and status']),
      ([CODES[4]],
       'A fictional asset map lists a hall and skilled residents. The organiser assumes all access is free, asks for unpaid labour before funding is decided and claims the map proves benefit. Give five corrections.',
       'Check access and control rather than existence alone; obtain voluntary bounded contributions; disclose costs, burdens and funding uncertainty; retain unmet needs and external responsibilities; and distinguish resource counts from outcomes, using the Newham and Tanzania evidence only within their contextual and methodological limits.',
       ['Access versus existence','Voluntary bounded contribution','Burdens and uncertain funding','Needs and institutional responsibilities','Outcome and evidence limits']),
      ([CODES[5]],
       'A fictional complaint box has no owner; its decision-maker reviews their own disputed decision, serious concerns wait in the routine queue, and a fall in complaints is called proof of safety. Give five corrections.',
       'Provide accessible bounded entry and a response owner; address conflicts through an authorised impartial route; use designated qualified safeguarding/emergency arrangements where applicable; minimise information with realistic confidentiality/non-retaliation arrangements and review options; and interpret counts cautiously because access and recording can change. Facilitation is not investigation or adjudication.',
       ['Accessible scope and owner','Impartial authorised review','Qualified safeguarding and scope','Proportionate information and response review','Counts and alternative explanations']),
      ([CODES[6]],
       'A fictional plan is called co-designed although only its poster colour can change. A cheap venue excludes some users; three classmates praise the prototype. Give five corrections.',
       'Match the label to meaningful decision influence; expose constraints and authority; compare options on access, resources and unequal burdens; describe the review as simulated rather than representative consultation; and retain versioned reasons, owners and unresolved approvals without claiming outcome proof.',
       ['Meaningful influence','Constraints and authority','Inclusive feasible trade-offs','Simulation and prototype evidence limits','Revision history and approval status']),
    ]
    for n,(coverage,prompt,model,criteria) in enumerate(short,1):
        items.append(dict(id=f'PCEI8-SA-{n:02}',type='SHORT_ANSWER',marks=5,course_codes=coverage,prompt=prompt,model_answer=model,rubric=[dict(criterion=x,marks=1,scoring='0 absent/unsafe/unsupported; 1 accurate relevant reasoning applied to the fictional case. Accept equivalent defensible reasoning.') for x in criteria],human_marking_required=True))
    essays=[
     ('Develop a conditional plan for a fictional community learning programme. A needs exercise hears only association leaders; the coalition disagrees on priorities; the hall has an access fee; unpaid work is requested before funding; a complaint route has no response owner; and delivery has not been approved. Integrate all eight PCEI courses. Explain evidence, participation, assets, accountability, inclusive options, implementation, review and boundaries.',
      'A coherent answer uses participatory assessment with assets/needs and validated priorities; examines coalition power, roles and communication; states a feasible theory of change and output/outcome indicators without causal overclaim; bounds dialogue influence and provides access/feedback; checks voluntary asset contributions and uncertainty; assigns impartial complaint handling with qualified safeguarding routes; compares inclusive options and records revisions; and sets conditional task owners, dependencies, simulation status and supervised-learning limits. Include appropriate authority, privacy and missing perspectives rather than collect real sensitive accounts.'),
     ('Critique a fictional programme that claims success from attendance, an asset list, fewer complaints and a praised prototype. Its coalition calls silence unanimous consent; one channel is app-only; it promises a completed field placement and certification after an offline quiz. Propose justified corrections across all eight PCEI courses and explain what evidence and approvals remain missing.',
      'A strong critique distinguishes assessment evidence and missing perspectives, coalition authority and consent, programme outputs and outcomes, dialogue access and disagreement, asset control and contribution burdens, grievance access/recording and qualified scope, prototype usability versus effects, and introductory rehearsal versus real delivery/competence. It sets feasible owners and feedback/revision points without assuming causal benefit. It rejects real sensitive coursework, unapproved recruitment, invented approvals and offline certification; approved courses, verified ParaLearn passes, full mixed exam, human written marking, independent moderation and authorised signatures remain separate gates.'),
    ]
    criteria=[('Participatory assessment and coalition power/roles (013/014)',3),('Programme logic indicators feasible resources and evidence limits (015)',3),('Dialogue influence and asset access/contribution burdens (061/062)',3),('Accountability scope and inclusive planning/revision (063/064)',3),('Implementation dependencies supervised-learning boundary and coherent review (065)',3)]
    for n,(prompt,model) in enumerate(essays,1):
        items.append(dict(id=f'PCEI8-ESSAY-{n:02}',type='ESSAY',marks=15,course_codes=CODES,prompt=prompt,model_answer=model,human_marking_required=True,rubric=[dict(criterion=x,marks=w,scoring='0 absent/unsafe; 1 relevant limited point; 2 defensible applied reasoning with an important gap; 3 coherent contextual reasoning with feasible action, authority and evidence limits. Accept equivalent defensible reasoning.') for x,w in criteria]))
    return dict(status='draft_for_review',school_code='PCEI',curriculum_version='PCEI-proposed-eight-course-0.1.0',provider='ParaLearn CBT',provider_assessment_id=None,provider_contract_verified=False,required_courses=CODES,programme_target_course_count=8,draft_catalogue_complete=True,curriculum_complete=False,remaining_curriculum_titles=[],retained_course_domains=retained,scope_note='Full eight-title internal draft map, not an approved professional curriculum. Original 013-015 domains read from retained catalogue. Academic, local community practice, safeguarding, accessibility/pilot and supervised-skills review pending. Provider mixed-item support and bindings unverified; no live exam or certification authorised.',proposed_duration_minutes=210,duration_status='Proposed; academic/accessibility review and learner piloting pending',marking_policy=dict(proposed_pass_percent=70,moderation_required=True,ai_only_finalisation=False,rubric_rule='Human criterion-level scores and rationales; independently identified human moderator checks written marking and amendments. Preserve response, rubric version, marker, moderator and amendment/appeal history. Equivalent defensible reasoning accepted; no unapproved automatic professional-competence or fail standard.',appeals='Authorised review route with original response, criterion marks, reasons, moderation, dated amendments and appeal outcome retained.'),certification=dict(authorised=False,requirements=['Course badge: approved course plus verified ParaLearn course CBT pass','Certificate: complete all approved school courses and pass the final mixed ParaLearn exam after human written marking and independent human moderation','Authorised signatures required; Head of Learning name/signature pending; Founder Prof. Mina Ogbanga']),items=items)

if __name__=='__main__':
    data=blueprint();print(validate_blueprint(data))
    (ROOT/'production_courseware/phase_ten/pcei_batch_01/school_exam_blueprint.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
