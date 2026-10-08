import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from feedback.models import Feedback

User = get_user_model()


class FeedbackEndpointTests(TestCase):
    def test_submit_valid_feedback_anonymously(self):
        payload = {
            "feedback_type": "suggestion",
            "message": "It would be great to have offline reading packs.",
            "email": "visitor@example.com",
            "page_url": "https://sweepacademy.org/courses/",
        }
        response = self.client.post(
            reverse("submit_feedback"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})

        feedback = Feedback.objects.first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.feedback_type, "suggestion")
        self.assertEqual(feedback.message, "It would be great to have offline reading packs.")
        self.assertEqual(feedback.email, "visitor@example.com")
        self.assertIsNone(feedback.user)

    def test_submit_feedback_authenticated(self):
        user = User.objects.create_user(username="learner1", password="testpass123")
        self.client.force_login(user)

        payload = {
            "feedback_type": "bug",
            "message": "Audio lecture is missing in module 2.",
        }
        response = self.client.post(
            reverse("submit_feedback"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.user, user)

    def test_submit_feedback_invalid_type(self):
        payload = {
            "feedback_type": "invalid_type_here",
            "message": "Testing",
        }
        response = self.client.post(
            reverse("submit_feedback"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_submit_feedback_empty_message(self):
        payload = {
            "feedback_type": "suggestion",
            "message": "   ",
        }
        response = self.client.post(
            reverse("submit_feedback"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_get_not_allowed(self):
        response = self.client.get(reverse("submit_feedback"))
        self.assertEqual(response.status_code, 405)
