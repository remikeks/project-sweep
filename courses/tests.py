from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, CourseModule
from learning.models import CourseEnrollment
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

    def test_anonymous_user_sees_content_summary_instead_of_full_content(self):
        response = self.client.get(reverse("course_detail", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Content summary")
        self.assertContains(response, "Enroll to unlock the full course content")
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

    def test_authenticated_user_sees_single_start_course_button(self):
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
        self.assertContains(response, "Start course")
        self.assertNotContains(response, "Go to course")
        self.assertNotContains(response, "Enroll and Start Course")
