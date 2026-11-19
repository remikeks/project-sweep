"""Deterministic original PCEI teaching; checkpoint courses are read-only."""
import importlib.util
from pathlib import Path

def load(name):
    spec=importlib.util.spec_from_file_location('pcei_'+name,Path(__file__).with_name(name+'.py'))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
research=load('research')
REFERENCES=research.REFERENCES
EVIDENCE_CHECKED_ON=research.CHECKED_ON
EVIDENCE_NOTE='Checked 16 November 2026. Standards, publication dates, fieldwork/search dates, rights, access and limitations are separate. IACD standards date to 2018; later training is not a new edition. Registry reference IDs are unresolved. Q1 statements concern indexed SCImago 2025 records with direct-table access limitations; rank is not article validity. Nigerian surveys are contextual, not causal evidence. No source tools or protected exercises copied. Academic, local practice, safeguarding, accessibility/pilot and supervised-skills review pending.'
REVIEW_REQUIREMENTS=dict(local_community_practice='pending',safeguarding='pending',community_and_accessibility_review='pending',supervised_skills_demonstration='pending')
SAFETY='Use only supplied fictional scenarios and invented aggregate data. Do not collect real complainant, child or survivor records or personal histories, or recruit people for fieldwork. You may pause or use an alternative fictional exercise. Record reasoning before checking guide feedback. Practicum is introductory simulated/supervised learning, not completed field placement or independent professional competence.'
def module(title,outcome,paragraphs,example,activity,feedback,sources,rows):
    items=[]
    for point,stem,correct,wrong,rationale in rows:
        items.append((point,stem,correct,wrong,rationale))
    return dict(title=title,outcome=outcome,paragraphs=paragraphs,example='Fictional case: '+example,activity=activity,feedback=feedback,sources=sources,items=items)
def course(n,title,cover,outcome,modules):
    import re
    return dict(code=f'SWP-{n:03}',title=title,slug=re.sub('[^a-z0-9]+','-',title.lower()).strip('-'),cover_title=cover,school_code='PCEI',school_name='School of Community Development and Participatory Engagement',school_display='Community Development and\nParticipatory Engagement',estimated_minutes=180,audience='Introductory community participation, planning and delivery learners. No investigation, legal adjudication, independent safeguarding or professional competence is conferred.',study_guidance=SAFETY+' Proposed study duration is subject to piloting.',practice_safety_note=SAFETY,outcome=outcome,modules=modules)
COURSES=[]
for filename in ['facilitation','assets','accountability','codesign','practicum']:
    COURSES.append(load(filename).build(course,module))
