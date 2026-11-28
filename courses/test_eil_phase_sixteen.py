"""Check EIL's new release scope and the retained course at publication."""
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase

from courses.content_storage import canonical_storage_url
from courses.material_publication import (
    lifecycle_state, load_entries, preflight, protected_snapshot, publish_atomically,
)
from courses.models import Course, CourseAsset
from schools.exam_blueprints import validate_blueprint
from schools.models import School

ROOT = Path(__file__).resolve().parents[1] / 'production_courseware'


class EilReleaseTests(TestCase):
    def test_release_scope_preserves_retained_course(self):
        school = School.objects.create(
            name='Eile Economy', code='EIL', target_course_count=8, enrollment_open=False,
        )
        existing_school = School.objects.create(name='Digital Innovation', code='DAI', enrollment_open=False)
        retained = Course.objects.create(
            school=existing_school, course_code='SWP-031', title='Digital Social Work Practice',
            content='Existing instruction', is_active=True, paralearn_assessment_id='fixture-cbt-031',
        )
        entries = load_entries(ROOT, 'eil-2026-11-28')
        new_codes = {f'SWP-{number:03}' for number in range(97, 105)}
        self.assertEqual({entry['course']['code'] for entry in entries}, new_codes)
        with TemporaryDirectory() as folder:
            call_command(
                'stage_authored_review',
                package=ROOT / 'phase_sixteen/eil_batch_01/review_package.json',
                receipt=Path(folder) / 'courses.json', commit=True, stdout=io.StringIO(),
            )

        for entry in entries:
            course = school.courses.get(course_code=entry['course']['code'])
            for row in entry['assets']:
                name = Path(row['path']).name
                path = f'courses/{course.slug}/course/{name}'
                CourseAsset.objects.create(
                    course=course, title=row['title'], asset_type=row['asset_type'],
                    external_url=canonical_storage_url(path), storage_path=path, original_filename=name,
                    version=row['version'], language=row['language'], content_type=row['content_type'],
                    size_bytes=row['size_bytes'], status='in_review',
                )

        course_ids, asset_ids, _ = preflight(entries)
        self.assertNotIn(retained.pk, course_ids)
        before = lifecycle_state(course_ids, asset_ids)
        protected = protected_snapshot(course_ids, asset_ids)
        publish_atomically(course_ids, asset_ids, before, protected)

        self.assertEqual(protected_snapshot(course_ids, asset_ids), protected)
        self.assertEqual(school.courses.filter(is_active=True).count(), 8)
        self.assertEqual(CourseAsset.objects.filter(status='published').count(), 32)
        retained.refresh_from_db()
        self.assertEqual(retained.content, 'Existing instruction')
        self.assertEqual(retained.paralearn_assessment_id, 'fixture-cbt-031')
        self.assertFalse(Course.objects.filter(pk__in=course_ids).exclude(paralearn_assessment_id='').exists())

        blueprint = json.loads(
            (ROOT / 'phase_sixteen/eil_batch_01/school_exam_blueprint.json').read_text(encoding='utf-8')
        )
        self.assertEqual(set(blueprint['required_courses']), new_codes)
        self.assertFalse(validate_blueprint(blueprint)['ready_for_launch'])
        self.assertTrue(all(set(i['course_codes']) == set(blueprint['required_courses'])
                            for i in blueprint['items'] if i['type'] == 'ESSAY'))
