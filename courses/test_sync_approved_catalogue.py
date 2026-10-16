from __future__ import annotations

import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from courses.models import Course
from schools.models import School


def catalogue() -> list[dict]:
    entries = []
    for number in range(1, 32):
        school_number = min((number - 1) // 3 + 1, 10)
        if number == 31:
            school_number = 5
        entries.append({
            "number": number,
            "school": f"School {school_number}",
            "title": "Digital Social Work Practice" if number == 31 else f"Course {number}",
            "code": f"SWP-{number:03d}",
            "slug": "digital-social-work-practice" if number == 31 else f"course-{number}",
            "outcome": "Use a defined approach safely and responsibly.",
            "modules": [
                {"order": order, "title": f"Module {order}", "focus": f"Focus {order}"}
                for order in range(1, 4)
            ],
        })
    return entries


def exam_bank() -> list[dict]:
    return [
        {
            "school": f"School {school_number}",
            "passing_score": 70,
            "questions": [
                {
                    "order": question_number,
                    "text": f"Question {school_number}-{question_number}",
                    "choices": [
                        {"order": choice_number, "text": f"Choice {choice_number}", "is_correct": choice_number == 1}
                        for choice_number in range(1, 5)
                    ],
                }
                for question_number in range(1, 16)
            ],
        }
        for school_number in range(1, 11)
    ]


class SyncApprovedCatalogueTests(TestCase):
    def setUp(self):
        self.catalogue = catalogue()
        for school_number in range(1, 11):
            school = School.objects.create(name=f"School {school_number}", slug=f"school-{school_number}")
            for entry in [item for item in self.catalogue[:30] if item["school"] == school.name]:
                Course.objects.create(
                    school=school,
                    title=entry["title"],
                    slug=entry["slug"],
                    course_code=entry["code"],
                    order=entry["number"],
                )

    def test_commit_can_create_an_approved_course_without_changing_school_count(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            catalogue_path = directory / "catalogue.json"
            exam_path = directory / "exam-bank.json"
            catalogue_path.write_text(json.dumps(self.catalogue), encoding="utf-8")
            exam_path.write_text(json.dumps(exam_bank()), encoding="utf-8")

            call_command(
                "sync_approved_catalogue",
                "--catalogue", str(catalogue_path),
                "--exam-bank", str(exam_path),
                "--create-missing-courses",
                "--commit",
            )

        course = Course.objects.get(course_code="SWP-031")
        self.assertEqual(course.school.name, "School 5")
        self.assertEqual(course.title, "Digital Social Work Practice")
        self.assertEqual(course.modules.count(), 3)
        self.assertEqual(School.objects.count(), 10)
