"""GBV completion breadth, non-live mixed exam and additive retained-data proof."""
import copy
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
from schools.exam_blueprints import validate_blueprint,review_result_contract
from schools.models import School
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/"production_courseware/phase_eight/gbv_batch_02"
MEDIA=ROOT/"production_courseware/phase_eight/gbv_media_02"

class GbvCompletionSourceTests(SimpleTestCase):
    def test_dated_deterministic_sources_and_sixty_questions_against_270_prior_stems(self):
        compiler=module(ROOT/"scripts/build_course_review_batch.py","gbv8_compiler")
        source=module(BATCH/"authoring.py","gbv8_source")
        package=read(BATCH/"review_package.json")
        self.assertEqual(compiler.compile_package(source),package)
        self.assertEqual(validate_package(package),dict(courses=4,modules=12,questions=60))
        self.assertEqual(package["evidence_checked_on"],"2026-11-15")
        self.assertEqual(package["review"]["specialist_GBV_and_safeguarding"],"pending")
        prior=[]
        for path in ["phase_two/fsw_batch_01","phase_four/fsw_batch_02","phase_five/ert_batch_01","phase_six/ert_batch_02","phase_seven/gbv_batch_01"]:
            prior.extend(q["question"] for c in read(ROOT/"production_courseware"/path/"review_package.json")["courses"] for q in c["assessment"]["questions"])
        self.assertEqual(len(prior),270)
        for c in package["courses"]:
            self.assertEqual(c["school_code"],"GBV")
            self.assertIn("Do not seek real disclosures",c["study_guidance"])
            self.assertIn("Do not collect real disclosures",c["practice_safety_note"])
            validate_review_bank(c["assessment"],dict(code=c["code"],title=c["title"],slug=c["slug"],modules=c["modules"]),existing_stems=prior)
            prior.extend(q["question"] for q in c["assessment"]["questions"])

    def test_full_eight_course_exam_covers_actual_catalogue_and_keeps_old_scope_historical(self):
        exam=read(BATCH/"school_exam_blueprint.json")
        builder=module(ROOT/"scripts/build_gbv_eight_course_exam.py","gbv8_exam")
        self.assertEqual(exam,builder.blueprint())
        self.assertEqual(validate_blueprint(exam),dict(courses=8,items=48,marks=100,unbound_mcqs=40,ready_for_launch=False))
        old=read(ROOT/"production_courseware/phase_seven/gbv_batch_01/review_package.json")
        new=read(BATCH/"review_package.json")
        self.assertEqual(exam["required_courses"],[c["code"] for c in old["courses"]+new["courses"]])
        for code in exam["required_courses"]:
            self.assertEqual(sum(i["type"]=="MCQ" and i["course_codes"]==[code] for i in exam["items"]),5)
        self.assertEqual({c for i in exam["items"] if i["type"]=="SHORT_ANSWER" for c in i["course_codes"]},set(exam["required_courses"]))
        for item in [i for i in exam["items"] if i["type"]=="ESSAY"]:
            self.assertEqual(set(item["course_codes"]),set(exam["required_courses"]))
        self.assertTrue(exam["draft_catalogue_complete"]);self.assertFalse(exam["curriculum_complete"])
        self.assertFalse(exam["certification"]["authorised"])
        scope=read(ROOT/"production_courseware/phase_seven/gbv_batch_01/school_exam_scope.json")
        self.assertFalse(scope["draft_catalogue_complete"])
        self.assertEqual(scope["authored_draft_count"],4)

    def test_perfect_offline_exam_cannot_certify_and_missing_courses_or_moderation_fail(self):
        exam=read(BATCH/"school_exam_blueprint.json")
        result=dict(school_code="GBV",curriculum_version=exam["curriculum_version"],completed_courses=exam["required_courses"],status="finalized",moderation_status="approved",
            item_results=[dict(id=i["id"],score=i["marks"],marking_status="marked",human_marker_id="test-human") for i in exam["items"]])
        good=review_result_contract(exam,result,verified_transport=True)
        self.assertTrue(good["contract_checks_passed"]);self.assertFalse(good["certificate_authorised"])
        self.assertFalse(review_result_contract(exam,result)["contract_checks_passed"])
        incomplete=copy.deepcopy(result);incomplete["completed_courses"]=exam["required_courses"][:4]
        self.assertIn("Required course completions are incomplete or mismatched",review_result_contract(exam,incomplete,verified_transport=True)["reasons"])
        pending=copy.deepcopy(result);pending["moderation_status"]="pending"
        self.assertIn("Marking and moderation are not final",review_result_contract(exam,pending,verified_transport=True)["reasons"])
        unmarked=copy.deepcopy(result);next(i for i in unmarked["item_results"] if "SA-" in i["id"])["human_marker_id"]=""
        self.assertIn("Written answer awaits human marking",review_result_contract(exam,unmarked,verified_transport=True)["reasons"])

    def test_sixteen_actual_resources_and_every_prior_media_hash(self):
        manifest=read(MEDIA/"upload_manifest.json")
        self.assertEqual(validate_manifest(manifest,release=MEDIA,profile="pdf_slides"),dict(assets=16,asset_courses=4))
        self.assertEqual({r["school_code"] for r in manifest},{"GBV"})
        self.assertEqual({r["course_code"] for r in manifest},{f"SWP-{n:03}" for n in range(53,57)})
        for path in ["phase_three/fsw_media_01","phase_four/fsw_media_02","phase_five/ert_media_01","phase_six/ert_media_02","phase_seven/gbv_media_01"]:
            release=ROOT/"production_courseware"/path
            validate_manifest(read(release/"upload_manifest.json"),release=release,profile="pdf_slides")

class GbvCompletionStagingTests(TestCase):
    def test_final_four_preserve_first_four_gbv_and_original_cbt_other_schools(self):
        gbv=School.objects.create(name="GBV",code="GBV",target_course_count=8,enrollment_open=False)
        for code in range(49,53):
            old=Course.objects.create(school=gbv,course_code=f"SWP-{code:03}",title=f"Earlier GBV {code}",content="Protected earlier draft",is_active=False)
            CourseModule.objects.create(course=old,order=1,title="Earlier module",content="Protected earlier teaching")
        ert=School.objects.create(name="ERT",code="ERT",enrollment_open=False)
        original=Course.objects.create(school=ert,course_code="SWP-032",title="Retained",content="Original content",paralearn_assessment_id="retained-cbt")
        fsw=School.objects.create(name="FSW",code="FSW",enrollment_open=False)
        Course.objects.create(school=fsw,course_code="SWP-035",title="Earlier FSW",content="Protected FSW",is_active=False)
        before_courses=list(Course.objects.order_by("pk").values());before_modules=list(CourseModule.objects.order_by("pk").values())
        with TemporaryDirectory() as temporary:
            receipt=Path(temporary)/"new.json"
            call_command("stage_authored_review",package=BATCH/"review_package.json",commit=True,receipt=receipt,stdout=io.StringIO())
            proof=read(receipt.with_suffix(".applied.json"))
        self.assertEqual(proof["before"],proof["after"])
        self.assertEqual(list(Course.objects.exclude(pk__in=proof["new_course_ids"]).order_by("pk").values()),before_courses)
        self.assertEqual(list(CourseModule.objects.exclude(pk__in=proof["new_module_ids"]).order_by("pk").values()),before_modules)
        self.assertEqual(gbv.courses.count(),8)
        original.refresh_from_db();self.assertEqual(original.paralearn_assessment_id,"retained-cbt")
        gbv.refresh_from_db();self.assertFalse(gbv.enrollment_open)
        for row in Course.objects.filter(pk__in=proof["new_course_ids"]):
            self.assertFalse(row.is_active);self.assertEqual(row.paralearn_assessment_id,"");self.assertEqual(row.modules.count(),3)
