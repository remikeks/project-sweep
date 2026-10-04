"""Package observed ParaLearn question exports; never invent missing answers."""
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'production_courseware' / 'qa'
catalogue = json.loads((ROOT / 'production_courseware/release-2026-10-03/course_catalogue.json').read_text(encoding='utf-8'))

def scalar(value):
    if value.startswith('"'):
        return json.loads(value)
    return value

views = json.loads((QA / 'paralearn-swp-024-editor-export.json').read_text(encoding='utf-8'))
questions = []
for number, view in enumerate(views, 1):
    main = view.split('- main:\n', 1)[1]
    assert f'Editing Question #{number}' in main
    question = re.search(r'textbox "Enter question statement or case study prompt\.\.\.": (.*)', main).group(1)
    options = []
    for match in re.finditer(r'- button "(Correct answer|[A-D])"[^\n]*\n  - textbox "Option ([A-D]) text\.\.\.": (.*)', main):
        options.append({'text': match[2] + '. ' + scalar(match[3]), 'correct': match[1] == 'Correct answer'})
    rationale = re.search(r'textbox "e\.g\. Highlighting core principles, formulas, and common student misconceptions\.\.\.": (.*)', main).group(1)
    assert len(options) == 4 and sum(o['correct'] for o in options) == 1
    questions.append({'question': scalar(question), 'options': options, 'rationale': 'Rationale: ' + scalar(rationale), 'metadata': ['MCQ', 'Exported from visible editor; expert review required']})
assert len(questions) == 15
bank = {'course_code': 'SWP-024', 'title': catalogue[23]['title'], 'status': 'AI draft — expert review required; server status unverified', 'questions': questions}
(QA / 'paralearn-swp-024-questions.json').write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')

banks = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(QA.glob('paralearn-swp-*-questions.json'))]
rows = []
flags = []
for bank in banks:
    qs = bank['questions']
    assert len(qs) == 15
    for i, q in enumerate(qs, 1):
        assert sum(o['correct'] for o in q['options']) == 1
        if len(q['options']) != 4 or q['metadata'][0] != 'MCQ':
            flags.append(f"{bank['course_code']} question {i}: {q['metadata'][0]}, {len(q['options'])} options; review requested four-option format.")
    text = f"# {bank['course_code']} — {bank['title']}\n\nAI-generated draft. Expert review required. Export is not publication approval.\n\n"
    for i, q in enumerate(qs, 1):
        text += f"## {i}. {q['question']}\n\n"
        text += '\n'.join('- ' + o['text'] + (' **[Correct]**' if o['correct'] else '') for o in q['options'])
        text += '\n\n' + q['rationale'] + '\n\n' + ' · '.join(q['metadata']) + '\n\n'
    filename = f"paralearn-{bank['course_code'].lower()}-questions.md"
    (QA / filename).write_text(text, encoding='utf-8')
    rows.append(f"| {bank['course_code']} | {bank['title']} | {len(qs)} | [{filename}]({filename}) |")
index = '# ParaLearn review bank exports\n\n'
index += f"{len(banks)} course banks, {sum(len(b['questions']) for b in banks)} questions, with observed answer keys and rationales. These are AI drafts requiring expert review.\n\n"
index += 'SWP-001–006 were previously verified synchronized in ParaLearn (90 questions). SWP-006 still displayed published after Unpublish attempts; treat it as potentially accessible. SWP-007–023 were exported from AI previews without imports during this pass. SWP-024 was recovered from a visible local editor after the browser session changed; its server status is unverified. SWP-025–030 remain to generate.\n\n'
index += 'Work paused when the active ParaLearn account changed to internship@parakletus.com / internship\'s Exam Hall. Restore the SWEEP ACADEMY account before continuing generation.\n\n'
index += '| Course | Title | Questions | Review file |\n|---|---|---:|---|\n' + '\n'.join(rows)
index += '\n\n## Format review flags\n\n' + ('\n'.join('- ' + flag for flag in flags) if flags else 'No structural format flags.')
index += '\n\nCheck source grounding, answer accuracy, local policy and scope, distractor quality, document-structure questions, and consistent marks before publication. Structural validation is not expert content approval.\n'
(QA / 'PARALEARN_REVIEW_INDEX.md').write_text(index, encoding='utf-8')
with ZipFile(QA / 'paralearn-review-banks.zip', 'w', ZIP_DEFLATED) as bundle:
    bundle.write(QA / 'PARALEARN_REVIEW_INDEX.md', 'PARALEARN_REVIEW_INDEX.md')
    for bank in banks:
        for extension in ('md', 'json'):
            path = QA / f"paralearn-{bank['course_code'].lower()}-questions.{extension}"
            bundle.write(path, path.name)
print(json.dumps({'banks': len(banks), 'questions': sum(len(b['questions']) for b in banks), 'format_flags': flags}))
