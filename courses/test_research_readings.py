from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from courses.models import Course, CourseModule
from courses.research_readings import reading_catalogue, reading_for_module
from learning.services import enroll_in_course
from schools.models import School


class ResearchReadingContentTests(SimpleTestCase):
    def test_six_unique_original_course_readings_with_provenance_and_limits(self):
        readings = reading_catalogue()["readings"]
        self.assertEqual(set(readings), {"SWP-003", "SWP-008", "SWP-013", "SWP-020", "SWP-023", "SWP-026"})
        self.assertEqual(len({r['doi'] for r in readings.values()}), 6)
        for item in readings.values():
            for field in ['citation', 'evidence', 'limits', 'activity', 'reflection', 'verified_on']:
                self.assertTrue(item[field])
            self.assertTrue(item['doi'].startswith('10.'))
            self.assertTrue(item['openalex_url'].startswith('https://openalex.org/W'))
            self.assertTrue(not item['doaj_url'] or item['doaj_url'].startswith('https://doaj.org/article/'))

    def test_reading_appears_only_once_in_selected_course(self):
        self.assertIsNotNone(reading_for_module('SWP-008', 1))
        self.assertIsNone(reading_for_module('SWP-008', 2))
        self.assertIsNone(reading_for_module('SWP-031', 1))


class ResearchReadingAccessTests(TestCase):
    def setUp(self):
        school = School.objects.create(name='Research test school', slug='research-test-school')
        self.course = Course.objects.create(school=school, title='Motivational Interviewing', slug='mi-test', course_code='SWP-008')
        self.module = CourseModule.objects.create(course=self.course, title='Introduction', order=1, content='Existing lesson remains intact.')
        self.url = reverse('course_module_detail', kwargs={'slug':self.course.slug, 'module_order':1})
        self.user = get_user_model().objects.create_user(username='reading-test', password='test-only-password')

    def test_enrolled_learner_sees_bounded_supplement_without_record_changes(self):
        enroll_in_course(self.user, self.course)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, 'Optional research reading')
        self.assertContains(response, 'Existing lesson remains intact.')
        self.assertContains(response, 'Evidence limits')
        self.assertContains(response, 'https://doi.org/10.1371/journal.pone.0204890')
        self.assertContains(response, 'does not change the downloadable course pack')
        self.assertEqual(self.course.modules.count(), 1)
        self.assertEqual(self.course.assets.count(), 0)
        self.assertEqual(self.user.course_assessment_attempts.count(), 0)

    def test_anonymous_visitor_does_not_see_enrolled_reading(self):
        self.assertNotContains(self.client.get(self.url), 'Optional research reading')

    def test_unenrolled_user_is_redirected(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(self.url), reverse('course_detail', kwargs={'slug':self.course.slug}))
