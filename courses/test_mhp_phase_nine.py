"""MHP completion breadth, non-live mixed exam and additive retained-data proof."""
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
BATCH=ROOT/"production_courseware/phase_nine/mhp_batch_01"
MEDIA=ROOT/"production_courseware/phase_nine/mhp_media_01"

class MhpCompletionSourceTests(SimpleTestCase):
    def test_dated_deterministic_sources_and_sixty_questions_against_330_prior_stems(self):
        compiler=module(ROOT/"scripts/build_course_review_batch.py","mhp9_compiler")
        source=module(BATCH/"authoring.py","mhp9_source")
        package=read(BATCH/"review_package.json")
        self.assertEqual(compiler.compile_package(source),package)
        self.assertEqual(validate_package(package),dict(courses=4,modules=12,questions=60))
        self.assertEqual(package["evidence_checked_on"],"2026-11-15")
        self.assertEqual(package["review"]["clinical_and_child_safeguarding"],"pending")
        prior=[]
        for path in ["phase_two/fsw_batch_01","phase_four/fsw_batch_02","phase_five/ert_batch_01","phase_six/ert_batch_02","phase_seven/gbv_batch_01","phase_eight/gbv_batch_02"]:
            prior.extend(q["question"] for c in read(ROOT/"production_courseware"/path/"review_package.json")["courses"] for q in c["assessment"]["questions"])
        self.assertEqual(len(prior),330)
        for c in package["courses"]:
            self.assertEqual(c["school_code"],"MHP")
            self.assertIn("fictional",c["study_guidance"])
            self.assertIn("fictional",c["practice_safety_note"])
            validate_review_bank(c["assessment"],dict(code=c["code"],title=c["title"],slug=c["slug"],modules=c["modules"]),existing_stems=prior)
            prior.extend(q["question"] for q in c["assessment"]["questions"])

    def test_full_ten_course_exam_covers_retained_domains_and_all_written_courses(self):
        exam=read(BATCH/"school_exam_blueprint.json")
        builder=module(ROOT/"scripts/build_mhp_ten_course_exam.py","mhp9_exam")
        self.assertEqual(exam,builder.blueprint())
        self.assertEqual(validate_blueprint(exam),dict(courses=10,items=48,marks=100,unbound_mcqs=40,ready_for_launch=False))
        originals = [c for c in read(ROOT/"production_courseware/release-2026-10-03/course_catalogue.json") if 4 <= c["number"] <= 9]
        new=read(BATCH/"review_package.json")
        self.assertEqual(exam["required_courses"], [c["code"] for c in originals+new["courses"]])
        self.assertEqual(exam["retained_catalogue_domains"], [{k:c[k] for k in ["code","title","outcome","modules","cbt_focus"]} for c in originals])
        for code in exam["required_courses"]:
            self.assertEqual(sum(i["type"]=="MCQ" and i["course_codes"]==[code] for i in exam["items"]),4)
        self.assertEqual({c for i in exam["items"] if i["type"]=="SHORT_ANSWER" for c in i["course_codes"]},set(exam["required_courses"]))
        for item in [i for i in exam["items"] if i["type"]=="ESSAY"]:
            self.assertEqual(set(item["course_codes"]),set(exam["required_courses"]))
        self.assertTrue(exam["draft_catalogue_complete"]);self.assertFalse(exam["curriculum_complete"])
        self.assertFalse(exam["certification"]["authorised"])

    def test_perfect_offline_exam_cannot_certify_and_missing_courses_or_moderation_fail(self):
        exam=read(BATCH/"school_exam_blueprint.json")
        result=dict(school_code="MHP",curriculum_version=exam["curriculum_version"],completed_courses=exam["required_courses"],status="finalized",moderation_status="approved",
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
        self.assertEqual({r["school_code"] for r in manifest},{"MHP"})
        self.assertEqual({r["course_code"] for r in manifest},{f"SWP-{n:03}" for n in [57,58,59,60]})
        for path in ["phase_three/fsw_media_01","phase_four/fsw_media_02","phase_five/ert_media_01","phase_six/ert_media_02","phase_seven/gbv_media_01","phase_eight/gbv_media_02"]:
            release=ROOT/"production_courseware"/path
            validate_manifest(read(release/"upload_manifest.json"),release=release,profile="pdf_slides")

    def test_guides_and_worksheets_embed_fonts_and_keep_all_safety_notes(self):
        from pypdf import PdfReader
        for row in read(MEDIA/"upload_manifest.json"):
            if row["asset_type"] not in {"learner_guide", "worksheet"}:
                continue
            pdf=PdfReader(MEDIA/row["path"])
            for page in pdf.pages:
                fonts=[f.get_object() for f in page["/Resources"]["/Font"].values()]
                embedded=[f for f in fonts if f.get("/FontDescriptor") and
                          f["/FontDescriptor"].get("/FontFile2")]
                self.assertGreaterEqual(len(embedded),2,"Portable regular and bold fonts required")
                if row["asset_type"]=="worksheet":
                    self.assertIn("Do not collect personal trauma histories"," ".join(page.extract_text().split()))

class MhpCompletionStagingTests(TestCase):
    def test_additions_preserve_six_original_cbts_drafts_learners_credentials_and_reject_replay(self):
        from django.contrib.auth import get_user_model
        from django.core.management.base import CommandError
        from learning.models import CourseEnrollment, CourseProgress
        from credentials.models import Badge, Certificate
        from courses.management.commands.stage_authored_review import snapshot
        mhp=School.objects.create(name="MHP",code="MHP",target_course_count=10,enrollment_open=False)
        originals=[]
        for c in read(ROOT/"production_courseware/release-2026-10-03/course_catalogue.json"):
            if 4 <= c["number"] <= 9:
                row=Course.objects.create(school=mhp,course_code=c["code"],title=c["title"],content="Protected original teaching",paralearn_assessment_id="fixture-cbt-"+c["code"])
                for m in c["modules"]:
                    CourseModule.objects.create(course=row,order=m["order"],title=m["title"],content=m["focus"])
                originals.append(row)
        other=School.objects.create(name="GBV",code="GBV",enrollment_open=False)
        Course.objects.create(school=other,course_code="SWP-053",title="Protected previous draft",content="Protected",is_active=False)
        user=get_user_model().objects.create_user(username="preserved-learner",password="fixture-only")
        CourseEnrollment.objects.create(user=user,course=originals[0])
        CourseProgress.objects.create(user=user,course=originals[0],best_score=90,status="completed")
        Badge.objects.create(user=user,course=originals[0])
        Certificate.objects.create(user=user,school=mhp)
        before=snapshot()
        with TemporaryDirectory() as temporary:
            receipt=Path(temporary)/"new.json"
            call_command("stage_authored_review",package=BATCH/"review_package.json",commit=True,receipt=receipt,stdout=io.StringIO())
            proof=read(receipt.with_suffix(".applied.json"))
            self.assertEqual(before,proof["before"])
            self.assertEqual(proof["before"],proof["after"])
            after=snapshot()
            with self.assertRaises(CommandError):
                call_command("stage_authored_review",package=BATCH/"review_package.json",commit=True,receipt=Path(temporary)/"replay.json",stdout=io.StringIO())
            self.assertEqual(after,snapshot())
        self.assertEqual(mhp.courses.count(),10)
        for old in originals:
            old.refresh_from_db()
            self.assertEqual(old.paralearn_assessment_id,"fixture-cbt-"+old.course_code)
            self.assertTrue(old.is_active)
            self.assertEqual(old.modules.count(),3)
        mhp.refresh_from_db();self.assertFalse(mhp.enrollment_open)
        for row in Course.objects.filter(pk__in=proof["new_course_ids"]):
            self.assertFalse(row.is_active);self.assertEqual(row.paralearn_assessment_id,"");self.assertEqual(row.modules.count(),3)
