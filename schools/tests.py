from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course
from learning.services import enroll_in_school
from schools.models import School

User = get_user_model()


class SchoolViewsTests(TestCase):
    def setUp(self):
        self.active_school = School.objects.create(
            name="Active Health School",
            slug="active-health-school",
            tagline="Clinical excellence in healthcare",
            is_active=True,
        )
        self.inactive_school = School.objects.create(
            name="Inactive Archive School",
            slug="inactive-archive-school",
            tagline="Old archive",
            is_active=False,
        )
        self.course = Course.objects.create(
            school=self.active_school,
            title="Hospital Discharge Planning",
            slug="hospital-discharge-planning",
            is_active=True,
        )

    def test_school_list_only_shows_active_schools(self):
        response = self.client.get(reverse("school_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Health School")
        self.assertNotContains(response, "Inactive Archive School")

    def test_school_list_search_query(self):
        response = self.client.get(reverse("school_list"), {"q": "Healthcare"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Health School")

        empty_search = self.client.get(reverse("school_list"), {"q": "NonExistentKeyword"})
        self.assertEqual(empty_search.status_code, 200)
        self.assertNotContains(empty_search, "Active Health School")

    def test_school_detail_view(self):
        response = self.client.get(reverse("school_detail", kwargs={"slug": self.active_school.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Health School")
        self.assertContains(response, "Hospital Discharge Planning")

    def test_school_detail_404_for_inactive_school(self):
        response = self.client.get(reverse("school_detail", kwargs={"slug": self.inactive_school.slug}))
        self.assertEqual(response.status_code, 404)

    def test_school_list_authenticated_enrollment_flags(self):
        user = User.objects.create_user(username="student", password="testpass123")
        enroll_in_school(user, self.active_school)
        self.client.force_login(user)

        response = self.client.get(reverse("school_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.active_school.id, response.context["enrolled_school_ids"])
