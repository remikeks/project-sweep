from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course
from credentials.models import Badge, Certificate
from credentials.services import revoke_credential
from schools.models import School

User = get_user_model()


class CredentialsViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="certified_learner",
            password="testpass123",
            first_name="Jane",
            last_name="Scholar",
        )
        self.other_user = User.objects.create_user(
            username="other_learner",
            password="testpass123",
        )
        self.school = School.objects.create(name="School of Community Practice", slug="school-of-community-practice")
        self.course = Course.objects.create(
            school=self.school,
            title="Community Needs Assessment",
            slug="community-needs-assessment",
            is_active=True,
        )
        self.badge = Badge.objects.create(
            user=self.user,
            course=self.course,
            issued_to_name="Jane Scholar",
            credential_title="Community Needs Assessment completion badge",
            status="active",
        )
        self.certificate = Certificate.objects.create(
            user=self.user,
            school=self.school,
            issued_to_name="Jane Scholar",
            credential_title="School of Community Practice certificate of completion",
            status="active",
        )

    def test_my_credentials_requires_login(self):
        response = self.client.get(reverse("my_credentials"))
        self.assertEqual(response.status_code, 302)

    def test_my_credentials_displays_user_awards(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("my_credentials"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Community Needs Assessment")
        self.assertContains(response, "School of Community Practice")

    def test_public_verification_active_credential(self):
        response = self.client.get(reverse("verify_credential", kwargs={"uid": self.badge.uid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credential verified")
        self.assertContains(response, "Jane Scholar")

    def test_public_verification_revoked_credential(self):
        revoke_credential(self.badge, reason="Testing revocation")
        response = self.client.get(reverse("verify_credential", kwargs={"uid": self.badge.uid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credential is not active")

    def test_public_verification_unknown_uid_returns_404(self):
        import uuid
        response = self.client.get(reverse("verify_credential", kwargs={"uid": uuid.uuid4()}))
        self.assertEqual(response.status_code, 404)

    def test_badge_png_and_pdf_generation(self):
        self.client.force_login(self.user)
        png_resp = self.client.get(reverse("badge_png", kwargs={"uid": self.badge.uid}))
        self.assertEqual(png_resp.status_code, 200)
        self.assertEqual(png_resp["Content-Type"], "image/png")

        pdf_resp = self.client.get(reverse("badge_pdf", kwargs={"uid": self.badge.uid}))
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp["Content-Type"], "application/pdf")

    def test_other_user_cannot_download_badge_artwork(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse("badge_png", kwargs={"uid": self.badge.uid}))
        self.assertEqual(response.status_code, 404)
