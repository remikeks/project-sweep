"""EIL lesson sources for eight applied extractives social work courses."""

import importlib.util
from pathlib import Path
import re


def load(name):
    spec = importlib.util.spec_from_file_location('eil_' + name, Path(__file__).with_name(name + '.py'))
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source


REFERENCES = load('research').REFERENCES
EVIDENCE_CHECKED_ON = '2026-11-28'
EVIDENCE_NOTE = (
    'Evidence checked 28 November 2026. The register distinguishes practice frameworks, open research '
    'and contextual reading. Classroom cases and figures are fictional. Graded ParaLearn delivery '
    'requires verified configuration and unpublished questions.'
)
REVIEW_REQUIREMENTS = dict(owner_material_release_authorised=True, paralearn_mixed_exam='unverified')
SAFETY = (
    'Work from the classroom case records. Refer real environmental testing, clinical assessment, '
    'legal decisions and site access to the responsible qualified teams.'
)


def module(title, outcome, teaching, example, activity, feedback, questions):
    paragraphs = teaching.strip().split('\n\n')
    sources = sorted(set(re.findall(r'\b(?:S|R)\d+\b', teaching)))
    items = []
    for line in questions.strip().splitlines():
        point, stem, answer, a, b, c, rationale = (field.strip() for field in line.split('|'))
        items.append((point, stem, answer, [a, b, c], rationale))
    return dict(title=title, outcome=outcome, paragraphs=paragraphs, example='Fictional case: ' + example,
                activity=activity, feedback=feedback, sources=sources, items=items)


def course(number, title, cover, outcome, modules):
    return dict(
        code=f'SWP-{number:03}', title=title, slug=re.sub('[^a-z0-9]+', '-', title.lower()).strip('-'),
        cover_title=cover, school_code='EIL',
        school_name='School of Extractive Industries, Livelihoods and SW-EMHEC',
        school_display='Extractive Industries, Livelihoods\nand SW-EMHEC', estimated_minutes=180,
        audience='Social work learners and practitioners developing extractive-sector community practice skills.',
        study_guidance=SAFETY + ' Complete each practice task before reading the feedback.',
        practice_safety_note=SAFETY, outcome=outcome, modules=modules,
    )


COURSES = [
    load(name).build(course, module)
    for name in ('relations', 'assessment', 'livelihoods', 'health', 'land', 'grievance', 'accountability', 'practicum')
]
