from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, CourseModule
from credentials.models import Badge
from credentials.services import revoke_credential
from schools.models import School

from .models import CourseProgress, SchoolCurriculumRequirement
from .services import complete_module, enroll_in_course, enroll_in_school, school_completion_status


class PhaseFourLearningTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="learner", password="test-pass-123")
        self.school = School.objects.create(name="Curriculum School")
        self.first = Course.objects.create(school=self.school, title="First", order=1)
        self.second = Course.objects.create(school=self.school, title="Second", order=2)

    def test_school_curriculum_is_frozen_at_enrollment(self):
        enrollment, _ = enroll_in_school(self.user, self.school)
        later = Course.objects.create(school=self.school, title="Later", order=3)
        required = set(enrollment.curriculum_requirements.values_list("course_id", flat=True))
        self.assertEqual(required, {self.first.id, self.second.id})
        self.assertNotIn(later.id, required)

    def test_modules_complete_only_in_order(self):
        one = CourseModule.objects.create(course=self.first, title="One", order=1)
        two = CourseModule.objects.create(course=self.first, title="Two", order=2)
        enroll_in_course(self.user, self.first)
        with self.assertRaisesMessage(ValueError, "previous module"):
            complete_module(user=self.user, module=two)
        complete_module(user=self.user, module=one)
        _, created = complete_module(user=self.user, module=two)
        self.assertTrue(created)

    def test_verification_reports_revoked_badge_without_login(self):
        badge = Badge.objects.create(user=self.user, course=self.first, issued_to_name="Learner", credential_title="First completion badge")
        response = self.client.get(reverse("verify_credential", kwargs={"uid": badge.uid}))
        self.assertContains(response, "Credential verified")
        revoke_credential(badge, reason="Administrative correction")
        response = self.client.get(reverse("verify_credential", kwargs={"uid": badge.uid}))
        self.assertContains(response, "Credential is not active")

    def test_completion_status_uses_requirements_not_current_catalog(self):
        enrollment, _ = enroll_in_school(self.user, self.school)
        Course.objects.create(school=self.school, title="Later", order=3)
        for course in (self.first, self.second):
            CourseProgress.objects.filter(user=self.user, course=course).update(status="completed")
        completed, total, is_complete = school_completion_status(self.user, self.school)
        self.assertEqual((completed, total, is_complete), (2, 2, True))
