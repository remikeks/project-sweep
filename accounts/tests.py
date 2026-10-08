from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class AccountsAuthTests(TestCase):
    def test_signup_page_renders_successfully(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create your account")

    def test_authenticated_user_redirected_from_signup(self):
        user = User.objects.create_user(username="existing", password="password123")
        self.client.force_login(user)
        response = self.client.get(reverse("signup"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("signup"),
            data={
                "username": "newlearner",
                "email": "learner@example.org",
                "first_name": "Jane",
                "last_name": "Doe",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.filter(username="newlearner").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "learner@example.org")
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Doe")

    def test_signup_fails_on_password_mismatch(self):
        response = self.client.post(
            reverse("signup"),
            data={
                "username": "mismatchuser",
                "email": "mismatch@example.org",
                "password1": "SecurePass123!",
                "password2": "DifferentPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatchuser").exists())

    def test_login_and_logout_flow(self):
        user = User.objects.create_user(username="loginuser", password="ValidPass123!")
        login_resp = self.client.post(
            reverse("login"),
            data={"username": "loginuser", "password": "ValidPass123!"},
        )
        self.assertRedirects(login_resp, reverse("dashboard"))

        logout_resp = self.client.post(reverse("logout"))
        self.assertRedirects(logout_resp, reverse("home"))

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset your password")

    def test_password_reset_flow(self):
        User.objects.create_user(username="resetuser", email="reset@example.org", password="OldPassword123!")
        response = self.client.post(reverse("password_reset"), data={"email": "reset@example.org"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password reset", mail.outbox[0].subject)

    @override_settings(ACCOUNT_EMAIL_VERIFICATION_REQUIRED=True)
    def test_email_verification_required_flow(self):
        response = self.client.post(
            reverse("signup"),
            data={
                "username": "unverified",
                "email": "unverified@example.org",
                "first_name": "Unverified",
                "last_name": "Learner",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verify your email address")
        user = User.objects.get(username="unverified")
        self.assertFalse(user.is_active)

        # Activate using token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activate_url = reverse("activate_account", kwargs={"uidb64": uid, "token": token})

        activate_resp = self.client.get(activate_url)
        self.assertRedirects(activate_resp, reverse("dashboard"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_invalid_activation_token(self):
        user = User.objects.create_user(username="badtokenuser", email="bad@example.org", is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_url = reverse("activate_account", kwargs={"uidb64": uid, "token": "invalid-token-123"})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Activation link invalid or expired", status_code=400)
