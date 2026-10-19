from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(FOUNDATION_ORIENTATION_ENABLED=True)
class HeaderNavigationTests(TestCase):
    def header(self, response):
        return response.content.decode().split('<nav class="sw-nav"', 1)[1].split('</nav>', 1)[0]

    def test_public_navigation_has_accessible_controls_and_current_page(self):
        response = self.client.get(reverse('course_list'))
        header = self.header(response)
        self.assertIn('aria-label="Main navigation"', header)
        self.assertIn('aria-controls="sw-nav-links"', header)
        self.assertIn('aria-expanded="false"', header)
        self.assertIn('aria-current="page">Courses</a>', header)
        for name in ['Start Here', 'Schools', 'Courses', 'Resources', 'Services', 'About Us', 'Our Team', 'Log in', 'Sign up']:
            self.assertIn(name, header)
        self.assertContains(response, 'href="#main-content"')
        self.assertContains(response, 'id="main-content" tabindex="-1"')
        self.assertContains(response, 'js/navigation.js')

    def test_authenticated_navigation_has_one_account_menu_and_post_logout(self):
        user = get_user_model().objects.create_user(username='header-test')
        self.client.force_login(user)
        header = self.header(self.client.get(reverse('home')))
        self.assertIn('<details class="nav-user-pill"', header)
        self.assertIn('<summary class="nav-user-trigger">', header)
        self.assertEqual(header.count('>My Learning</a>'), 1)
        self.assertEqual(header.count('>Badges &amp; Certificates</a>'), 1)
        self.assertEqual(header.count('>Log out</button>'), 1)
        self.assertIn(f'action="{reverse("logout")}" method="post"', header)
        self.assertNotIn('onclick=', header)
        self.assertNotIn('Content Admin', header)

    def test_content_permission_is_preserved(self):
        user = get_user_model().objects.create_user(username='header-editor')
        user.user_permissions.add(Permission.objects.get(codename='view_courseasset'))
        self.client.force_login(user)
        header = self.header(self.client.get(reverse('home')))
        self.assertEqual(header.count('>Content Admin</a>'), 1)

    @override_settings(FOUNDATION_ORIENTATION_ENABLED=False)
    def test_disabled_orientation_does_not_leak_into_header(self):
        self.assertNotIn('Start Here', self.header(self.client.get(reverse('home'))))
