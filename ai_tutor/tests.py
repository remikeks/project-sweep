import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from courses.models import Course, CourseModule
from learning.services import enroll_in_course
from schools.models import School

from . import services
from .models import TutorInteraction


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

    def test_course_context_uses_stable_source_labels(self):
        context = services._course_context(self.course)

        self.assertIn("### Source: Course learning material", context)
        self.assertEqual(services._source_labels(context), ("Course learning material",))

    @patch("ai_tutor.services._call_gemini")
    def test_unsourced_model_answer_is_replaced_with_a_grounded_refusal(self, call_gemini):
        enroll_in_course(self.user, self.course)
        call_gemini.return_value = "A made-up answer.\nSources: [External website]"

        answer = services.ask_course_question(self.user, self.course, "What should I do?")

        self.assertEqual(answer, services.GROUNDING_REFUSAL)
        self.assertEqual(TutorInteraction.objects.get().answer, services.GROUNDING_REFUSAL)
        self.assertIn("Available source labels: [Course learning material]", call_gemini.call_args.args[0])

    @patch("ai_tutor.services._call_gemini")
    def test_supported_answer_keeps_an_available_source_citation(self, call_gemini):
        enroll_in_course(self.user, self.course)
        call_gemini.return_value = (
            "The material says to use the learner-visible source material.\n"
            "Sources: [Course learning material]"
        )

        answer = services.ask_course_question(self.user, self.course, "What does the material say?")

        self.assertIn("Sources: [Course learning material]", answer)

    @patch("ai_tutor.services._call_gemini")
    def test_tutor_rejects_an_oversized_question_before_provider_call(self, call_gemini):
        enroll_in_course(self.user, self.course)

        response = self.client.post(
            reverse("tutor_ask"),
            data=json.dumps(
                {
                    "course_slug": self.course.slug,
                    "mode": "chat",
                    "question": "x" * (services.MAX_QUESTION_CHARS + 1),
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("characters or fewer", response.json()["error"])
        call_gemini.assert_not_called()

    def test_module_context_has_no_answerable_source_when_module_is_empty(self):
        module = CourseModule.objects.create(course=self.course, title="Empty module", order=1)

        self.assertEqual(services._module_context(module), "")
