from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from . import services


class GeminiConfigTests(SimpleTestCase):
    @override_settings(GEMINI_API_KEY="gemini-key", GOOGLE_API_KEY=None)
    def test_get_api_key_prefers_gemini_setting(self):
        with patch.dict("os.environ", {}, clear=False):
            self.assertEqual(services._get_api_key(), "gemini-key")

    @override_settings(GEMINI_API_KEY=None, GOOGLE_API_KEY="google-key")
    def test_get_api_key_falls_back_to_google_setting(self):
        with patch.dict("os.environ", {}, clear=False):
            self.assertEqual(services._get_api_key(), "google-key")

    @override_settings(GEMINI_API_KEY=None, GOOGLE_API_KEY=None)
    def test_get_api_key_raises_when_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(services.TutorNotConfigured):
                services._get_api_key()
