import hashlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.management.commands.publish_verified_expansion import current_state, publish_atomically
from courses.models import Course, CourseAsset, CourseModule
from courses import test_staged_expansion_revision as fixtures


class ExpansionPublicationTests(TestCase):
    setUp = fixtures.StagedRevisionTests.setUp

    def test_publish_changes_existing_rows_only(self):
        before = current_state()
        after = publish_atomically(before)
        self.assertEqual(Course.objects.filter(is_active=True).count(), 4)
        self.assertEqual(CourseAsset.objects.filter(status='published', published_at__isnull=False).count(), 32)
        self.assertEqual([a['id'] for a in before['assets']], [a['id'] for a in after['assets']])
        self.assertEqual(before['modules'], after['modules'])

    def test_stale_asset_blocks_every_change(self):
        before = current_state()
        CourseAsset.objects.filter(pk=before['assets'][0]['id']).update(version='changed')
        with self.assertRaises(CommandError):
            publish_atomically(before)
        self.assertFalse(Course.objects.filter(is_active=True).exists())
        self.assertFalse(CourseAsset.objects.filter(status='published').exists())

    def test_changed_assessment_mapping_blocks_publication(self):
        before = current_state()
        Course.objects.filter(course_code='SWP-031').update(paralearn_assessment_id='other-exam')
        with self.assertRaises(CommandError):
            publish_atomically(before)
        self.assertFalse(CourseAsset.objects.filter(status='published').exists())

    def test_changed_module_blocks_publication(self):
        before = current_state()
        CourseModule.objects.filter(pk=before['modules'][0]['id']).update(content='changed')
        with self.assertRaises(CommandError):
            publish_atomically(before)

    def test_activation_failure_rolls_back_asset_publication(self):
        before = current_state()
        from django.db.models.query import QuerySet
        original_update = QuerySet.update
        def fail_course_update(queryset, **kwargs):
            if queryset.model is Course and kwargs.get('is_active'):
                raise RuntimeError('Synthetic transaction interruption')
            return original_update(queryset, **kwargs)
        with patch.object(QuerySet, 'update', fail_course_update):
            with self.assertRaises(RuntimeError):
                publish_atomically(before)
        self.assertEqual(current_state(), before)

    def test_committed_repeat_is_noop(self):
        release = Path(__file__).resolve().parents[1] / 'production_courseware/drafts/expansion-evidence-2026-10-17'
        state = publish_atomically(current_state())
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / 'publication.json'
            journal.write_text(json.dumps({'manifest_sha256':hashlib.sha256((release/'upload_manifest.json').read_bytes()).hexdigest(),
                                           'committed':True, 'after':state}))
            output = io.StringIO()
            call_command('publish_verified_expansion', release=release, revision_journal=Path(directory)/'unused.json',
                         journal=journal, qa_user='synthetic', commit=True, stdout=output)
            self.assertIn('Already published; unchanged', output.getvalue())
            self.assertEqual(current_state(), state)
