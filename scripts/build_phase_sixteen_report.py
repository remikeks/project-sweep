"""Create the one-page EIL owner report and a hash-checked learner ZIP."""
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
OUTPUT = ROOT / 'production_courseware/phase_sixteen'
MEDIA = OUTPUT / 'eil_media_01'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-regular', required=True)
    parser.add_argument('--font-bold', required=True)
    args = parser.parse_args()
    summary = json.loads((OUTPUT / 'build_summary.json').read_text(encoding='utf-8'))
    package = json.loads((OUTPUT / 'eil_batch_01/review_package.json').read_text(encoding='utf-8'))
    manifest = json.loads((MEDIA / 'upload_manifest.json').read_text(encoding='utf-8'))
    assert summary['live_verified'] and summary['production_ready'] and len(manifest) == 32

    bundle_dir = ROOT.parent / 'output/academy_phase_sixteen'
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / 'SWEEP_EIL_Phase_16_Learning_Materials.zip'
    with ZipFile(bundle_path, 'w', ZIP_DEFLATED) as bundle:
        for row in manifest:
            data = (MEDIA / row['path']).read_bytes()
            assert sha256(data).hexdigest() == row['sha256']
            bundle.writestr(row['path'], data)
        bundle.write(MEDIA / 'README.md', 'README.md')
    with ZipFile(bundle_path) as bundle:
        assert len(bundle.namelist()) == 33 and bundle.testzip() is None
        assert set(bundle.namelist()) == {row['path'] for row in manifest} | {'README.md'}
        for row in manifest:
            assert sha256(bundle.read(row['path'])).hexdigest() == row['sha256']

    pdfmetrics.registerFont(TTFont('ReportSans', args.font_regular))
    pdfmetrics.registerFont(TTFont('ReportSans-Bold', args.font_bold))
    pdfmetrics.registerFontFamily('ReportSans', normal='ReportSans', bold='ReportSans-Bold')
    title = ParagraphStyle('Title', fontName='ReportSans-Bold', fontSize=20, leading=24,
                           textColor=colors.HexColor('#0B2C7A'), spaceAfter=12)
    body = ParagraphStyle('Body', fontName='ReportSans', fontSize=12, leading=15, spaceAfter=9)
    course_style = ParagraphStyle('Course', parent=body, leading=14, spaceAfter=3)
    course_lines = [Paragraph(f"<b>{escape(c['code'])}</b>  {escape(c['title'])}", course_style)
                    for c in package['courses']]
    ci = {
        'not_started_account_billing': 'GitHub hosted CI could not start because of an account billing lock.',
        'passed': 'GitHub hosted CI passed.',
        'failed': 'GitHub hosted CI reported a failure. The release record links the run.',
        'pending': 'GitHub hosted CI had yet to finish when this report was prepared.',
    }[summary['github_ci_status']]
    introduction = [
        'To Prof. Mina Ogbanga, Founder, SWEEP Academy | 28 November 2026',
        'EIL, the School of Extractive Industries, Livelihoods and SW-EMHEC, reached its target of eight active courses. The school retains its recorded name. The meaning of SW-EMHEC is unconfirmed, so the curriculum covers the agreed extractives and livelihoods scope.',
    ]
    findings = [
        'The eight additions contain 24 modules and 120 review MCQs. The 32 learner files include eight 12-point guides, eight three-page worksheets, eight editable PowerPoint decks and their matching slide PDFs. Videos are planned for a later phase.',
        'The curriculum uses fictional cases to apply international practice guidance, open Q1 research and Nigerian IJSDS contextual reading. University of Queensland and University of Toronto course outlines helped benchmark topic coverage.',
        f"All {summary['isolated_tests']} isolated tests passed. Live checks verified 104 active courses, 552 resources, 32 file hashes and preserved earlier CBTs. Both academy domains serve the published materials. {ci}",
        'Both domains were restored to the last verified academy deployment after they began serving an unrelated project. Phase 16 was pushed to SWEEP main and released through the live catalogue.',
        'The ParaLearn school exam draft covers all eight courses with 40 MCQ slots, six short answers and two essays. Student badges require verified course CBT passes. Certification also requires final mixed-exam verification, human marking and independent moderation, and the authorised signatures of the Head of Learning and Founder.',
        'Phase 16 brings the programme to 70 of 150 planned additions. Phase 17 covers Humanitarian Action and Disaster Response (HDR), with three courses to retain and five additions to develop.',
    ]
    report = OUTPUT / 'SWEEP_Phase_16_Report_Prof_Mina.pdf'
    doc = SimpleDocTemplate(str(report), pagesize=A4, leftMargin=44, rightMargin=44,
                            topMargin=34, bottomMargin=37, title='SWEEP EIL Phase 16 report',
                            author='SWEEP Academy')
    doc.build([
        Paragraph('SWEEP Academy | EIL Phase 16', title),
        *[Paragraph(escape(p), body) for p in introduction],
        *course_lines,
        *[Paragraph(escape(p), body) for p in findings],
    ])
    assert len(PdfReader(report).pages) == 1
    print(report)
    print(bundle_path)


if __name__ == '__main__':
    main()
