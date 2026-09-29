from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, CourseAsset, CourseModule
from learning.models import CourseEnrollment
from learning.services import enroll_in_course
from schools.models import School


class CourseDetailAccessTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Test School", slug="test-school")
        self.course = Course.objects.create(
            school=self.school,
            title="Intro to SWEEP",
            slug="intro-to-sweep",
            summary="A short summary for the course.",
            description="This is a longer course description intended to be visible before enrollment.",
            course_code="CS-101",
            learning_objectives="Learn the basics\nUnderstand the workflow",
            content="This is the full course content that should stay hidden until enrollment.",
        )

    def test_anonymous_user_sees_public_overview_but_not_learning_material(self):
        response = self.client.get(reverse("course_detail", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course Overview")
        self.assertContains(response, "This is a longer course description intended to be visible before enrollment.")
        self.assertContains(response, "CS-101")
        self.assertContains(response, "Learning objectives")
        self.assertNotContains(response, "This is the full course content that should stay hidden until enrollment.")

    def test_course_list_shows_enrolled_status_for_enrolled_courses(self):
        user = get_user_model().objects.create_user(username="student", password="secret123")
        CourseEnrollment.objects.create(user=user, course=self.course)

        self.client.force_login(user)
        response = self.client.get(reverse("course_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enrolled")

    def test_enrollment_redirects_to_the_first_module(self):
        user = get_user_model().objects.create_user(username="student2", password="secret123")
        CourseModule.objects.create(
            course=self.course,
            title="Welcome",
            order=1,
            duration="15 min",
            module_type="video",
            learning_mode="self_paced",
            overview="Intro overview",
            content="Intro content",
            module_summary="Intro summary",
            knowledge_check="What did you learn?",
            practical_activity="Reflect on your learning.",
        )

        self.client.force_login(user)
        response = self.client.post(reverse("enroll_in_course", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("course_module_detail", kwargs={"slug": self.course.slug, "module_order": 1}))

    def test_authenticated_user_can_enroll_and_start_course(self):
        user = get_user_model().objects.create_user(username="student3", password="secret123")
        CourseModule.objects.create(
            course=self.course,
            title="Welcome",
            order=1,
            duration="15 min",
            module_type="article",
            learning_mode="self_paced",
            overview="Intro overview",
            content="Intro content",
            module_summary="Intro summary",
            knowledge_check="What did you learn?",
            practical_activity="Reflect on your learning.",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("course_detail", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enroll and start course")
        self.assertNotContains(response, "Continue course")

    def test_module_content_is_sanitized_before_rendering(self):
        user = get_user_model().objects.create_user(username="student4", password="secret123")
        module = CourseModule.objects.create(
            course=self.course,
            title="Safe lesson",
            order=1,
            content="# Lesson\n<script>alert('unsafe')</script>\nSafe paragraph.",
        )
        enroll_in_course(user, self.course)
        self.client.force_login(user)

        response = self.client.get(
            reverse("course_module_detail", kwargs={"slug": self.course.slug, "module_order": module.order})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Safe paragraph.")
        self.assertNotIn("<script", str(response.context["module_content_html"]))


class ContentWorkflowApiTests(TestCase):
    def setUp(self):
        school = School.objects.create(name="Content School", slug="content-school")
        self.course = Course.objects.create(school=school, title="Content Course", slug="content-course")
        self.module = CourseModule.objects.create(course=self.course, title="Content lesson", order=1)
        self.user = get_user_model().objects.create_superuser(
            username="content-admin", password="secret123", email="admin@example.com"
        )
        self.client.force_login(self.user)

    def test_staff_can_create_and_publish_an_external_asset(self):
        payload = {
            "course_slug": self.course.slug,
            "module_order": self.module.order,
            "title": "Learner guide",
            "asset_type": "learner_guide",
            "external_url": "https://assets.example.test/guide.pdf",
        }
        response = self.client.post(reverse("create_course_asset"), data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        asset = CourseAsset.objects.get(title="Learner guide")
        self.assertEqual(asset.status, CourseAsset.PublicationStatus.DRAFT)

        for action in ("submit", "approve", "publish"):
            response = self.client.post(reverse("transition_course_asset", kwargs={"asset_id": asset.id, "action": action}))
            self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, CourseAsset.PublicationStatus.PUBLISHED)
        self.assertEqual(asset.published_by, self.user)

    def test_non_staff_cannot_register_content(self):
        learner = get_user_model().objects.create_user(username="learner", password="secret123")
        self.client.force_login(learner)
        response = self.client.post(reverse("create_course_asset"), data={}, content_type="application/json")
        self.assertEqual(response.status_code, 403)
