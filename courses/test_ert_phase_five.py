"""ERT source, milestone, school identity and retained-CBT protection checks."""
import importlib.util
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from django.core.management import call_command
from django.test import SimpleTestCase,TestCase
from courses.assessment_review_validation import validate_review_bank
from courses.authored_review import validate_package
from courses.curriculum_validation import validate_manifest
from courses.models import Course
from schools.exam_blueprints import validate_blueprint,review_result_contract
from schools.models import School

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/"production_courseware/phase_five/ert_batch_01"
MEDIA=ROOT/"production_courseware/phase_five/ert_media_01"
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

class ErtReviewSourceTests(SimpleTestCase):
    def test_deterministic_source_and_no_question_stem_overlap_with_prior_batches(self):
        compiler=module(ROOT/"scripts/build_course_review_batch.py","ert_test_compiler")
        source=module(BATCH/"authoring.py","ert_test_authoring")
        package=read(BATCH/"review_package.json")
        self.assertEqual(compiler.compile_package(source),package)
        self.assertEqual(validate_package(package),dict(courses=4,modules=12,questions=60))
        prior=[]
        for path in ["phase_two/fsw_batch_01","phase_four/fsw_batch_02"]:
            prior.extend(q["question"] for c in read(ROOT/"production_courseware"/path/"review_package.json")["courses"] for q in c["assessment"]["questions"])
        self.assertEqual(len(prior),105)
        for c in package["courses"]:
            self.assertEqual(c["school_code"],"ERT")
            validate_review_bank(c["assessment"],dict(code=c["code"],title=c["title"],slug=c["slug"],modules=c["modules"]),existing_stems=prior)
            prior.extend(q["question"] for q in c["assessment"]["questions"])

    def test_resource_manifest_keeps_actual_school_identity_and_prior_media_hashes(self):
        manifest=read(MEDIA/"upload_manifest.json")
        self.assertEqual(validate_manifest(manifest,release=MEDIA,profile="pdf_slides"),dict(assets=16,asset_courses=4))
        self.assertEqual({r["school_code"] for r in manifest},{"ERT"})
        self.assertEqual({r["course_code"] for r in manifest},{"SWP-042","SWP-043","SWP-044","SWP-045"})
        for path in ["phase_three/fsw_media_01","phase_four/fsw_media_02"]:
            release=ROOT/"production_courseware"/path
            validate_manifest(read(release/"upload_manifest.json"),release=release,profile="pdf_slides")

    def test_milestone_exam_does_not_claim_completed_eight_course_curriculum_or_certificate(self):
        exam=read(BATCH/"school_exam_blueprint.json")
        summary=validate_blueprint(exam)
        self.assertEqual(summary["courses"],5)
        self.assertEqual(exam["programme_target_course_count"],8)
        self.assertFalse(exam["curriculum_complete"])
        self.assertEqual(len(exam["remaining_curriculum_titles"]),3)
        for code in exam["required_courses"]:
            self.assertEqual(sum(i["type"]=="MCQ" and i["course_codes"]==[code] for i in exam["items"]),8)
        result=dict(school_code="ERT",curriculum_version=exam["curriculum_version"],completed_courses=exam["required_courses"],status="finalized",moderation_status="approved",
            item_results=[dict(id=i["id"],score=i["marks"],marking_status="marked",human_marker_id="test-marker") for i in exam["items"]])
        self.assertFalse(review_result_contract(exam,result,verified_transport=True)["certificate_authorised"])

class ErtReviewStagingTests(TestCase):
    def test_ert_additions_preserve_existing_course_cbt_and_other_school(self):
        ert=School.objects.create(name="ERT draft",code="ERT",target_course_count=8,enrollment_open=False)
        original=Course.objects.create(school=ert,course_code="SWP-032",title="Retained ERT",content="Protected original",paralearn_assessment_id="existing-cbt")
        fsw=School.objects.create(name="FSW",code="FSW",enrollment_open=False)
        other=Course.objects.create(school=fsw,course_code="SWP-035",title="Existing FSW",content="Protected FSW",is_active=False)
        before=list(Course.objects.order_by("pk").values())
        with TemporaryDirectory() as temporary:
            receipt=Path(temporary)/"new.json"
            call_command("stage_authored_review",package=BATCH/"review_package.json",commit=True,receipt=receipt,stdout=io.StringIO())
            audit=read(receipt.with_suffix(".applied.json"))
        self.assertEqual(audit["before"],audit["after"])
        self.assertEqual(list(Course.objects.filter(pk__in=[original.pk,other.pk]).order_by("pk").values()),before)
        self.assertEqual(ert.courses.count(),5)
        ert.refresh_from_db();self.assertEqual(ert.target_course_count,8);self.assertFalse(ert.enrollment_open)
        for row in ert.courses.exclude(pk=original.pk):
            self.assertFalse(row.is_active);self.assertEqual(row.paralearn_assessment_id,"");self.assertEqual(row.modules.count(),3)
