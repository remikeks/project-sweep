from django.test import TestCase
from django.urls import reverse

from core.models import Resource, TeamMember
from courses.models import Course
from schools.models import School


class CoreViewsTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="School of Practice", slug="school-of-practice")
        self.course = Course.objects.create(
            school=self.school,
            title="Practice Fundamentals",
            slug="practice-fundamentals",
            is_active=True,
        )
        self.member = TeamMember.objects.create(
            name="Dr. Jane Social",
            role="Dean of Social Work",
            bio="Leading education researcher",
            is_active=True,
        )
        self.resource = Resource.objects.create(
            title="Child Welfare Toolkit",
            caption="Essential guide for field workers",
            description="Practical toolkit for case workers",
            is_active=True,
        )

    def test_home_page_renders_with_counts(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SWEEP Academy")
        self.assertEqual(response.context["stats"]["school_count"], 1)
        self.assertEqual(response.context["stats"]["course_count"], 1)

    def test_about_page_renders(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About")

    def test_services_page_renders_service_groups(self):
        response = self.client.get(reverse("services"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Education and Professional Development")
        self.assertGreater(response.context["total_services"], 0)

    def test_team_page_renders_active_members(self):
        response = self.client.get(reverse("team"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Jane Social")
        self.assertContains(response, "Dean of Social Work")

    def test_resources_page_renders_active_resources(self):
        response = self.client.get(reverse("resources"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Child Welfare Toolkit")
