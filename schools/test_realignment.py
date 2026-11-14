import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, CourseModule
from credentials.models import Badge, Certificate
from credentials.services import award_certificate
from learning.models import SchoolEnrollment, CourseProgress
from learning.services import enroll_in_school, grade_school_exam
from schools.catalogue import refactor_manifest
from schools.management.commands.realign_schools import fingerprints
from schools.models import School, SchoolExamQuestion


class SchoolRealignmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for row in refactor_manifest()["courses"]:
            school, _ = School.objects.get_or_create(name=row["old_school"])
            course = Course.objects.create(school=school, course_code=row["code"], title=row["title"],
                content="Preserved original course material", passing_score=70,
                paralearn_assessment_id="unchanged-exam-" + row["code"])
            CourseModule.objects.create(course=course, title="Preserved module", order=1, content="Original text")
        cls.user = get_user_model().objects.create_user(username="existing-learner")
        cls.old_school = School.objects.get(name="School of Community & Macro Practice")
        cls.enrollment, _ = enroll_in_school(cls.user, cls.old_school)
        cls.required_ids = set(cls.enrollment.curriculum_requirements.values_list("course_id", flat=True))
        Badge.objects.create(user=cls.user, course=Course.objects.get(course_code="SWP-013"))
        Certificate.objects.create(user=cls.user, school=cls.old_school)
        SchoolExamQuestion.objects.create(school=cls.old_school, text="Original exam", order=1)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.receipt = Path(self.temp.name) / "run.json"
        self.applied = Path(self.temp.name) / "run.applied.json"

    def run_move(self):
        call_command("realign_schools", commit=True, receipt=self.receipt, stdout=io.StringIO())

    def test_dry_run_is_read_only(self):
        before = fingerprints()
        call_command("realign_schools", stdout=io.StringIO())
        self.assertEqual(School.objects.count(), 10)
        self.assertEqual(before, fingerprints())

    def test_apply_verify_repeat_rollback_preserve_content_assessments_and_learners(self):
        before = fingerprints()
        original = dict(Course.objects.values_list("id", "school_id"))
        self.run_move()
        self.assertEqual(School.objects.filter(is_active=True).count(), 25)
        self.assertEqual(School.objects.filter(is_historical=True).count(), 10)
        self.assertEqual(before, fingerprints())
        for row in refactor_manifest()["courses"]:
            self.assertEqual(Course.objects.get(course_code=row["code"]).school.code, row["new_school"])
        self.assertFalse(School.objects.filter(code__isnull=False, enrollment_open=True).exists())
        call_command("realign_schools", verify=self.applied, stdout=io.StringIO())
        self.run_move()  # Must not overwrite the first receipt or duplicate anything.
        self.assertEqual(School.objects.count(), 35)
        call_command("realign_schools", rollback=self.applied, commit=True, stdout=io.StringIO())
        self.assertEqual(dict(Course.objects.values_list("id", "school_id")), original)
        self.assertEqual(School.objects.filter(is_active=True).count(), 10)
        self.assertEqual(before, fingerprints())

    def test_realignment_drift_is_rejected_before_any_write(self):
        Course.objects.filter(course_code="SWP-031").update(title="Unexpected title")
        with self.assertRaisesMessage(CommandError, "title drift"):
            self.run_move()
        self.assertEqual(School.objects.count(), 10)
        self.assertFalse(self.receipt.exists())

    def test_parity_failure_rolls_back_the_transaction(self):
        before = fingerprints()
        with patch("schools.management.commands.realign_schools.fingerprints", side_effect=[before, {}]):
            with self.assertRaisesMessage(CommandError, "Parity verification failed"):
                self.run_move()
        self.assertEqual(School.objects.count(), 10)
        self.assertEqual(before, fingerprints())

    def test_legacy_learner_keeps_all_frozen_courses_and_original_exam(self):
        self.run_move()
        self.client.force_login(self.user)
        response = self.client.get(self.old_school.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual({c.id for c in response.context["courses"]}, self.required_ids)
        self.assertContains(response, "Your progress: 0 / 6")
        CourseProgress.objects.filter(user=self.user).update(status="completed")
        response = self.client.get(reverse("school_exam", kwargs={"slug": self.old_school.slug}))
        self.assertContains(response, "Original exam")
        self.client.logout()
        response = self.client.get(self.old_school.get_absolute_url())
        self.assertContains(response, "School catalogue update")
        self.assertContains(response, "PCEI")
        self.assertContains(response, "DAI")

    def test_repeat_enrollment_does_not_expand_snapshot(self):
        Course.objects.create(school=self.old_school, title="Added later")
        _, created = enroll_in_school(self.user, self.old_school)
        self.assertFalse(created)
        self.assertEqual(set(self.enrollment.curriculum_requirements.values_list("course_id", flat=True)), self.required_ids)

    def test_planned_schools_cannot_enroll_or_issue_local_certificates(self):
        self.run_move()
        school = School.objects.get(code="MHP")
        with self.assertRaises(PermissionError):
            enroll_in_school(self.user, school)
        with self.assertRaises(PermissionError):
            grade_school_exam(self.user, school, {})
        with self.assertRaises(ValueError):
            award_certificate(self.user, school)
        self.client.force_login(self.user)
        self.assertContains(self.client.get(school.get_absolute_url()), "School pathway in development")
        self.client.post(reverse("enroll_in_school", kwargs={"slug": school.slug}))
        self.assertFalse(SchoolEnrollment.objects.filter(user=self.user, school=school).exists())
        self.assertContains(self.client.get(reverse("school_list"), {"q": "SPIA"}), "Petroleum Industry Act")

    def test_legacy_seed_and_sync_cannot_overwrite_realigned_courses(self):
        self.run_move()
        before = fingerprints()
        with self.assertRaises(CommandError):
            call_command("seed_data", stdout=io.StringIO())
        with self.assertRaises(CommandError):
            call_command("sync_approved_catalogue", commit=True, catalogue="unused.json", exam_bank="unused.json", stdout=io.StringIO())
        self.assertEqual(before, fingerprints())

    def test_rollback_refuses_changed_protected_data(self):
        self.run_move()
        CourseProgress.objects.filter(user=self.user).update(status="completed")
        with self.assertRaisesMessage(CommandError, "Protected data has changed"):
            call_command("realign_schools", rollback=self.applied, commit=True, stdout=io.StringIO())
        self.assertEqual(School.objects.filter(is_active=True).count(), 25)
