import copy
import json
import unittest
from pathlib import Path

from courses.assessment_review_validation import AssessmentReviewError, validate_review_bank

ROOT = Path(__file__).resolve().parents[1]


class AssessmentReviewValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((ROOT / "production_courseware/expansion_review/swp-031-assessment-review.json").read_text(encoding="utf-8"))
        cls.catalogue = json.loads((ROOT / cls.bank["catalogue_path"]).read_text(encoding="utf-8"))[0]

    def test_valid_bank(self):
        self.assertEqual(validate_review_bank(self.bank, self.catalogue)["questions"], 15)

    def test_rejects_unsafe_or_incomplete_banks(self):
        changes = [
            lambda b: b.update(status="published"),
            lambda b: b.update(assessment_id="invented-id"),
            lambda b: b.update(course_code="SWP-001"),
            lambda b: b.update(minimum_correct=10),
            lambda b: b.update(catalogue_sha256=""),
            lambda b: b["questions"].pop(),
            lambda b: b["questions"][0].update(rationale=""),
            lambda b: b["questions"][0].update(module_order=2),
            lambda b: b["questions"][0].update(teaching_point_id="missing"),
            lambda b: b["questions"][1].update(id=b["questions"][0]["id"]),
            lambda b: b["questions"][1].update(question=b["questions"][0]["question"]),
            lambda b: b["questions"][0]["options"].pop(),
            lambda b: b["questions"][0]["options"][0].update(correct="false"),
            lambda b: b["questions"][0]["options"].__setitem__(1, copy.deepcopy(b["questions"][0]["options"][0])),
        ]
        for index, mutate in enumerate(changes):
            with self.subTest(change=index):
                bank = copy.deepcopy(self.bank)
                mutate(bank)
                with self.assertRaises(AssessmentReviewError):
                    validate_review_bank(bank, self.catalogue)

    def test_rejects_wrong_answer_key_count(self):
        for count in (0, 2, 4):
            bank = copy.deepcopy(self.bank)
            for index, option in enumerate(bank["questions"][0]["options"]):
                option["correct"] = index < count
            with self.subTest(count=count), self.assertRaises(AssessmentReviewError):
                validate_review_bank(bank, self.catalogue)

    def test_rejects_normalised_existing_question(self):
        existing = [self.bank["questions"][0]["question"].upper().replace(" ", "  ")]
        with self.assertRaises(AssessmentReviewError):
            validate_review_bank(self.bank, self.catalogue, existing)

    def test_all_four_banks_match_source(self):
        from scripts.build_expansion_review import build, REVIEW
        for name, content in build().items():
            self.assertEqual((REVIEW / name).read_text(encoding="utf-8"), content)

    def test_source_fingerprints_ignore_json_formatting(self):
        from scripts.build_expansion_review import json_fingerprint
        first = json.loads('{"b": 2, "a": 1}')
        second = json.loads('{\r\n  "a": 1,\r\n  "b": 2\r\n}')
        self.assertEqual(json_fingerprint(first), json_fingerprint(second))
        self.assertNotEqual(json_fingerprint(first), json_fingerprint({"a": 2, "b": 2}))
