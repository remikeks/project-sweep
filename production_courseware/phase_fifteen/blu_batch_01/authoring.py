"""BLU lesson sources for six coastal social work courses."""

import importlib.util
from pathlib import Path
import re


def load(name):
    spec = importlib.util.spec_from_file_location('blu_' + name, Path(__file__).with_name(name + '.py'))
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source


REFERENCES = load('research').REFERENCES
EVIDENCE_CHECKED_ON = '2026-11-27'
EVIDENCE_NOTE = (
    'Evidence checked 27 November 2026. Practice guidance and research each answer different questions. '
    'The source notes record context, dates, access and reuse terms. Exercises use supplied fictional cases and '
    'invented figures. Graded ParaLearn assessments require configured delivery and unpublished items.'
)
REVIEW_REQUIREMENTS = dict(owner_material_release_authorised=True, paralearn_mixed_exam='unverified')
SAFETY = (
    'Use the supplied fictional coastal cases and invented figures. Route real safety, legal, environmental '
    'and funding decisions through the responsible qualified teams. Work from the classroom materials.'
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
        cover_title=cover, school_code='BLU',
        school_name='School of Climate Change and Blue Economy Social Work',
        school_display='Climate Change and\nBlue Economy Social Work', estimated_minutes=180,
        audience='Social work learners and practitioners developing coastal practice skills through guided simulation.',
        study_guidance=SAFETY + ' Try each activity before reading the feedback.',
        practice_safety_note=SAFETY, outcome=outcome, modules=modules,
    )


COURSES = [
    load(name).build(course, module)
    for name in ('foundations', 'fisheries', 'adaptation', 'conservation', 'finance', 'practicum')
]
