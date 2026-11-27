"""Create the one-page DAI owner report and a hash-checked learner ZIP."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'production_courseware/phase_fourteen'
MEDIA = OUTPUT / 'dai_media_01'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-regular', required=True)
    parser.add_argument('--font-bold', required=True)
    args = parser.parse_args()
    summary = json.loads((OUTPUT / 'build_summary.json').read_text(encoding='utf-8'))
    package = json.loads((OUTPUT / 'dai_batch_01/review_package.json').read_text(encoding='utf-8'))
    manifest = json.loads((MEDIA / 'upload_manifest.json').read_text(encoding='utf-8'))
    assert summary['live_verified'] and summary['production_ready'] and len(manifest) == 28

    bundle_dir = ROOT.parent / 'output/academy_phase_fourteen'
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / 'SWEEP_DAI_Phase_14_Learning_Materials.zip'
    with ZipFile(bundle_path, 'w', ZIP_DEFLATED) as bundle:
        for row in manifest:
            data = (MEDIA / row['path']).read_bytes()
            assert sha256(data).hexdigest() == row['sha256']
            bundle.writestr(row['path'], data)
        bundle.write(MEDIA / 'README.md', 'README.md')
    with ZipFile(bundle_path) as bundle:
        assert len(bundle.namelist()) == 29 and bundle.testzip() is None
        assert set(bundle.namelist()) == {row['path'] for row in manifest} | {'README.md'}
        for row in manifest:
            assert sha256(bundle.read(row['path'])).hexdigest() == row['sha256']

    pdfmetrics.registerFont(TTFont('ReportSans', args.font_regular))
    pdfmetrics.registerFont(TTFont('ReportSans-Bold', args.font_bold))
    title = ParagraphStyle('Title', fontName='ReportSans-Bold', fontSize=20, leading=24,
                           textColor=colors.HexColor('#0B2C7A'), spaceAfter=12)
    body = ParagraphStyle('Body', fontName='ReportSans', fontSize=12, leading=15, spaceAfter=9)
    course_text = ' '.join(f"{c['code']} {c['title']}." for c in package['courses'])
    ci = {
        'not_started_account_billing': 'GitHub hosted CI could not start because of an account billing lock.',
        'passed': 'GitHub hosted CI passed.',
        'failed': 'GitHub hosted CI reported a failure. The release record links the run.',
        'pending': 'GitHub hosted CI had yet to finish when this report was prepared.',
    }[summary['github_ci_status']]
    parts = [
        'To Prof. Mina Ogbanga, Founder, SWEEP Academy | 27 November 2026',
        'The School of Digital Innovation and Artificial Intelligence in Social Work (DAI) now has eight active courses. Digital Social Work Practice (SWP-031) continues as the foundation, with its three modules and existing CBT.',
        course_text,
        'The seven additions contain 21 modules, worked cases and 105 review MCQs. The 28 learner files include seven guides with 12-point body text, seven three-page worksheets, seven editable PowerPoint decks and their matching slide PDFs. Videos are planned for a later phase.',
        'The curriculum combines ethical technology use, accessibility, Nigerian data protection, AI review and accountable casework. It draws on CSWE and DigComp benchmarks, open research from 2026 and IJSDS discussion of cultural fit. Learners apply the material to fictional records and fixed sample drafts.',
        f"All {summary['isolated_tests']} isolated tests passed. Live checks verified the academy’s 90 courses, 496 resources, the 28 new file hashes and 28 login guards. Both academy domains serve the deployed build. {ci}",
        'The draft ParaLearn school exam covers all eight courses through 40 MCQ slots, six short answers and two essays. New badges require verified course CBT passes. School certification requires the final verified exam, human marking and independent moderation of written responses, and authorised signatures from the Head of Learning and Founder. The Head of Learning details are pending.',
        'The academy has authored 56 of 150 planned additions. Next is BLU, the School of Climate Change and Blue Economy Social Work. Verify the current course inventory and benchmark the six proposed courses before building and releasing the next batch.',
    ]
    report = OUTPUT / 'SWEEP_Phase_14_Report_Prof_Mina.pdf'
    doc = SimpleDocTemplate(str(report), pagesize=A4, leftMargin=44, rightMargin=44,
                            topMargin=34, bottomMargin=37, title='SWEEP DAI Phase 14 report',
                            author='SWEEP Academy')
    doc.build([Paragraph('SWEEP Academy | DAI Phase 14', title), *[
        Paragraph(escape(part), body) for part in parts
    ]])
    assert len(PdfReader(report).pages) == 1
    print(report)
    print(bundle_path)


if __name__ == '__main__':
    main()
