"""Six original introductory SEE additions; no existing course or CBT changes."""
import importlib.util
from pathlib import Path
import re


def load(name):
    spec = importlib.util.spec_from_file_location('see_' + name, Path(__file__).with_name(name + '.py'))
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj


research = load('research')
REFERENCES = research.REFERENCES
EVIDENCE_CHECKED_ON = '2026-11-27'
EVIDENCE_NOTE = 'Evidence checked 27 November 2026. Publication, issue and data dates differ. Frameworks are curriculum comparators, not Nigerian law, registration or accreditation. Research methods, rights and access limits are recorded. All cases, calculations and exercises are original and fictional. Public assessment drafts are review examples; unpublished production banks and verified ParaLearn configuration are separate launch requirements.'
REVIEW_REQUIREMENTS = dict(owner_material_release_authorised=True, local_legal_tax_finance='requires_qualified_verification', professional_or_investment_authority='not_conferred', paralearn_mixed_exam='unverified')
SAFETY = 'Use supplied fictional enterprises, invented transactions and aggregate cases only. Do not collect personal or business-confidential records, solicit funds, make investments, incur debts or launch a real service through coursework. You may pause or choose another fictional exercise. Real trading, employment, finance, tax and legal decisions require appropriate qualified advice and verified authority.'


def module(title, outcome, paragraphs, example, activity, feedback, sources, rows):
    return dict(title=title, outcome=outcome, paragraphs=paragraphs, example='Fictional case: ' + example, activity=activity, feedback=feedback, sources=sources, items=rows)


def course(number, title, cover, outcome, modules):
    return dict(code=f'SWP-{number:03}', title=title, slug=re.sub('[^a-z0-9]+', '-', title.lower()).strip('-'),
        cover_title=cover, school_code='SEE', school_name='School of Social Entrepreneurship and Enterprise Development',
        school_display='Social Entrepreneurship\nand Enterprise Development', estimated_minutes=180,
        audience='Introductory social-work and community-enterprise learners developing enterprise reasoning under appropriate support.',
        study_guidance=SAFETY + ' Complete each exercise before checking feedback. Study time is proposed for piloting.',
        practice_safety_note=SAFETY, outcome=outcome, modules=modules)


COURSES = [load(name).build(course, module) for name in ['models', 'market', 'finance', 'cooperative', 'impact', 'practicum']]
