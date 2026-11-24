"""Original CPS additions; retained courses and CBTs are read-only."""
import importlib.util
from pathlib import Path
import re


def load(name):
    spec = importlib.util.spec_from_file_location('cps_' + name, Path(__file__).with_name(name + '.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


research = load('research')
REFERENCES = research.REFERENCES
EVIDENCE_CHECKED_ON = '2026-11-24'
EVIDENCE_NOTE = 'Evidence appraised 24 November 2026. Standards, publication dates, search periods and fieldwork dates are distinguished. Research supports bounded learning, not proof of local programme effects or professional competence. Some full downloads were unavailable; access limitations are recorded per source. Original fictional cases and factual commentary only: no source manuals, instruments or raw papers reproduced. Owner authorises learning-material release after a verified build; ParaLearn assessment verification, field competence, local operating protocols and certificate signatures remain separate.'
REVIEW_REQUIREMENTS = dict(owner_material_release_authorised=True, local_operating_protocol='requires_authorised_context', supervised_professional_competence='not_conferred', paralearn_mixed_exam='unverified')
SAFETY = 'Use only the supplied fictional cases and invented aggregate information. Do not contact children or families, collect personal histories, submit real case files, investigate allegations or recruit people for fieldwork. You may pause or choose an alternative fictional exercise. This introductory course does not authorise independent child-protection casework, clinical treatment, statutory decisions or emergency deployment. Use designated qualified safeguarding arrangements for actual concerns.'


def module(title, outcome, paragraphs, example, activity, feedback, sources, rows):
    return dict(title=title, outcome=outcome, paragraphs=paragraphs, example='Fictional case: ' + example,
                activity=activity, feedback=feedback, sources=sources, items=rows)


def course(number, title, cover, outcome, modules):
    return dict(code=f'SWP-{number:03}', title=title, slug=re.sub('[^a-z0-9]+', '-', title.lower()).strip('-'),
                cover_title=cover, school_code='CPS', school_name='School of Child Protection and Safeguarding',
                school_display='Child Protection\nand Safeguarding', estimated_minutes=180,
                audience='Introductory social-work and safeguarding learners preparing to recognise boundaries, analyse fictional plans and work under appropriate supervision. No statutory, investigation or clinical authority is conferred.',
                study_guidance=SAFETY + ' Work through each case before reading feedback. Study time is a proposal for piloting.',
                practice_safety_note=SAFETY, outcome=outcome, modules=modules)


COURSES = [load(name).build(course, module) for name in ['participation', 'case_information', 'organisations', 'prevention', 'emergencies']]
