"""Original SPG learning additions; retained SWP-028 and its CBT are read-only."""
import importlib.util
from pathlib import Path
import re


def load(name):
    spec = importlib.util.spec_from_file_location('spg_' + name, Path(__file__).with_name(name + '.py'))
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj


research = load('research')
REFERENCES = research.REFERENCES
EVIDENCE_CHECKED_ON = '2026-11-25'
EVIDENCE_NOTE = 'Evidence checked 25 November 2026. Report years, publication dates and data periods differ. Practice guidance is a comparator, not Nigerian law or accreditation. Research designs, outcome limits, rights and access restrictions are recorded per source. Original fictional examples only; no protected source tools or raw papers reproduced. Owner authorises learning-material release after a verified build; provider configuration, professional authority and certificate signatures are separate requirements.'
REVIEW_REQUIREMENTS = dict(owner_material_release_authorised=True, local_operating_authority='requires_contextual_verification', professional_audit_or_policy_authority='not_conferred', paralearn_mixed_exam='unverified')
SAFETY = 'Use supplied fictional budgets, policies and invented aggregate information only. Do not collect benefit-recipient records, personal complaints or confidential government documents. You may pause or choose another fictional exercise. Coursework does not authorise public expenditure, eligibility decisions, statutory audit, legal advice or independent professional practice.'


def module(title, outcome, paragraphs, example, activity, feedback, sources, rows):
    return dict(title=title, outcome=outcome, paragraphs=paragraphs, example='Fictional case: ' + example,
        activity=activity, feedback=feedback, sources=sources, items=rows)


def course(number, title, cover, outcome, modules):
    return dict(code=f'SWP-{number:03}', title=title, slug=re.sub('[^a-z0-9]+', '-', title.lower()).strip('-'),
        cover_title=cover, school_code='SPG', school_name='School of Social Policy and Governance',
        school_display='Social Policy\nand Governance', estimated_minutes=180,
        audience='Introductory social-work and public-service learners analysing policy delivery, institutions and accountability under appropriate supervision.',
        study_guidance=SAFETY + ' Work through each case before checking feedback. Study time is proposed for piloting.',
        practice_safety_note=SAFETY, outcome=outcome, modules=modules)


COURSES = [load(name).build(course, module) for name in ['protection', 'finance', 'implementation', 'decentralisation', 'inequality', 'participation', 'practicum']]
