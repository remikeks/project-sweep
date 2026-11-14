"""ERT completion breadth, historical-result rejection and additive staging."""
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
BATCH=ROOT/"production_courseware/phase_six/ert_batch_02"
MEDIA=ROOT/"production_courseware/phase_six/ert_media_02"

class ErtCompletionSourceTests(SimpleTestCase):
    def test_completion_sources_trace_all_questions_without_reusing_165_prior_stems(self):
        compiler=module(ROOT/"scripts/build_course_review_batch.py","ert6_compiler")
        source=module(BATCH/"authoring.py","ert6_source")
        package=read(BATCH/"review_package.json")
        self.assertEqual(compiler.compile_package(source),package)
        self.assertEqual(validate_package(package),dict(courses=3,modules=9,questions=45))
        prior=[]
        for path in ["phase_two/fsw_batch_01","phase_four/fsw_batch_02","phase_five/ert_batch_01"]:
            prior.extend(q["question"] for c in read(ROOT/"production_courseware"/path/"review_package.json")["courses"] for q in c["assessment"]["questions"])
        self.assertEqual(len(prior),165)
        for c in package["courses"]:
            validate_review_bank(c["assessment"],dict(code=c["code"],title=c["title"],slug=c["slug"],modules=c["modules"]),existing_stems=prior)
            prior.extend(q["question"] for q in c["assessment"]["questions"])
        self.assertNotIn("R9",{r["id"] for r in package["references"]})

    def test_full_exam_covers_all_eight_and_rejects_old_five_course_result(self):
        exam=read(BATCH/"school_exam_blueprint.json")
        builder=module(ROOT/"scripts/build_ert_eight_course_exam.py","ert6_exam")
        self.assertEqual(exam,builder.blueprint())
        self.assertEqual(validate_blueprint(exam)["courses"],8)
        self.assertTrue(exam["draft_catalogue_complete"])
        self.assertFalse(exam["curriculum_complete"])
        self.assertFalse(exam["certification"]["authorised"])
        for code in exam["required_courses"]:
            self.assertEqual(sum(i["type"]=="MCQ" and i["course_codes"]==[code] for i in exam["items"]),5)
        for item in [i for i in exam["items"] if i["type"]=="ESSAY"]:
            self.assertEqual(set(item["course_codes"]),set(exam["required_courses"]))
        old=read(ROOT/"production_courseware/phase_five/ert_batch_01/school_exam_blueprint.json")
        result=dict(school_code="ERT",curriculum_version=old["curriculum_version"],completed_courses=old["required_courses"],status="finalized",moderation_status="approved",
            item_results=[dict(id=i["id"],score=i["marks"],marking_status="marked",human_marker_id="test-marker") for i in old["items"]])
        checked=review_result_contract(exam,result,verified_transport=True)
        self.assertFalse(checked["contract_checks_passed"])
        self.assertIn("School or curriculum identity mismatch",checked["reasons"])
        self.assertFalse(checked["certificate_authorised"])

    def test_twelve_actual_resources_and_prior_media_integrity(self):
        self.assertEqual(validate_manifest(read(MEDIA/"upload_manifest.json"),release=MEDIA,profile="pdf_slides"),dict(assets=12,asset_courses=3))
        self.assertEqual({r["school_code"] for r in read(MEDIA/"upload_manifest.json")},{"ERT"})
        for path in ["phase_three/fsw_media_01","phase_four/fsw_media_02","phase_five/ert_media_01"]:
            release=ROOT/"production_courseware"/path
            validate_manifest(read(release/"upload_manifest.json"),release=release,profile="pdf_slides")

class ErtCompletionStagingTests(TestCase):
    def test_new_batch_preserves_original_cbt_previous_ert_drafts_and_other_school(self):
        ert=School.objects.create(name="ERT",code="ERT",target_course_count=8,enrollment_open=False)
        original=Course.objects.create(school=ert,course_code="SWP-032",title="Retained",content="Original content",paralearn_assessment_id="original-cbt")
        for code in range(42,46):
            previous=Course.objects.create(school=ert,course_code=f"SWP-{code:03}",title=f"Earlier ERT {code}",is_active=False,content="Earlier draft")
            CourseModule.objects.create(course=previous,order=1,title="Earlier module",content="Protected earlier teaching")
        fsw=School.objects.create(name="FSW",code="FSW",enrollment_open=False)
        Course.objects.create(school=fsw,course_code="SWP-035",title="Earlier FSW",is_active=False,content="Protected FSW")
        before_courses=list(Course.objects.order_by("pk").values())
        before_modules=list(CourseModule.objects.order_by("pk").values())
        with TemporaryDirectory() as temporary:
            receipt=Path(temporary)/"new.json"
            call_command("stage_authored_review",package=BATCH/"review_package.json",commit=True,receipt=receipt,stdout=io.StringIO())
            audit=read(receipt.with_suffix(".applied.json"))
        self.assertEqual(audit["before"],audit["after"])
        self.assertEqual(list(Course.objects.exclude(pk__in=audit["new_course_ids"]).order_by("pk").values()),before_courses)
        self.assertEqual(list(CourseModule.objects.exclude(pk__in=audit["new_module_ids"]).order_by("pk").values()),before_modules)
        self.assertEqual(ert.courses.count(),8)
        original.refresh_from_db();self.assertEqual(original.paralearn_assessment_id,"original-cbt")
        ert.refresh_from_db();self.assertFalse(ert.enrollment_open)
        for course in Course.objects.filter(pk__in=audit["new_course_ids"]):
            self.assertFalse(course.is_active);self.assertEqual(course.paralearn_assessment_id,"");self.assertEqual(course.modules.count(),3)
