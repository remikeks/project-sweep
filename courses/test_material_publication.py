import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from schools.models import School
from .authored_review import course_values, lesson_text
from .content_storage import canonical_storage_url
from .material_publication import (
    load_entries, preflight, protected_snapshot, lifecycle_state,
    publish_atomically, verify_remote_resources,
)
from .models import Course, CourseAsset, CourseModule

ROOT = Path(__file__).resolve().parents[1]


class ApprovedMaterialPublicationTests(TestCase):
    def setUp(self):
        package = json.loads((ROOT/'production_courseware/phase_two/fsw_batch_01/review_package.json').read_text())
        source = package['courses'][0]
        rows = json.loads((ROOT/'production_courseware/phase_three/fsw_media_01/upload_manifest.json').read_text())
        self.entry = dict(course=source, references=package['references'], assets=[r for r in rows if r['course_code'] == source['code']])
        self.school = School.objects.create(code='FSW', name='Foundational practice', slug='release-foundational', enrollment_open=False)
        self.original = Course.objects.create(school=self.school, title='Original course', slug='original', course_code='SWP-001', content='Retained original teaching', paralearn_assessment_id='retained-cbt')
        self.course = Course.objects.create(school=self.school, **course_values(source, package['references']))
        for m in source['modules']:
            CourseModule.objects.create(course=self.course, order=m['order'], title=m['title'], overview=m['outcome'], content=lesson_text(m, package['references']), practical_activity=m['activity'])
        self.assets = []
        for row in self.entry['assets']:
            name = Path(row['path']).name
            storage_path = f"courses/{source['slug']}/course/{name}"
            self.assets.append(CourseAsset.objects.create(course=self.course, title=row['title'], asset_type=row['asset_type'],
                external_url=canonical_storage_url(storage_path), storage_path=storage_path, original_filename=name,
                version=row['version'], language=row['language'], content_type=row['content_type'], size_bytes=row['size_bytes'], status='in_review'))

    def state(self):
        cids, aids, resources = preflight([self.entry])
        return cids, aids, resources, lifecycle_state(cids, aids), protected_snapshot(cids, aids)

    def test_exact_all_eight_release_scope_has_31_courses_and_124_files(self):
        entries = load_entries(ROOT/'production_courseware')
        self.assertEqual(len(entries), 31)
        self.assertEqual(sum(len(e['assets']) for e in entries), 124)
        self.assertEqual({e['course']['code'] for e in entries}, {f'SWP-{n:03}' for n in range(35, 66)})

    def test_publication_preserves_all_teaching_cbts_schools_and_existing_records(self):
        cids, aids, resources, before, protected = self.state()
        publish_atomically(cids, aids, before, protected)
        self.assertEqual(protected_snapshot(cids, aids), protected)
        self.course.refresh_from_db(); self.original.refresh_from_db(); self.school.refresh_from_db()
        self.assertTrue(self.course.is_active)
        self.assertEqual(self.course.paralearn_assessment_id, '')
        self.assertEqual(self.original.paralearn_assessment_id, 'retained-cbt')
        self.assertFalse(self.school.enrollment_open)
        for asset in CourseAsset.objects.filter(pk__in=aids):
            self.assertEqual(asset.status, 'published')
            self.assertIsNotNone(asset.reviewed_at); self.assertIsNotNone(asset.published_at)
            self.assertIsNone(asset.reviewed_by_id); self.assertIsNone(asset.published_by_id)

    def test_remote_hash_mismatch_refuses_release(self):
        _, _, resources, before, _ = self.state()
        with patch('courses.material_publication.SupabaseStorageClient') as client, patch('courses.material_publication.ensure_private_bucket'), patch('courses.material_publication.urlopen', side_effect=lambda *a, **k: io.BytesIO(b'wrong bytes')):
            client.return_value.create_signed_download_url.return_value = 'https://supabase.local/signed'
            with self.assertRaises(CommandError):
                verify_remote_resources(resources)
        self.assertEqual(lifecycle_state({self.course.pk}, {a.pk for a in self.assets}), before)

    def test_lifecycle_drift_refuses_publication(self):
        cids, aids, _, before, protected = self.state()
        CourseAsset.objects.filter(pk=self.assets[0].pk).update(status='approved')
        with self.assertRaises(CommandError):
            publish_atomically(cids, aids, before, protected)
        self.course.refresh_from_db(); self.assertFalse(self.course.is_active)
        self.assertFalse(CourseAsset.objects.filter(status='published').exists())

    def test_protected_teaching_drift_refuses_publication(self):
        cids, aids, _, before, protected = self.state()
        Course.objects.filter(pk=self.original.pk).update(content='Concurrent change')
        with self.assertRaises(CommandError):
            publish_atomically(cids, aids, before, protected)
        self.assertEqual(lifecycle_state(cids, aids), before)

    def test_post_update_parity_failure_rolls_back_every_lifecycle_change(self):
        cids, aids, _, before, protected = self.state()
        with patch('courses.material_publication.protected_snapshot', side_effect=[protected, {'drift': True}]):
            with self.assertRaises(CommandError):
                publish_atomically(cids, aids, before, protected)
        self.assertEqual(lifecycle_state(cids, aids), before)

    def test_published_learning_page_and_real_enrolment_checked_download_contract(self):
        cids, aids, _, before, protected = self.state()
        publish_atomically(cids, aids, before, protected)
        response = self.client.get(self.course.get_absolute_url())
        self.assertContains(response, 'Learning materials approved')
        self.assertContains(response, 'original draft-edition labels')
        self.assertContains(response, 'course assessment and completion badge are not yet available')
        self.assertContains(response, 'Enroll to download', count=4)
        download = reverse('course_asset_download', args=[self.assets[0].pk])
        self.assertEqual(self.client.get(download).status_code, 302)
        learner = get_user_model().objects.create_user(username='publication-learner', password='isolated-test-only')
        self.client.force_login(learner)
        self.assertRedirects(self.client.get(download), self.course.get_absolute_url(), fetch_redirect_response=False)
        self.client.post(reverse('enroll_in_course', args=[self.course.slug]))
        with patch('courses.views.storage_is_configured', return_value=True), patch('courses.views.SupabaseStorageClient') as storage:
            storage.return_value.create_signed_download_url.return_value = 'https://supabase.local/temporary-resource'
            self.assertRedirects(self.client.get(download), 'https://supabase.local/temporary-resource', fetch_redirect_response=False)
            storage.return_value.create_signed_download_url.assert_called_once_with(self.assets[0].storage_path, download=True)
        self.assertEqual(learner.badges.count(), 0)

    def test_existing_journal_is_never_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory)/'publication.json'; receipt.write_text('{}')
            approval = ROOT/'production_courseware/releases/2026-11-19/owner_approval.json'
            with self.assertRaises(CommandError):
                call_command('publish_approved_materials', approval=approval, receipt=receipt, commit=True, stdout=io.StringIO())
        self.course.refresh_from_db(); self.assertFalse(self.course.is_active)
