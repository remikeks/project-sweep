"""DAI lesson sources for seven additions to Digital Social Work Practice."""

import importlib.util
from pathlib import Path
import re


def load(name):
    spec = importlib.util.spec_from_file_location('dai_' + name, Path(__file__).with_name(name + '.py'))
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source


REFERENCES = load('research').REFERENCES
EVIDENCE_CHECKED_ON = '2026-11-27'
EVIDENCE_NOTE = (
    'Evidence checked 27 November 2026. Comparators, legal texts and research each answer different questions. '
    'The source notes record context, dates, access and reuse terms. Exercises use supplied fictional cases and '
    'fixed example outputs. Graded ParaLearn assessments require configured delivery and unpublished items.'
)
REVIEW_REQUIREMENTS = dict(owner_material_release_authorised=True, paralearn_mixed_exam='unverified')
SAFETY = (
    'Work with supplied fictional records and fixed example outputs. Keep real client material, account credentials '
    'and audio out of coursework. Use the agency privacy and supervision route for decisions about real services.'
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
        cover_title=cover, school_code='DAI',
        school_name='School of Digital Innovation and Artificial Intelligence in Social Work',
        school_display='Digital Innovation and AI\nin Social Work', estimated_minutes=180,
        audience='Social work learners and practitioners developing digital practice skills through guided simulation.',
        study_guidance=SAFETY + ' Try each activity before reading the feedback.',
        practice_safety_note=SAFETY, outcome=outcome, modules=modules,
    )


COURSES = [
    load(name).build(course, module)
    for name in ('inclusion', 'privacy', 'literacy', 'documentation', 'workflow', 'evaluation', 'practicum')
]
