import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.authored_review import validate_package
from courses.models import Course
from schools.models import School

PACKAGE = Path(__file__).resolve().parents[1] / "production_courseware/phase_two/fsw_batch_01/review_package.json"


class AuthoredReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school = School.objects.create(name="Foundational review", code="FSW", enrollment_open=False)
        cls.existing = Course.objects.create(school=cls.school,title="Retained course",course_code="SWP-016",
            content="Original protected teaching",paralearn_assessment_id="retained-exam")

    def setUp(self):
        self.package = json.loads(PACKAGE.read_text(encoding="utf-8"))

    def test_full_batch_validates_and_rejects_missing_evidence(self):
        self.assertEqual(validate_package(self.package),dict(courses=2,modules=6,questions=30))
        self.package["courses"][0]["modules"][0]["sources"].append("UNKNOWN")
        with self.assertRaisesRegex(ValueError,"Unknown module reference"):
            validate_package(self.package)

    def test_tampering_is_rejected(self):
        self.package["courses"][0]["modules"][0]["paragraphs"][0] += " Unreviewed change."
        with self.assertRaisesRegex(ValueError,"checksum mismatch"):
            validate_package(self.package)

    def test_staging_preserves_existing_and_cannot_overwrite_on_repeat(self):
        before = Course.objects.get(pk=self.existing.pk).__dict__.copy()
        before.pop("_state")
        with TemporaryDirectory() as temp:
            path = Path(temp)/"receipt.json"
            call_command("stage_authored_review",package=PACKAGE,commit=True,receipt=path,stdout=io.StringIO())
            result = json.loads(path.with_suffix(".applied.json").read_text())
            self.assertEqual(result["before"],result["after"])
            self.assertEqual(len(result["new_course_ids"]),2)
            for course in Course.objects.exclude(pk=self.existing.pk):
                self.assertFalse(course.is_active)
                self.assertEqual(course.paralearn_assessment_id,"")
                self.assertEqual(course.modules.count(),3)
                self.assertNotIn("is_correct",course.content)
                self.assertNotIn('"correct":',course.content)
            with self.assertRaisesRegex(CommandError,"already exists"):
                call_command("stage_authored_review",package=PACKAGE,commit=True,receipt=Path(temp)/"repeat.json",stdout=io.StringIO())
        after = Course.objects.get(pk=self.existing.pk).__dict__.copy()
        after.pop("_state")
        self.assertEqual(before,after)

    def test_global_collision_rolls_back_whole_batch(self):
        other = School.objects.create(name="Other school",code="ERT",enrollment_open=False)
        Course.objects.create(school=other,title="Different title",course_code="SWP-036")
        with TemporaryDirectory() as temp, self.assertRaisesRegex(CommandError,"identity already exists"):
            call_command("stage_authored_review",package=PACKAGE,commit=True,receipt=Path(temp)/"collision.json",stdout=io.StringIO())
        self.assertFalse(Course.objects.filter(course_code="SWP-035").exists())

    def test_closed_enrolment_and_receipt_required(self):
        self.school.enrollment_open=True
        self.school.save(update_fields=["enrollment_open"])
        with TemporaryDirectory() as temp, self.assertRaisesRegex(CommandError,"enrolment closed"):
            call_command("stage_authored_review",package=PACKAGE,commit=True,receipt=Path(temp)/"open.json",stdout=io.StringIO())
        with self.assertRaisesRegex(CommandError,"requires a new"):
            call_command("stage_authored_review",package=PACKAGE,commit=True,stdout=io.StringIO())

    def test_dry_run_is_read_only(self):
        call_command("stage_authored_review",package=PACKAGE,stdout=io.StringIO())
        self.assertEqual(Course.objects.count(),1)
