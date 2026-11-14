import copy
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.curriculum_validation import CurriculumValidationError, validate_manifest
from courses.models import Course, CourseAsset
from schools.models import School

PDF="application/pdf"
PPTX="application/vnd.openxmlformats-officedocument.presentationml.presentation"


class PdfSlideResourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        school=School.objects.create(name="Foundational drafts",code="FSW",enrollment_open=False)
        cls.course=Course.objects.create(school=school,title="Ethics draft",course_code="SWP-035",is_active=False)

    def setUp(self):
        self.temporary=TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.release=Path(self.temporary.name)
        self.manifest=[]
        for n,(kind,mime,suffix) in enumerate([("learner_guide",PDF,".pdf"),("worksheet",PDF,".pdf"),("slides",PDF,".pdf"),("slides",PPTX,".pptx")]):
            source=self.release/(f"resource-{n}"+suffix)
            source.write_bytes(f"unique fake test content {n}".encode())
            self.manifest.append(dict(course_code="SWP-035",course_slug=self.course.slug,title=f"Ethics resource {n}",asset_type=kind,
                path=source.name,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),size_bytes=source.stat().st_size,
                version="0.1.0",content_type=mime,module_order="",publication_status="in_review",language="en"))
        self.path=self.release/"manifest.json"
        self.path.write_text(json.dumps(self.manifest))

    def test_accepts_only_the_complete_pdf_and_slides_profile(self):
        self.assertEqual(validate_manifest(self.manifest,release=self.release,profile="pdf_slides"),dict(assets=4,asset_courses=1))
        with self.assertRaises(CurriculumValidationError):
            validate_manifest(self.manifest)  # Legacy packages still require all eight legacy assets.
        for change in (lambda d:d.pop(),lambda d:d[0].update(content_type="application/msword"),
                       lambda d:d[1].update(version="9.0"),lambda d:d[2].update(publication_status="published")):
            invalid=copy.deepcopy(self.manifest);change(invalid)
            with self.assertRaises(CurriculumValidationError):
                validate_manifest(invalid,profile="pdf_slides")

    def test_changed_file_is_rejected_before_upload(self):
        (self.release/self.manifest[0]["path"]).write_bytes(b"changed")
        with self.assertRaises(CurriculumValidationError),patch("courses.management.commands.stage_pdf_slide_resources.SupabaseStorageClient") as storage:
            call_command("stage_pdf_slide_resources",release=self.release,manifest=self.path,stdout=io.StringIO())
        storage.assert_not_called()

    def test_active_course_refused_before_upload(self):
        self.course.is_active=True;self.course.save(update_fields=["is_active"])
        with patch("courses.management.commands.stage_pdf_slide_resources.SupabaseStorageClient") as storage:
            with self.assertRaisesRegex(CommandError,"inactive"):
                call_command("stage_pdf_slide_resources",release=self.release,manifest=self.path,commit=True,receipt=self.release/"receipt.json",stdout=io.StringIO())
            storage.assert_not_called()

    def test_complete_batch_is_added_in_review_without_approving_it(self):
        before=Course.objects.get(pk=self.course.pk).__dict__.copy();before.pop("_state")
        with patch("courses.management.commands.stage_pdf_slide_resources.SupabaseStorageClient"), \
             patch("courses.management.commands.stage_pdf_slide_resources.ensure_private_bucket"), \
             patch("courses.management.commands.stage_pdf_slide_resources.upload_bytes") as upload, \
             patch("courses.management.commands.stage_pdf_slide_resources.verify_bytes") as verify:
            receipt=self.release/"receipt.json"
            call_command("stage_pdf_slide_resources",release=self.release,manifest=self.path,commit=True,receipt=receipt,stdout=io.StringIO())
            self.assertEqual(upload.call_count,4);self.assertEqual(verify.call_count,4)
        rows=CourseAsset.objects.filter(course=self.course)
        self.assertEqual(rows.count(),4)
        self.assertEqual(set(rows.values_list("status",flat=True)),{"in_review"})
        self.assertFalse(rows.exclude(reviewed_at=None).exists())
        after=Course.objects.get(pk=self.course.pk).__dict__.copy();after.pop("_state")
        self.assertEqual(before,after)
        proof=json.loads(receipt.with_suffix(".applied.json").read_text())
        self.assertEqual(proof["before"],proof["after"])
        with self.assertRaisesRegex(CommandError,"already has assets"):
            call_command("stage_pdf_slide_resources",release=self.release,manifest=self.path,commit=True,receipt=self.release/"again.json",stdout=io.StringIO())

    def test_failed_download_verification_creates_no_metadata(self):
        with patch("courses.management.commands.stage_pdf_slide_resources.SupabaseStorageClient"), \
             patch("courses.management.commands.stage_pdf_slide_resources.ensure_private_bucket"), \
             patch("courses.management.commands.stage_pdf_slide_resources.upload_bytes"), \
             patch("courses.management.commands.stage_pdf_slide_resources.verify_bytes",side_effect=CommandError("checksum mismatch")):
            with self.assertRaisesRegex(CommandError,"checksum mismatch"):
                call_command("stage_pdf_slide_resources",release=self.release,manifest=self.path,commit=True,receipt=self.release/"receipt.json",stdout=io.StringIO())
        self.assertFalse(CourseAsset.objects.exists())
        self.assertTrue((self.release/"receipt.uploads.jsonl").is_file())
