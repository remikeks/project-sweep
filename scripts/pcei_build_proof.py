"""Read-only proof checks. No network, deployment or credential operations."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='3ea7bf212314148cd1c6ade754de177aca9a65e2'
PRIOR=['phase_two/fsw_batch_01','phase_four/fsw_batch_02','phase_five/ert_batch_01','phase_six/ert_batch_02','phase_seven/gbv_batch_01','phase_eight/gbv_batch_02','phase_nine/mhp_batch_01','phase_ten/pcei_batch_01']
def expected_public_checks():
    expected={'/courses/':200}
    for p in PRIOR:
        for c in json.loads((ROOT/'production_courseware'/p/'review_package.json').read_text(encoding='utf-8'))['courses']:
            expected['/courses/'+c['slug']+'/']=404
    for c in json.loads((ROOT/'production_courseware/release-2026-10-03/course_catalogue.json').read_text(encoding='utf-8')):
        if c['code'] in ['SWP-013','SWP-014','SWP-015']:expected['/courses/'+c['slug']+'/']=200
    assert len(expected)==35
    return expected

def validate_live_proof(live,manifest):
    """Validate supplied real bridge export; never asserts host performed checks."""
    assert live['school_code']=='PCEI' and live['preexisting_parity'] is True
    assert live['source_courses_verified']==5 and live['private_resources_verified']==20
    fields=['total_courses','active_courses','inactive_drafts','total_assets','school_courses','school_target','closed_coded_schools']
    assert [live[k] for k in fields]==[65,34,31,396,8,8,25]
    rows=live['remote_files']
    assert len(rows)==20 and len({r['path'] for r in rows})==20
    assert {r['path']:r['sha256'] for r in rows}=={r['path']:r['sha256'] for r in manifest}
    checks=live['public_checks'];expected=expected_public_checks()
    assert len(checks)==35 and len({r['path'] for r in checks})==35
    assert {r['path']:r['status'] for r in checks}==expected
    assert all(r['passed'] is True for r in checks)
    assert live['verification_provenance'].strip() and live['verified_on'].strip()
    return True

def media_summary(release, expected_assets=20):
    from pypdf import PdfReader
    manifest=json.loads((release/'upload_manifest.json').read_text())
    pages=slides=0
    for row in manifest:
        path=release/row['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        if path.suffix=='.pdf':
            n=len(PdfReader(path).pages);pages+=n
            if 'course-slides' in path.name:slides+=n
    assert len(manifest)==expected_assets
    return manifest,pages,slides
