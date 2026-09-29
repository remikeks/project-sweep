from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from courses.models import Course
from learning.services import enroll_in_course
from schools.models import School

from . import services


class GeminiConfigTests(SimpleTestCase):
    @override_settings(GEMINI_API_KEY="gemini-key", GOOGLE_API_KEY=None)
    def test_get_api_key_prefers_gemini_setting(self):
        with patch.dict("os.environ", {}, clear=False):
            self.assertEqual(services._get_api_key(), "gemini-key")

    @override_settings(GEMINI_API_KEY=None, GOOGLE_API_KEY="google-key")
    def test_get_api_key_falls_back_to_google_setting(self):
        with patch.dict("os.environ", {}, clear=False):
            self.assertEqual(services._get_api_key(), "google-key")

    @override_settings(GEMINI_API_KEY=None, GOOGLE_API_KEY=None)
    def test_get_api_key_raises_when_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(services.TutorNotConfigured):
                services._get_api_key()


class TutorAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="learner", password="secret123")
        school = School.objects.create(name="Tutor Test School", slug="tutor-test-school")
        self.course = Course.objects.create(
            school=school,
            title="Tutor Test Course",
            slug="tutor-test-course",
            content="Learner-visible source material.",
        )
        self.client.force_login(self.user)

    def test_tutor_rejects_a_user_who_is_not_enrolled(self):
        response = self.client.post(
            reverse("tutor_ask"),
            data='{"course_slug": "tutor-test-course", "mode": "summary"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_course_context_includes_legacy_course_content(self):
        enroll_in_course(self.user, self.course)
        self.assertIn("Learner-visible source material.", services._course_context(self.course))
