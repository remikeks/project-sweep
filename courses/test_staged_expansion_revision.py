import copy
import hashlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.management.commands.revise_staged_expansion import snapshot
from courses.models import Course, CourseAsset, CourseModule
from schools.models import School


class StagedRevisionTests(TestCase):
    def setUp(self):
        folder = Path(__file__).resolve().parents[1] / "production_courseware/drafts/expansion-evidence-2026-10-17"
        catalogue = json.loads((folder / "course_catalogue.json").read_text())
        self.manifest = json.loads((folder / "upload_manifest.json").read_text())
        for row in catalogue:
            school, _ = School.objects.get_or_create(name=row["school"], defaults={"slug":f"school-{row['number']}"})
            course = Course.objects.create(school=school, title=row["title"], slug=row["slug"], course_code=row["code"], is_active=False)
            for module in row["modules"]:
                CourseModule.objects.create(course=course, title=module["title"], order=module["order"])
        for index, entry in enumerate(self.manifest):
            course = Course.objects.get(course_code=entry["course_code"])
            module = course.modules.get(order=entry["module_order"]) if entry["module_order"] else None
            CourseAsset.objects.create(course=course, module=module, title=entry["title"], asset_type=entry["asset_type"],
                content_type=entry["content_type"], version="1.0.0", status="in_review", storage_path=f"courses/old/{index}.pdf", external_url=f"https://example.test/{index}")

    def test_exact_existing_rows_are_matched_without_mutation(self):
        before = list(CourseAsset.objects.values())
        result = snapshot(self.manifest)
        self.assertEqual(len(result["assets"]), 32)
        self.assertEqual(len({e["target_id"] for e in self.manifest}), 32)
        self.assertEqual(before, list(CourseAsset.objects.values()))

    def test_active_course_is_rejected(self):
        Course.objects.filter(course_code="SWP-031").update(is_active=True)
        with self.assertRaises(CommandError): snapshot(self.manifest)

    def test_published_asset_is_rejected(self):
        CourseAsset.objects.filter(pk=CourseAsset.objects.first().pk).update(status="published")
        with self.assertRaises(CommandError): snapshot(self.manifest)

    def test_duplicate_asset_is_rejected(self):
        asset = CourseAsset.objects.first()
        asset.pk = None
        asset.save()
        with self.assertRaises(CommandError): snapshot(self.manifest)

    def test_missing_module_is_rejected(self):
        CourseModule.objects.first().delete()
        with self.assertRaises(CommandError): snapshot(self.manifest)

    def test_changed_slug_is_rejected(self):
        Course.objects.filter(course_code="SWP-031").update(slug="different-course")
        with self.assertRaises(CommandError): snapshot(self.manifest)

    def test_repeated_target_is_rejected(self):
        entries = copy.deepcopy(self.manifest)
        entries[1] = copy.deepcopy(entries[0])
        with self.assertRaises(CommandError): snapshot(entries)

    def revision_fixture(self, directory):
        """Synthetic QA receipt for an isolated test, never production approval."""
        root = Path(__file__).resolve().parents[1]
        original = root / "production_courseware/drafts/expansion-evidence-2026-10-17"
        release = Path(directory)
        for name in ("upload_manifest.json", "course_catalogue.json"):
            (release / name).write_bytes((original / name).read_bytes())
        teaching = root / "production_courseware/expansion_review/teaching_source.json"
        receipt = {"visual_review_complete": True,
                   "manifest_sha256": hashlib.sha256((release / "upload_manifest.json").read_bytes()).hexdigest(),
                   "teaching_source_sha256": hashlib.sha256(teaching.read_bytes()).hexdigest(),
                   "assessment_source_sha256": hashlib.sha256(teaching.with_name("assessment_source.json").read_bytes()).hexdigest()}
        (release / "evidence_receipt.json").write_text(json.dumps(receipt))
        return dict(release=release, teaching_source=teaching, journal=release / "private.json", commit=True, stdout=io.StringIO())

    def test_commit_preserves_ids_and_publication_and_rerun_is_noop(self):
        prefix = "courses.management.commands.revise_staged_expansion."
        before_ids = list(CourseAsset.objects.values_list("id", flat=True))
        with tempfile.TemporaryDirectory() as directory:
            options = self.revision_fixture(directory)
            with patch(prefix + "validate_manifest"), patch(prefix + "SupabaseStorageClient"), \
                    patch(prefix + "verify_remote") as verify, patch(prefix + "upload_bytes") as upload, \
                    patch(prefix + "canonical_storage_url", side_effect=lambda p: "https://example.test/" + p):
                call_command("revise_staged_expansion", **options)
                self.assertEqual(verify.call_count, 32)
                self.assertEqual(before_ids, list(CourseAsset.objects.values_list("id", flat=True)))
                self.assertEqual(CourseAsset.objects.filter(status="in_review", version="1.1.0").count(), 32)
                self.assertEqual(Course.objects.filter(is_active=False).count(), 4)
                self.assertEqual(CourseModule.objects.filter(content__contains="Decision points").count(), 12)
                after = snapshot(copy.deepcopy(self.manifest))
                call_command("revise_staged_expansion", **options)
                self.assertEqual(verify.call_count, 32)
                upload.assert_not_called()
                self.assertEqual(after, snapshot(copy.deepcopy(self.manifest)))
                journal = json.loads(options["journal"].read_text())
                self.assertTrue(journal["committed"])
                self.assertEqual(len(journal["before"]["assets"]), 32)

    def test_database_failure_rolls_back_all_rows_and_retry_reuses_objects(self):
        prefix = "courses.management.commands.revise_staged_expansion."
        before = snapshot(copy.deepcopy(self.manifest))
        with tempfile.TemporaryDirectory() as directory:
            options = self.revision_fixture(directory)
            with patch(prefix + "validate_manifest"), patch(prefix + "SupabaseStorageClient"), \
                    patch(prefix + "verify_remote") as verify, patch(prefix + "upload_bytes") as upload, \
                    patch(prefix + "canonical_storage_url", side_effect=RuntimeError("simulated database-phase failure")):
                with self.assertRaises(RuntimeError):
                    call_command("revise_staged_expansion", **options)
                self.assertEqual(before, snapshot(copy.deepcopy(self.manifest)))
                self.assertFalse(json.loads(options["journal"].read_text())["committed"])
                with patch(prefix + "canonical_storage_url", side_effect=lambda p: "https://example.test/" + p):
                    call_command("revise_staged_expansion", **options)
                self.assertEqual(verify.call_count, 64)
                upload.assert_not_called()
                self.assertEqual(CourseAsset.objects.count(), 32)
