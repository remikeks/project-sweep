"""Produce the one-page owner report only from observed build and live proof."""
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
from pcei_build_proof import ROOT, media_summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--font-regular', type=Path, required=True)
    p.add_argument('--font-bold', type=Path, required=True)
    a = p.parse_args()
    private = ROOT / 'production_courseware/private/phase-twelve'
    release = ROOT / 'production_courseware/phase_twelve/spg_media_01'
    output = release.parent
    local = json.loads((private / 'local-build-verification.json').read_text())
    live = json.loads((private / 'live-release-verification.json').read_text())
    qa = json.loads((release / 'visual_qa.json').read_text())
    manifest, pages, slides = media_summary(release, expected_assets=28)
    assert local['status'] == 'local_build_verified' and local['tests'] >= 220
    assert local['database'] == 'sqlite:///:memory:' and local['protected_source_unchanged']
    assert local['original_checkpoint'] == 'f7ff8b9ed891fc75e5c125b6effca010651fb363'
    assert qa['status'] == 'reviewed' and qa['pdf_pages_reviewed'] == local['pdf_pages'] == pages
    assert qa['slide_pages_reviewed'] == local['slide_pages'] == slides
    assert qa['final_file_sha256'] == {r['path']: r['sha256'] for r in manifest}
    assert live['status'] == 'live_material_release_verified' and live['protected_parity']
    assert [live[k] for k in ['total_courses', 'active_courses', 'inactive_courses', 'published_assets', 'released_courses', 'released_resources', 'remote_hashes_verified', 'closed_coded_schools']] == [77, 77, 0, 444, 7, 28, 28, 25]
    assert len(live['public_page_checks']) == 78 and all(r['passed'] and r['status'] == 200 for r in live['public_page_checks'])
    assert len(live['unauthenticated_download_checks']) == 28 and all(r['authentication_required'] for r in live['unauthenticated_download_checks'])
    bundle_dir = ROOT.parent / 'output/academy_phase_twelve'
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle = bundle_dir / 'SWEEP_SPG_Phase_12_Learning_Materials.zip'
    secret = re.compile(rb'(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sb_secret_[A-Za-z0-9]+|gh[pousr]_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,})')
    with ZipFile(bundle, 'w', ZIP_DEFLATED) as archive:
        for row in manifest:
            path = release / row['path']; raw = path.read_bytes()
            if path.suffix == '.pdf':
                text = '\n'.join(p.extract_text() or '' for p in PdfReader(path).pages).encode()
            else:
                with ZipFile(path) as deck:
                    text = b'\n'.join(deck.read(n) for n in deck.namelist() if n.endswith('.xml'))
            assert not secret.search(text)
            assert not any(key in text for key in [b'"correct":', b'is_correct', b'"model_answer":', b'"rubric":'])
            archive.writestr(row['path'], raw)
        archive.writestr('README.md', (release / 'README.md').read_bytes())
    with ZipFile(bundle) as archive:
        assert archive.testzip() is None and len(archive.namelist()) == 29
        assert set(archive.namelist()) == {r['path'] for r in manifest} | {'README.md'}
        for row in manifest:
            assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
    pdfmetrics.registerFont(TTFont('ReportSans', str(a.font_regular)))
    pdfmetrics.registerFont(TTFont('ReportSans-Bold', str(a.font_bold)))
    title = ParagraphStyle('Title', fontName='ReportSans-Bold', fontSize=19, leading=23, spaceAfter=10, textColor=colors.HexColor('#0B2C7A'))
    body = ParagraphStyle('Body', fontName='ReportSans', fontSize=12, leading=15, spaceAfter=10)
    parts = [
        'To Prof. Mina Ogbanga, Founder, SWEEP Academy | 25 November 2026',
        'SPG: School of Social Policy and Governance now has eight courses. SWP-028 Policy Analysis Fundamentals retains its teaching, modules, resources and CBT mapping.',
        'Seven additions are live: SWP-071 Social Protection Systems and Welfare Governance; SWP-072 Public Finance Budget Analysis and Accountability; SWP-073 Policy Design Implementation and Evaluation; SWP-074 Decentralization and Inclusive Public Administration; SWP-075 Social Policy Political Economy and Inequality; SWP-076 Participatory Governance and Public Consultation; SWP-077 Policy Briefing and Reform Practicum.',
        f'The additions contain 21 modules and 105 original MCQs checked against 540 earlier questions. Twenty-eight designed resources comprise seven guides, seven worksheets, seven editable slide decks and seven matching slide PDFs. All {pages} final PDF pages, including {slides} slides, were visually inspected. Guides use embedded 12-point body text; videos are pending.',
        'Evidence checked 25 November includes ILO, PEFA, OECD and UN public-sector guidance plus open-access studies published in 2025-26. Methods, data periods, rights and access limits are recorded. Fictional budgets and cases avoid personal records. Coursework does not authorise public expenditure, eligibility decisions, legal advice or statutory audits.',
        f'Validation: {local["tests"]} isolated tests passed; {local["protected_source_files"]} existing courseware files preserved. Live checks verified 28 private file hashes, 78 public pages, 28 guest download guards and prior-record parity. The academy has 77 active courses and 444 published resources. Downloads require appropriate authentication and course enrolment. Production and hosted-CI observations are recorded separately in the build summary.',
        'The eight-course school exam map has 40 MCQ slots, six short answers and two integrative essays: 100 marks. Proposed duration is 210 minutes and pass mark 70%, pending piloting. Public source questions are review exemplars; unpublished production banks and verified ParaLearn configuration are required. Written answers require criterion-level human marking and independent moderation.',
        'Materials are released under your standing approval. Course badges await verified ParaLearn course passes. School certificates require all approved courses, the moderated final exam and authorised signatures from the Head of Learning and Founder Prof. Mina Ogbanga. Head of Learning details/signature are pending; all 25 school enrolments remain closed.',
        'Programme progress: 43 of 150 planned additions authored; 107 remain. Next: SEE, six proposed social-enterprise courses. Research its curriculum gaps before authoring, preserve existing teaching and CBTs, then build, verify, publish and push the next accurate phase.'
    ]
    report = output / 'SWEEP_Phase_12_Report_Prof_Mina.pdf'
    def footer(canvas, doc):
        canvas.setFont('ReportSans', 9); canvas.setFillColor(colors.HexColor('#52617D'))
        canvas.drawString(44, 24, 'SPG learning-material release | Provider assessment and certification readiness remain separate')
    SimpleDocTemplate(str(report), pagesize=A4, leftMargin=44, rightMargin=44, topMargin=30, bottomMargin=38, title='SWEEP SPG Phase 12 report', author='SWEEP Academy').build([Paragraph('SWEEP Academy | SPG Phase 12', title), *[Paragraph(escape(s), body) for s in parts]], onFirstPage=footer, onLaterPages=footer)
    assert len(PdfReader(report).pages) == 1, 'Edit copy to fit; retain 12-point body text'
    summary = {k: v for k, v in live.items() if k not in {'public_page_checks', 'unauthenticated_download_checks'}}
    summary.update(tests=local['tests'], test_seconds=local['test_seconds'], protected_courseware_files=local['protected_source_files'], protected_courseware_unchanged=True, pdf_pages_reviewed=pages, slide_pages_reviewed=slides, public_pages_verified=78, guest_download_guards_verified=28, spg_course_count=8, original_cbts_unchanged=True, bundle_entries=29)
    (output / 'build_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(report=str(report), bundle=str(bundle), pages=pages, slides=slides), indent=2))


if __name__ == '__main__':
    main()
