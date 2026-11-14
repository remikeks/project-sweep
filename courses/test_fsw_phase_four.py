"""Verify the complete second FSW batch and its ten-course coverage boundary."""
import importlib.util
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase, SimpleTestCase

from courses.authored_review import validate_package
from courses.assessment_review_validation import validate_review_bank
from courses.models import Course
from schools.models import School
from schools.exam_blueprints import validate_blueprint,review_result_contract

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/"production_courseware/phase_four/fsw_batch_02"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class FswSecondBatchTests(SimpleTestCase):
    def test_export_is_reproducible_and_stems_do_not_duplicate_prior_batch(self):
        spec=importlib.util.spec_from_file_location("batch_compiler",ROOT/"scripts/build_course_review_batch.py")
        compiler=importlib.util.module_from_spec(spec);spec.loader.exec_module(compiler)
        spec=importlib.util.spec_from_file_location("batch_authoring",BATCH/"authoring.py")
        source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
        package=load(BATCH/"review_package.json")
        self.assertEqual(compiler.compile_package(source),package)
        self.assertEqual(validate_package(package),dict(courses=5,modules=15,questions=75))
        prior=load(ROOT/"production_courseware/phase_two/fsw_batch_01/review_package.json")
        stems=[q["question"] for c in prior["courses"] for q in c["assessment"]["questions"]]
        for c in package["courses"]:
            validate_review_bank(c["assessment"],dict(code=c["code"],title=c["title"],slug=c["slug"],modules=c["modules"]),existing_stems=stems)
            stems.extend(q["question"] for q in c["assessment"]["questions"])

    def test_ten_course_exam_covers_each_course_in_mcq_and_written_sections(self):
        exam=load(BATCH/"school_exam_blueprint.json")
        result=validate_blueprint(exam)
        self.assertEqual(result,dict(courses=10,items=48,marks=100,unbound_mcqs=40,ready_for_launch=False))
        for code in exam["required_courses"]:
            self.assertEqual(sum(i["course_codes"]==[code] for i in exam["items"] if i["type"]=="MCQ"),4)
            self.assertTrue(any(code in i["course_codes"] for i in exam["items"] if i["type"]!="MCQ"))
        old=load(ROOT/"production_courseware/phase_two/fsw_batch_01/school_exam_blueprint.json")
        self.assertNotEqual(exam["curriculum_version"],old["curriculum_version"])
        result=review_result_contract(exam,dict(school_code="FSW",curriculum_version=old["curriculum_version"],
            completed_courses=old["required_courses"],status="finalized",moderation_status="approved",item_results=[]),verified_transport=True)
        self.assertFalse(result["contract_checks_passed"])
        self.assertFalse(result["certificate_authorised"])


class FswSecondBatchStagingTests(TestCase):
    def test_five_additions_preserve_the_previous_fsw_courses_and_cbt(self):
        school=School.objects.create(name="FSW review",code="FSW",enrollment_open=False)
        prior_codes=["SWP-016","SWP-017","SWP-018","SWP-035","SWP-036"]
        for code in prior_codes:
            Course.objects.create(school=school,title="Existing "+code,course_code=code,
                content="Protected "+code,paralearn_assessment_id="existing-"+code,is_active=code in prior_codes[:3])
        before=list(Course.objects.order_by("pk").values())
        with TemporaryDirectory() as temporary:
            receipt=Path(temporary)/"new.json"
            call_command("stage_authored_review",package=BATCH/"review_package.json",commit=True,receipt=receipt,stdout=io.StringIO())
            audit=load(receipt.with_suffix(".applied.json"))
        self.assertEqual(audit["before"],audit["after"])
        self.assertEqual(list(Course.objects.filter(course_code__in=prior_codes).order_by("pk").values()),before)
        self.assertEqual(school.courses.count(),10)
        for course in school.courses.exclude(course_code__in=prior_codes):
            self.assertFalse(course.is_active)
            self.assertEqual(course.paralearn_assessment_id,"")
            self.assertEqual(course.modules.count(),3)
            self.assertNotIn('"correct":',course.content)
