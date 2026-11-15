"""GBV source traceability, incomplete-school boundary and retained CBT parity."""
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from django.core.management import call_command
from django.test import SimpleTestCase,TestCase
from courses.test_ert_phase_five import read,module
from courses.assessment_review_validation import validate_review_bank
from courses.authored_review import validate_package
from courses.curriculum_validation import validate_manifest
from courses.models import Course,CourseModule
from schools.models import School
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/"production_courseware/phase_seven/gbv_batch_01"
MEDIA=ROOT/"production_courseware/phase_seven/gbv_media_01"

class GbvSourceTests(SimpleTestCase):
    def test_deterministic_dated_source_and_sixty_new_questions_against_210_stems(self):
        compiler=module(ROOT/"scripts/build_course_review_batch.py","gbv_compiler")
        source=module(BATCH/"authoring.py","gbv_source")
        package=read(BATCH/"review_package.json")
        self.assertEqual(compiler.compile_package(source),package)
        self.assertEqual(validate_package(package),dict(courses=4,modules=12,questions=60))
        self.assertEqual(package["evidence_checked_on"],"2026-11-15")
        self.assertEqual(package["review"]["specialist_GBV_and_safeguarding"],"pending")
        prior=[]
        for path in ["phase_two/fsw_batch_01","phase_four/fsw_batch_02","phase_five/ert_batch_01","phase_six/ert_batch_02"]:
            old=read(ROOT/"production_courseware"/path/"review_package.json")
            prior.extend(q["question"] for c in old["courses"] for q in c["assessment"]["questions"])
        self.assertEqual(len(prior),210)
        for c in package["courses"]:
            self.assertEqual(c["school_code"],"GBV")
            self.assertIn("Do not seek real disclosures",c["study_guidance"])
            self.assertIn("Do not collect real disclosures",c["practice_safety_note"])
            validate_review_bank(c["assessment"],dict(code=c["code"],title=c["title"],slug=c["slug"],modules=c["modules"]),existing_stems=prior)
            prior.extend(q["question"] for q in c["assessment"]["questions"])

    def test_four_drafts_do_not_claim_complete_eight_course_curriculum_or_live_exam(self):
        scope=read(BATCH/"school_exam_scope.json")
        builder=module(ROOT/"scripts/build_gbv_curriculum_scope.py","gbv_scope")
        self.assertEqual(scope,builder.scope())
        self.assertEqual((scope["authored_draft_count"],scope["target_course_count"]),(4,8))
        self.assertEqual(sum(c["status"]=="not_authored" and c["course_code"] is None for c in scope["courses"]),4)
        self.assertFalse(scope["draft_catalogue_complete"]);self.assertFalse(scope["curriculum_approved"])
        exam=scope["exam_plan"]
        self.assertIsNone(exam["provider_assessment_id"]);self.assertFalse(exam["provider_contract_verified"])
        self.assertEqual(exam["proposed_items"],dict(MCQ=40,SHORT_ANSWER=6,ESSAY=2))
        self.assertTrue(exam["human_written_marking_required"]);self.assertTrue(exam["moderation_required"])
        self.assertFalse(exam["ai_only_finalisation"]);self.assertFalse(scope["certification"]["authorised"])

    def test_actual_gbv_resource_identity_and_all_prior_media_hashes(self):
        manifest=read(MEDIA/"upload_manifest.json")
        self.assertEqual(validate_manifest(manifest,release=MEDIA,profile="pdf_slides"),dict(assets=16,asset_courses=4))
        self.assertEqual({r["school_code"] for r in manifest},{"GBV"})
        self.assertEqual({r["course_code"] for r in manifest},{"SWP-049","SWP-050","SWP-051","SWP-052"})
        for path in ["phase_three/fsw_media_01","phase_four/fsw_media_02","phase_five/ert_media_01","phase_six/ert_media_02"]:
            release=ROOT/"production_courseware"/path
            validate_manifest(read(release/"upload_manifest.json"),release=release,profile="pdf_slides")

    def test_full_guidance_page_notice_is_not_mistaken_for_small_browser_challenge(self):
        fetch=module(ROOT/"scripts/fetch_ert_research.py","gbv_retrieval_test")
        self.assertFalse(fetch.is_challenge_page(b"<html>JavaScript is disabled"+b" normal guidance content"*1500+b"</html>"))
        self.assertTrue(fetch.is_challenge_page(b"<title>Client Challenge</title>"))
        self.assertTrue(fetch.is_challenge_page(b"Checking your browser"))
        self.assertTrue(fetch.is_challenge_page(b"JavaScript is disabled"))
        self.assertFalse(fetch.is_challenge_page(b"Ordinary retrieved source"))

class GbvStagingTests(TestCase):
    def test_gbv_creation_preserves_original_cbt_and_previous_ert_and_fsw_drafts(self):
        gbv=School.objects.create(name="GBV",code="GBV",target_course_count=8,enrollment_open=False)
        ert=School.objects.create(name="ERT",code="ERT",target_course_count=8,enrollment_open=False)
        original=Course.objects.create(school=ert,course_code="SWP-032",title="Retained",content="Original content",paralearn_assessment_id="retained-cbt")
        previous=Course.objects.create(school=ert,course_code="SWP-048",title="Earlier ERT",content="Prior draft",is_active=False)
        CourseModule.objects.create(course=previous,order=1,title="Prior module",content="Prior teaching")
        fsw=School.objects.create(name="FSW",code="FSW",enrollment_open=False)
        Course.objects.create(school=fsw,course_code="SWP-035",title="Earlier FSW",content="Protected FSW",is_active=False)
        before_courses=list(Course.objects.order_by("pk").values())
        before_modules=list(CourseModule.objects.order_by("pk").values())
        with TemporaryDirectory() as temporary:
            receipt=Path(temporary)/"new.json"
            call_command("stage_authored_review",package=BATCH/"review_package.json",commit=True,receipt=receipt,stdout=io.StringIO())
            proof=read(receipt.with_suffix(".applied.json"))
        self.assertEqual(proof["before"],proof["after"])
        self.assertEqual(list(Course.objects.exclude(pk__in=proof["new_course_ids"]).order_by("pk").values()),before_courses)
        self.assertEqual(list(CourseModule.objects.exclude(pk__in=proof["new_module_ids"]).order_by("pk").values()),before_modules)
        self.assertEqual(gbv.courses.count(),4)
        original.refresh_from_db();self.assertEqual(original.paralearn_assessment_id,"retained-cbt")
        gbv.refresh_from_db();self.assertFalse(gbv.enrollment_open);self.assertEqual(gbv.target_course_count,8)
        for row in gbv.courses.all():
            self.assertFalse(row.is_active);self.assertEqual(row.paralearn_assessment_id,"");self.assertEqual(row.modules.count(),3)
