from __future__ import annotations

import hashlib
import unittest

from courses.curriculum_validation import CurriculumValidationError, validate_catalogue, validate_manifest


def catalogue_with_course_total(total: int = 30) -> list[dict]:
    """Return a ten-school fixture, allowing an extension beyond 30 courses."""
    catalogue = []
    for number in range(1, total + 1):
        school_number = min((number - 1) // 3 + 1, 10)
        catalogue.append({
            "number": number,
            "school": f"School {school_number}",
            "title": f"Course {number}",
            "code": f"SWP-{number:03d}",
            "slug": f"course-{number}",
            "outcome": "A measurable learning outcome.",
            "modules": [
                {"order": order, "title": f"Lesson {order}", "focus": f"Focus {order}"}
                for order in range(1, 4)
            ],
        })
    return catalogue


def manifest_for(catalogue: list[dict]) -> list[dict]:
    entries = []
    package = (
        ("learner_guide", "Learner guide DOCX", "guide.docx", ""),
        ("learner_guide", "Learner guide PDF", "guide.pdf", ""),
        ("slides", "Course deck", "deck.pptx", ""),
        ("worksheet", "Worksheet DOCX", "worksheet.docx", ""),
        ("worksheet", "Worksheet PDF", "worksheet.pdf", ""),
        ("transcript", "Module 1 transcript", "module-1.docx", "1"),
        ("transcript", "Module 2 transcript", "module-2.docx", "2"),
        ("transcript", "Module 3 transcript", "module-3.docx", "3"),
    )
    for course in catalogue:
        for asset_type, title, filename, module_order in package:
            path = f"assets/{course['slug']}/{filename}"
            entries.append({
                "course_number": course["number"],
                "course_code": course["code"],
                "course_slug": course["slug"],
                "school": course["school"],
                "module_order": module_order,
                "title": title,
                "asset_type": asset_type,
                "path": path,
                "content_type": "application/octet-stream",
                "size_bytes": 1,
                "sha256": hashlib.sha256(path.encode("utf-8")).hexdigest(),
                "version": "1.0.0",
                "language": "en",
                "publication_status": "in_review",
            })
    return entries


class CurriculumValidationTests(unittest.TestCase):
    def test_accepts_an_extension_without_requiring_exactly_thirty_courses(self):
        catalogue = catalogue_with_course_total(31)
        catalogue[-1]["school"] = "School 10"
        self.assertEqual(validate_catalogue(catalogue)["courses"], 31)
        self.assertEqual(validate_manifest(manifest_for(catalogue), catalogue=catalogue)["assets"], 248)

    def test_rejects_normalized_duplicate_course_title_within_a_school(self):
        catalogue = catalogue_with_course_total()
        catalogue[1]["title"] = "  COURSE   1 "
        with self.assertRaisesRegex(CurriculumValidationError, "course title"):
            validate_catalogue(catalogue)

    def test_rejects_a_duplicated_release_checksum(self):
        catalogue = catalogue_with_course_total()
        manifest = manifest_for(catalogue)
        manifest[1]["sha256"] = manifest[0]["sha256"]
        with self.assertRaisesRegex(CurriculumValidationError, "checksum"):
            validate_manifest(manifest, catalogue=catalogue)

    def test_rejects_an_incomplete_course_package(self):
        catalogue = catalogue_with_course_total()
        manifest = manifest_for(catalogue)
        manifest.pop()
        with self.assertRaisesRegex(CurriculumValidationError, "exactly eight"):
            validate_manifest(manifest, catalogue=catalogue)
