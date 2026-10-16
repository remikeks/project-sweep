from django.test import TestCase, override_settings
from django.urls import reverse

from core.legacy_catalogue import LEGACY_SCHOOL_REDIRECTS
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

    def test_foundation_orientation_is_hidden_until_curriculum_approval(self):
        response = self.client.get(reverse("foundation_orientation"))
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(self.client.get(reverse("home")), "Start Here")

    @override_settings(FOUNDATION_ORIENTATION_ENABLED=True)
    def test_foundation_orientation_is_shared_and_non_credit(self):
        response = self.client.get(reverse("foundation_orientation"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Foundations of Social Work")
        self.assertContains(response, "not an eleventh School or a catalogue course")
        self.assertContains(response, "No assessment")
        self.assertContains(self.client.get(reverse("home")), "Start Here")

    def test_render_archive_explains_historical_records(self):
        response = self.client.get(reverse("legacy_render_archive"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Earlier Render catalogue")
        self.assertContains(response, "Past completions")
        self.assertContains(response, "not automatically transferred")

    def test_retired_render_urls_redirect_without_creating_current_enrolments(self):
        for slug, destination in LEGACY_SCHOOL_REDIRECTS.items():
            with self.subTest(slug=slug):
                response = self.client.get(f"/schools/{slug}/")
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response["Location"], destination)

        for path in (
            "/courses/introduction-to-social-work/",
            "/courses/introduction-to-social-work/modules/1/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response["Location"], "/archive/render/")
