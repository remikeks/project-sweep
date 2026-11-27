"""SEE traceability, mixed-exam safeguards and create-only release boundaries."""
import copy
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase
from courses.test_ert_phase_five import read, module
from courses.authored_review import validate_package
from courses.assessment_review_validation import validate_review_bank
from courses.curriculum_validation import validate_manifest
from courses.models import Course, CourseModule, CourseAsset
from courses.material_publication import load_entries, preflight, protected_snapshot, lifecycle_state, publish_atomically
from schools.models import School
from schools.exam_blueprints import validate_blueprint
from schools.see_exam_review import review_see_result

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'production_courseware/phase_thirteen/see_batch_01'
MEDIA = ROOT / 'production_courseware/phase_thirteen/see_media_01'


class SeeSourceTests(SimpleTestCase):
    def test_source_determinism_and_prior_question_rejection(self):
        compiler = module(ROOT / 'scripts/build_course_review_batch.py', 'see_compiler')
        source = module(BATCH / 'authoring.py', 'see_source')
        data = read(BATCH / 'review_package.json')
        self.assertEqual(compiler.compile_package(source), data)
        self.assertEqual(validate_package(data), dict(courses=6, modules=18, questions=90))
        prior_batches = module(ROOT / 'scripts/build_see_source.py', 'see_prior').PRIOR
        prior = [q['question'] for p in prior_batches for c in read(ROOT / 'production_courseware' / p / 'review_package.json')['courses'] for q in c['assessment']['questions']]
        self.assertEqual(len(prior), 645)
        for c in data['courses']:
            self.assertEqual(c['school_code'], 'SEE')
            self.assertIn('Use supplied fictional enterprises', c['practice_safety_note'])
            for m in c['modules']:
                self.assertGreaterEqual(len(' '.join(m['paragraphs']).split()), 250)
            identity = dict(code=c['code'], title=c['title'], slug=c['slug'], modules=c['modules'])
            validate_review_bank(c['assessment'], identity, existing_stems=prior)
            bad = copy.deepcopy(c['assessment']); bad['questions'][0]['question'] = prior[0]
            with self.assertRaises(ValueError): validate_review_bank(bad, identity, existing_stems=prior)
            prior.extend(q['question'] for q in c['assessment']['questions'])

    def test_evidence_distinguishes_dates_unread_sources_and_outcomes(self):
        data = read(BATCH / 'review_package.json'); refs = {r['id']: r for r in data['references']}
        self.assertEqual(data['evidence_checked_on'], '2026-11-27')
        self.assertIn('January 2026', refs['R71']['appraisal'])
        self.assertIn('differing interview/startup counts', refs['R71']['appraisal'])
        self.assertIn('no formal quality appraisal', refs['R72']['appraisal'])
        self.assertIn('November 2023', refs['R72']['appraisal'])
        self.assertIn('December 2021', refs['R73']['appraisal'])
        self.assertIn('direct reader returned 403', refs['R73']['appraisal'])
        self.assertIn('CC BY-NC-ND 4.0', refs['R73']['licence'])
        self.assertIn('1995 statement', refs['S63']['appraisal'])
        self.assertTrue(all(r['licence'] and r['checked_on'] == '2026-11-27' for r in refs.values()))

    def test_exam_covers_all_six_actual_domains_without_provider_bindings(self):
        b = read(BATCH / 'school_exam_blueprint.json')
        self.assertEqual(b, module(ROOT / 'scripts/build_see_six_course_exam.py', 'see_exam').blueprint())
        self.assertEqual(validate_blueprint(b), dict(courses=6, items=48, marks=100, unbound_mcqs=40, ready_for_launch=False))
        self.assertEqual(b['retained_course_domains'], {})
        from collections import Counter
        counts = Counter(i['course_codes'][0] for i in b['items'] if i['type'] == 'MCQ')
        self.assertEqual([counts[c] for c in b['required_courses']], [7, 7, 7, 7, 6, 6])
        self.assertEqual({c for i in b['items'] if i['type'] == 'SHORT_ANSWER' for c in i['course_codes']}, set(b['required_courses']))
        self.assertTrue(all(i['course_codes'] == b['required_courses'] for i in b['items'] if i['type'] == 'ESSAY'))
        self.assertIsNone(b['provider_assessment_id']); self.assertFalse(b['certification']['authorised'])

    def test_human_review_rejects_self_moderation_missing_history_and_wrong_totals(self):
        b = read(BATCH / 'school_exam_blueprint.json')
        result = dict(school_code='SEE', curriculum_version=b['curriculum_version'], completed_courses=b['required_courses'], status='finalized', moderation_status='approved', item_results=[])
        for i in b['items']:
            result['item_results'].append(dict(id=i['id'], score=i['marks'], marking_status='marked', human_marker_id='fixture-marker', human_moderator_id='fixture-moderator', moderation_status='approved', rubric_version='0.1.0', moderation_rationale='Fictional criterion review.', amendment_history=[], appeal_history=[], criterion_results=[dict(criterion=r['criterion'], score=r['marks'], rationale='Fictional answer demonstrates applied reasoning.') for r in i.get('rubric', [])]))
        self.assertTrue(review_see_result(b, result, verified_transport=True)['contract_checks_passed'])
        self.assertFalse(review_see_result(b, result)['contract_checks_passed'])
        self.assertFalse(review_see_result(b, result, verified_transport=True)['certificate_authorised'])
        for field, value in [('human_moderator_id', 'fixture-marker'), ('criterion_results', []), ('appeal_history', None), ('rubric_version', '')]:
            bad = copy.deepcopy(result); bad['item_results'][40][field] = value
            self.assertFalse(review_see_result(b, bad, verified_transport=True)['contract_checks_passed'])
        bad = copy.deepcopy(result); bad['item_results'][40]['criterion_results'][0]['score'] = 0
        self.assertFalse(review_see_result(b, bad, verified_transport=True)['contract_checks_passed'])
        bad = copy.deepcopy(b); bad['school_code'] = 'PCEI'
        self.assertFalse(review_see_result(bad, result, verified_transport=True)['contract_checks_passed'])

    def test_actual_resources_have_embedded_legible_fonts_and_approved_edition(self):
        from pypdf import PdfReader
        import pdfplumber
        manifest = read(MEDIA / 'upload_manifest.json')
        self.assertEqual(validate_manifest(manifest, release=MEDIA, profile='pdf_slides'), dict(assets=24, asset_courses=6))
        self.assertEqual({r['school_code'] for r in manifest}, {'SEE'})
        for r in manifest:
            if r['asset_type'] not in {'learner_guide', 'worksheet'}: continue
            reader = PdfReader(MEDIA / r['path'])
            if r['asset_type'] == 'worksheet': self.assertEqual(len(reader.pages), 3)
            for page in reader.pages:
                self.assertIn('Approved learning materials', page.extract_text())
                fonts = [f.get_object() for f in page['/Resources']['/Font'].values()]
                self.assertGreaterEqual(len([f for f in fonts if f.get('/FontDescriptor') and f['/FontDescriptor'].get('/FontFile2')]), 2)
                if r['asset_type'] == 'worksheet': self.assertIn('Use supplied fictional enterprises', ' '.join(page.extract_text().split()))
            if r['asset_type'] == 'learner_guide':
                with pdfplumber.open(MEDIA / r['path']) as pdf:
                    self.assertGreater(sum(round(ch['size'], 1) == 12 for p in pdf.pages for ch in p.chars if ch.get('text', '').isalpha()), 500)


class SeeStagingPublicationTests(TestCase):
    def test_additive_staging_release_scope_parity_and_replay_refusal(self):
        from courses.management.commands.stage_authored_review import snapshot
        from courses.authored_review import course_values, lesson_text
        from courses.content_storage import canonical_storage_url
        school = School.objects.create(name='SEE', code='SEE', target_course_count=6, enrollment_open=False)
        original_school = School.objects.create(name='Retained', code='FSW', target_course_count=8, enrollment_open=False)
        c = Course.objects.create(school=original_school, course_code='SWP-001', title='Protected original', content='Protected teaching', paralearn_assessment_id='fixture-cbt-001')
        CourseModule.objects.create(course=c, order=1, title='Original module', content='Protected module')
        before = snapshot()
        with TemporaryDirectory() as tmp:
            receipt = Path(tmp) / 'stage.json'
            call_command('stage_authored_review', package=BATCH / 'review_package.json', commit=True, receipt=receipt, stdout=io.StringIO())
            self.assertEqual(before, read(receipt.with_suffix('.applied.json'))['after'])
            with self.assertRaises(CommandError): call_command('stage_authored_review', package=BATCH / 'review_package.json', commit=True, receipt=Path(tmp) / 'replay.json', stdout=io.StringIO())
        entries = load_entries(ROOT / 'production_courseware', 'see-2026-11-27')
        self.assertEqual(len(entries), 6)
        self.assertEqual({e['course']['code'] for e in entries}, {f'SWP-{n:03}' for n in range(78, 84)})
        for e in entries:
            c = Course.objects.get(course_code=e['course']['code'])
            for r in e['assets']:
                name = Path(r['path']).name; path = f'courses/{c.slug}/course/{name}'
                CourseAsset.objects.create(course=c, title=r['title'], asset_type=r['asset_type'], external_url=canonical_storage_url(path), storage_path=path, original_filename=name, version=r['version'], language=r['language'], content_type=r['content_type'], size_bytes=r['size_bytes'], status='in_review')
        cids, aids, _ = preflight(entries); lifecycle = lifecycle_state(cids, aids); protected = protected_snapshot(cids, aids)
        publish_atomically(cids, aids, lifecycle, protected)
        self.assertEqual(protected_snapshot(cids, aids), protected)
        self.assertEqual(Course.objects.filter(is_active=True).count(), 7)
        self.assertEqual(CourseAsset.objects.filter(status='published').count(), 24)
        self.assertEqual(Course.objects.exclude(pk__in=cids).exclude(paralearn_assessment_id__startswith='fixture-cbt-').count(), 0)
        self.assertFalse(Course.objects.filter(pk__in=cids).exclude(paralearn_assessment_id='').exists())
        school.refresh_from_db(); self.assertFalse(school.enrollment_open)
        self.assertEqual(school.courses.count(), 6)
        retained = Course.objects.get(course_code='SWP-001')
        self.assertEqual(retained.content, 'Protected teaching'); self.assertEqual(retained.paralearn_assessment_id, 'fixture-cbt-001')
        with self.assertRaises(CommandError): preflight(entries)

    def test_approval_for_another_release_cannot_publish_see(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(CommandError):
                call_command('publish_approved_materials', release='see-2026-11-27', approval=ROOT / 'production_courseware/releases/2026-11-19/owner_approval.json', receipt=Path(tmp) / 'wrong.json', commit=True, stdout=io.StringIO())
