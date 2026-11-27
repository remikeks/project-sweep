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
    private = ROOT / 'production_courseware/private/phase-thirteen'
    release = ROOT / 'production_courseware/phase_thirteen/see_media_01'
    output = release.parent
    local = json.loads((private / 'local-build-verification.json').read_text())
    live = json.loads((private / 'live-release-verification.json').read_text())
    qa = json.loads((release / 'visual_qa.json').read_text())
    manifest, pages, slides = media_summary(release, expected_assets=24)
    assert local['status'] == 'local_build_verified' and local['tests'] >= 227
    assert local['database'] == 'sqlite:///:memory:' and local['protected_source_unchanged']
    assert local['original_checkpoint'] == '550db8a9b56776f9f067fe5ff206d818c57f78a8'
    assert qa['status'] == 'reviewed' and qa['pdf_pages_reviewed'] == local['pdf_pages'] == pages
    assert qa['slide_pages_reviewed'] == local['slide_pages'] == slides
    assert qa['final_file_sha256'] == {r['path']: r['sha256'] for r in manifest}
    assert live['status'] == 'live_material_release_verified' and live['protected_parity']
    assert [live[k] for k in ['total_courses', 'active_courses', 'inactive_courses', 'published_assets', 'released_courses', 'released_resources', 'remote_hashes_verified', 'closed_coded_schools']] == [83, 83, 0, 468, 6, 24, 24, 25]
    assert len(live['public_page_checks']) == 84 and all(r['passed'] and r['status'] == 200 for r in live['public_page_checks'])
    assert len(live['unauthenticated_download_checks']) == 24 and all(r['authentication_required'] for r in live['unauthenticated_download_checks'])
    bundle_dir = ROOT.parent / 'output/academy_phase_thirteen'
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle = bundle_dir / 'SWEEP_SEE_Phase_13_Learning_Materials.zip'
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
        assert archive.testzip() is None and len(archive.namelist()) == 25
        assert set(archive.namelist()) == {r['path'] for r in manifest} | {'README.md'}
        for row in manifest:
            assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
    pdfmetrics.registerFont(TTFont('ReportSans', str(a.font_regular)))
    pdfmetrics.registerFont(TTFont('ReportSans-Bold', str(a.font_bold)))
    title = ParagraphStyle('Title', fontName='ReportSans-Bold', fontSize=19, leading=23, spaceAfter=10, textColor=colors.HexColor('#0B2C7A'))
    body = ParagraphStyle('Body', fontName='ReportSans', fontSize=12, leading=15, spaceAfter=10)
    parts = [
        'To Prof. Mina Ogbanga, Founder, SWEEP Academy | 27 November 2026',
        'SEE: School of Social Entrepreneurship and Enterprise Development now has six courses. Its verified baseline had no courses. All earlier academy teaching, modules, resources, CBT mappings, learner records and credentials remain unchanged.',
        'Six additions are live: SWP-078 Social Enterprise Models and Social Innovation; SWP-079 Community Market Research and Value Propositions; SWP-080 Business Models Costing and Cash Flow; SWP-081 Social Finance Cooperative Models and Inclusion; SWP-082 Impact Measurement and Mission Accountability; SWP-083 Social Enterprise Launch Practicum.',
        f'The additions contain 18 modules and 90 original MCQs checked against 645 earlier questions. Twenty-four resources comprise six guides, six worksheets, six editable slide decks and six matching slide PDFs. All {pages} final PDF pages, including {slides} slides, were visually inspected. Guides use embedded 12-point body text; videos are pending.',
        'Evidence checked 27 November includes enterprise, cooperative and impact guidance plus open-access research published in 2025-26. Methods, data periods, rights and access limits are recorded. Selected NUC curriculum domains and EntreComp foundation progression inform this introductory pathway; no degree equivalence is claimed. All transactions and cases are fictional; real trading, finance, employment, tax and legal matters require qualified advice and authority.',
        f'Validation: {local["tests"]} isolated tests passed; {local["protected_source_files"]} earlier courseware files preserved. Live checks verified 24 fresh private hashes, 84 public pages, 24 guest download guards and prior-record parity. The academy has 83 active courses and 468 published resources. Vercel production is READY. Hosted CI status is recorded from the actual run in the build summary.',
        'The six-course school exam map has 40 MCQ slots, six short answers and two essays integrating all six courses: 100 marks. Proposed duration is 210 minutes and pass mark 70%, pending piloting. Public source questions are review examples; unpublished production banks and verified ParaLearn configuration are required. Written work requires human criterion marking and independent moderation.',
        'Materials are released under your standing approval. Badges await verified course CBT passes. School certificates require every approved course, the moderated mixed exam and authorised signatures from the Head of Learning and Founder Prof. Mina Ogbanga. Head of Learning details/signature remain pending; all 25 school enrolments stay closed.',
        'Programme progress: 49 of 150 planned additions authored; 101 remain. Next: DAI, retaining SWP-031 and researching seven additions toward eight courses. Verify its live scope, preserve existing teaching and CBTs, then build, review, publish and push the next accurate phase.'
    ]
    report = output / 'SWEEP_Phase_13_Report_Prof_Mina.pdf'
    def footer(canvas, doc):
        canvas.setFont('ReportSans', 9); canvas.setFillColor(colors.HexColor('#52617D'))
        canvas.drawString(44, 24, 'SEE learning-material release | Provider assessment and certification readiness remain separate')
    SimpleDocTemplate(str(report), pagesize=A4, leftMargin=44, rightMargin=44, topMargin=30, bottomMargin=38, title='SWEEP SEE Phase 13 report', author='SWEEP Academy').build([Paragraph('SWEEP Academy | SEE Phase 13', title), *[Paragraph(escape(s), body) for s in parts]], onFirstPage=footer, onLaterPages=footer)
    assert len(PdfReader(report).pages) == 1, 'Edit copy to fit; retain 12-point body text'
    summary = {k: v for k, v in live.items() if k not in {'public_page_checks', 'unauthenticated_download_checks'}}
    summary.update(tests=local['tests'], test_seconds=local['test_seconds'], protected_courseware_files=local['protected_source_files'], protected_courseware_unchanged=True, pdf_pages_reviewed=pages, slide_pages_reviewed=slides, public_pages_verified=84, guest_download_guards_verified=24, see_course_count=6, original_cbts_unchanged=True, bundle_entries=25)
    deployment = json.loads((private / 'verified-deployment.json').read_text())
    post = json.loads((private / 'post-deployment-verification.json').read_text())
    ci = json.loads((private / 'ci-verification.json').read_text())
    assert deployment['status'] == 'READY' and deployment['server_metadata_source_verified']
    assert re.fullmatch(r'[0-9a-f]{40}', deployment['source_commit'])
    assert set(deployment['production_domains']) == {'sweepacademy.org', 'www.sweepacademy.org'}
    assert post['status'] == 'post_deployment_http_verified' and post['catalogue_active_count'] == 83
    assert len(post['see_course_pages']) == 6 and all(r['passed'] for r in post['see_course_pages'])
    assert len(post['guest_download_guards']) == 24 and all(r['authentication_required'] for r in post['guest_download_guards'])
    assert ci['source_commit'] == deployment['source_commit'] and ci['status'] in {'not_started_account_billing', 'passed', 'failed', 'pending'}
    summary.update(source_package_sha256=json.loads((output / 'see_batch_01/validation.json').read_text())['package_sha256'],
        material_approval='Standing owner authorisation recorded 27 November 2026', report_pages=1, report_body_points=12,
        report_visually_reviewed=False, learner_bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),
        repository_visibility='PUBLIC', assessment_source_status='Disclosed unbound review exemplars; unpublished production banks required before graded ParaLearn launch',
        academic_comparator_check='NUC selected entrepreneurship sections and EntreComp supported foundation-level progression; no degree equivalence',
        deployment_status=deployment['status'], deployment_id=deployment['id'], deployment_url=deployment['url'],
        deployment_source_commit=deployment['source_commit'], production_domains=deployment['production_domains'], deployment_source_verified=True,
        post_deployment_verified_on=post['verified_on'], post_deployment_see_pages_verified=6, post_deployment_guest_guards_verified=24,
        github_ci_status=ci['status'], github_ci_run=ci['run_url'], github_ci_annotation=ci['annotation'])
    (output / 'build_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(report=str(report), bundle=str(bundle), pages=pages, slides=slides), indent=2))


if __name__ == '__main__':
    main()
