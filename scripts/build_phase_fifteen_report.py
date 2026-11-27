"""Create the one-page BLU owner report and a hash-checked learner ZIP."""
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
OUTPUT = ROOT / 'production_courseware/phase_fifteen'
MEDIA = OUTPUT / 'blu_media_01'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-regular', required=True)
    parser.add_argument('--font-bold', required=True)
    args = parser.parse_args()
    summary = json.loads((OUTPUT / 'build_summary.json').read_text(encoding='utf-8'))
    package = json.loads((OUTPUT / 'blu_batch_01/review_package.json').read_text(encoding='utf-8'))
    manifest = json.loads((MEDIA / 'upload_manifest.json').read_text(encoding='utf-8'))
    assert summary['live_verified'] and summary['production_ready'] and len(manifest) == 24

    bundle_dir = ROOT.parent / 'output/academy_phase_fifteen'
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / 'SWEEP_BLU_Phase_15_Learning_Materials.zip'
    with ZipFile(bundle_path, 'w', ZIP_DEFLATED) as bundle:
        for row in manifest:
            data = (MEDIA / row['path']).read_bytes()
            assert sha256(data).hexdigest() == row['sha256']
            bundle.writestr(row['path'], data)
        bundle.write(MEDIA / 'README.md', 'README.md')
    with ZipFile(bundle_path) as bundle:
        assert len(bundle.namelist()) == 25 and bundle.testzip() is None
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
        'To Prof. Mina Ogbanga, Founder, SWEEP Academy | 28 November 2026',
        'The School of Climate Change and Blue Economy Social Work (BLU) reached its target of six active courses. The live baseline had no BLU courses. Earlier academy courses, records and CBTs passed preservation checks.',
        course_text,
        'The six additions contain 18 modules and 90 review MCQs. The 24 learner files comprise six guides with 12-point body text, six three-page worksheets, six editable PowerPoint decks and their matching slide PDFs. Videos are planned for a later phase.',
        'Learners use fictional coastal cases to study fisheries livelihoods, adaptation, conservation, finance and community benefit. The evidence register documents FAO, IPCC and other frameworks, open journal research, including Nigerian studies, and contextual IJSDS reading.',
        f"All {summary['isolated_tests']} isolated tests passed. Live checks verified 96 academy courses, 520 resources and 24 new file hashes and login guards. Both academy domains serve the deployed build. {ci}",
        'The draft ParaLearn school exam covers all six courses through 40 MCQ slots, six short answers and two integrated essays. Badges require a verified course CBT pass. Certification requires the final verified exam, human marking and moderation of written answers, and authorised signatures from the Head of Learning and Founder. The Head of Learning details are pending.',
        'Phase 15 brings the programme to 62 of 150 planned course additions. Next is EIL, the School of Extractive Industries, Livelihoods and SW-EMHEC, with an eight-course target.',
    ]
    report = OUTPUT / 'SWEEP_Phase_15_Report_Prof_Mina.pdf'
    doc = SimpleDocTemplate(str(report), pagesize=A4, leftMargin=44, rightMargin=44,
                            topMargin=34, bottomMargin=37, title='SWEEP BLU Phase 15 report',
                            author='SWEEP Academy')
    doc.build([Paragraph('SWEEP Academy | BLU Phase 15', title), *[
        Paragraph(escape(part), body) for part in parts
    ]])
    assert len(PdfReader(report).pages) == 1
    print(report)
    print(bundle_path)


if __name__ == '__main__':
    main()
