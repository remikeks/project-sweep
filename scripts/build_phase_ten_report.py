"""Build a legible owner report and a key-free, allowlisted review bundle.

Locally reviewed implementation; staging evidence and Git publication are separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph

from pcei_build_proof import ROOT, BASE, media_summary, validate_live_proof


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-regular', type=Path, required=True)
    parser.add_argument('--font-bold', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT.parent/'output/academy_phase_ten')
    parser.add_argument('--report-date', default='19 November 2026')
    parser.add_argument('--live-proof', type=Path, help='Genuine local publishing verification export only.')
    args = parser.parse_args()
    private = ROOT/'production_courseware/private/phase-ten'
    proof = json.loads((private/'local-build-verification.json').read_text())
    assert proof['status'] == 'local_build_verified'
    assert proof['database'] == 'sqlite:///:memory:' and proof['debug'] is True
    assert proof['tests'] >= 198 and proof['protected_source_unchanged']
    assert proof['original_checkpoint'] == BASE
    release = ROOT/'production_courseware/phase_ten/pcei_media_01'
    manifest, pages, slides = media_summary(release)
    qa = json.loads((release/'visual_qa.json').read_text())
    assert qa['status'] == 'reviewed'
    assert qa['final_file_sha256'] == {r['path']: r['sha256'] for r in manifest}
    assert proof['pdf_pages'] == pages == qa['pdf_pages_reviewed']
    assert proof['slide_pages'] == slides == qa['slide_pages_reviewed']
    live = None
    if args.live_proof:
        live = json.loads(args.live_proof.read_text())
        validate_live_proof(live, manifest)
    args.output.mkdir(parents=True, exist_ok=True)
    bundle = args.output/'SWEEP_PCEI_Phase_10_Private_Review_Materials.zip'
    secret = re.compile(rb'(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sb_secret_[A-Za-z0-9]+|gh[pousr]_[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{30,}|eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,})')
    with ZipFile(bundle, 'w', ZIP_DEFLATED) as archive:
        for row in manifest:
            path = release/row['path']
            raw = path.read_bytes()
            if path.suffix == '.pdf':
                text = '\n'.join(p.extract_text() or '' for p in PdfReader(path).pages).encode()
            else:
                with ZipFile(path) as deck:
                    text = b'\n'.join(deck.read(n) for n in deck.namelist() if n.endswith('.xml'))
            assert not secret.search(text), 'Potential secret in review resource'
            assert not any(key in text for key in [b'"correct":', b'is_correct', b'"model_answer":', b'"rubric":'])
            archive.writestr(row['path'], raw)
        readme = (release/'README.md').read_bytes()
        assert not secret.search(readme)
        archive.writestr('README.md', readme)
    with ZipFile(bundle) as archive:
        assert archive.testzip() is None and len(archive.namelist()) == 21
        assert set(archive.namelist()) == {r['path'] for r in manifest} | {'README.md'}
        for row in manifest:
            assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']

    pdfmetrics.registerFont(TTFont('ReportSans', str(args.font_regular)))
    pdfmetrics.registerFont(TTFont('ReportSans-Bold', str(args.font_bold)))
    title = ParagraphStyle('Title', fontName='ReportSans-Bold', fontSize=19, leading=23,
                           textColor=colors.HexColor('#0B2C7A'), spaceAfter=10)
    body = ParagraphStyle('Body', fontName='ReportSans', fontSize=12, leading=15, spaceAfter=10)
    status = 'Private staging verified; academic release pending' if live else 'Local build verified; private staging pending'
    verification = (
        'Live verification confirmed retained-record parity, all 20 private remote file hashes and 35 public access checks. '
        'The academy now has 65 courses: 34 active originals and 31 inactive drafts; 396 assets; PCEI has eight titles. '
        'All 25 coded schools remain closed. Git publication is confirmed separately.'
        if live else
        'Private staging has not been verified by this report. Expected after verified staging: 65 courses, '
        '34 active originals, 31 inactive drafts, 396 assets, eight PCEI titles and 25 closed schools. '
        'These counts are targets until genuine live verification is supplied.'
    )
    parts = [
        f'To Prof. Mina Ogbanga, Founder, SWEEP Academy | {args.report_date}',
        'PCEI: School of Community Development and Participatory Engagement. Retain SWP-013 Community Needs Assessment, '
        'SWP-014 Community Organizing & Coalition Building and SWP-015 Program Development & Evaluation, including their existing CBT mappings.',
        'Add SWP-061 Participatory Facilitation and Community Dialogue; SWP-062 Asset Based Community Development; '
        'SWP-063 Community Accountability and Grievance Mechanisms; SWP-064 Inclusive Local Planning and Co Design; '
        'SWP-065 Community Programme Implementation Practicum.',
        f'The five drafts contain 15 modules and 75 MCQs checked against 390 earlier questions. Twenty resources comprise '
        f'five guides, five worksheets, five editable slide decks and five matching slide PDFs. All {pages} PDF pages, '
        f'including {slides} slide pages, were inspected. Guides use embedded 12-point text.',
        'Research appraised on 16 November 2026 combines IACD, OECD and World Bank guidance with recent open-access studies '
        'and contextual IJSDS evidence. Each source records methods, dates, limitations and rights. Possible survey overlap '
        'and reporting inconsistencies prevent causal teaching claims.',
        'The eight-course final exam draft has 40 MCQ slots, six short answers and two integrative essays, totalling 100 marks. '
        'Proposed duration is 210 minutes with a 70% pass mark, subject to piloting. Written answers require human marking '
        'and independent moderation. ParaLearn mixed-item compatibility remains unverified; offline results cannot certify.',
        f'Validation: {proof["tests"]} isolated tests passed in {proof["test_seconds"]:.3f} seconds; '
        f'{proof["protected_source_files"]} protected courseware files preserved. The reopened 21-entry review ZIP contains '
        'only learner materials and its README, excluding staff answer keys, rubrics, raw papers and operational records.',
        verification,
        'Before learner release: complete academic, local-practice, safeguarding, accessibility/pilot and supervised-skills reviews. '
        'Keep new courses inactive and resources private/in review. Badges require approved courses and verified ParaLearn passes. '
        'Certificates also require every school course, the moderated final exam and authorised signatures from the Head of Learning '
        'and Founder Prof. Mina Ogbanga. Head of Learning details/signature are pending.',
        'Programme progress: 31 of 150 planned additions authored; 119 remain. Next: CPS, retaining SWP-001-003 and developing '
        'five additions toward eight courses after this phase is verified and pushed.'
    ]

    def footer(canvas, doc):
        canvas.setFont('ReportSans', 9)
        canvas.setFillColor(colors.HexColor('#52617D'))
        canvas.drawString(44, 24, 'PCEI internal academic review | Final release and ParaLearn verification pending')

    report = args.output/'SWEEP_Phase_10_Report_Prof_Mina.pdf'
    flow = [Paragraph('SWEEP Academy | PCEI Phase 10', title),
            Paragraph(escape(status), ParagraphStyle('Status', parent=body, fontName='ReportSans-Bold',
                                                    textColor=colors.HexColor('#35634B')))]
    flow.extend(Paragraph(escape(s), body) for s in parts)
    SimpleDocTemplate(str(report), pagesize=A4, leftMargin=44, rightMargin=44,
                      topMargin=30, bottomMargin=38, title='SWEEP PCEI Phase 10 report',
                      author='SWEEP Academy').build(flow, onFirstPage=footer, onLaterPages=footer)
    assert len(PdfReader(report).pages) == 1, 'Edit copy to fit one page; keep 12-point body text'
    print(json.dumps(dict(report=str(report), bundle=str(bundle), entries=21, pdf_pages=pages,
                          slide_pages=slides, live_verified=bool(live)), indent=2))


if __name__ == '__main__':
    main()
