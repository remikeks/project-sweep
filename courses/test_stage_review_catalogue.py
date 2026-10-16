from __future__ import annotations

import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from courses.models import Course
from schools.models import School


def review_catalogue() -> list[dict]:
    return [{
        "number": 31,
        "school": "School of Community & Macro Practice",
        "title": "Digital Social Work Practice",
        "code": "SWP-031",
        "slug": "digital-social-work-practice",
        "outcome": "Use digital practice tools safely and accountably.",
        "modules": [
            {"order": 1, "title": "Access", "focus": "Inclusive access"},
            {"order": 2, "title": "Governance", "focus": "Information governance"},
            {"order": 3, "title": "Accountability", "focus": "Professional accountability"},
        ],
    }]


class StageReviewCatalogueTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="School of Community & Macro Practice",
            slug="school-of-community-macro-practice",
        )

    def test_commit_stages_a_non_learner_visible_course(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            catalogue_path = Path(temporary_directory) / "catalogue.json"
            catalogue_path.write_text(json.dumps(review_catalogue()), encoding="utf-8")
            call_command("stage_review_catalogue", "--catalogue", str(catalogue_path), "--commit")

        course = Course.objects.get(course_code="SWP-031")
        self.assertFalse(course.is_active)
        self.assertEqual(course.modules.count(), 3)
        self.assertEqual(Course.objects.filter(is_active=True).count(), 0)
