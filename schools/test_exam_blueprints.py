import json
from pathlib import Path
from django.test import SimpleTestCase

from schools.exam_blueprints import review_result_contract, validate_blueprint

PATH = Path(__file__).resolve().parents[1] / "production_courseware/phase_two/fsw_batch_01/school_exam_blueprint.json"


class SchoolExamBlueprintTests(SimpleTestCase):
    def setUp(self):
        self.blueprint=json.loads(PATH.read_text())

    def result(self):
        return dict(school_code="FSW",curriculum_version=self.blueprint["curriculum_version"],
            completed_courses=self.blueprint["required_courses"],status="finalized",moderation_status="approved",
            item_results=[dict(id=i["id"],score=i["marks"],marking_status="marked",human_marker_id="test-marker") for i in self.blueprint["items"]])

    def test_valid_draft_never_claims_launch_readiness(self):
        summary=validate_blueprint(self.blueprint)
        self.assertEqual(summary["marks"],100)
        self.assertFalse(summary["ready_for_launch"])

    def test_omitted_course_coverage_is_rejected(self):
        for i in self.blueprint["items"][:8]:
            i["course_codes"]=["SWP-017"]
        with self.assertRaisesRegex(ValueError,"Every curriculum course"):
            validate_blueprint(self.blueprint)

    def test_missing_rubric_or_human_marking_is_rejected(self):
        item=self.blueprint["items"][-1]
        item["rubric"]=[]
        with self.assertRaisesRegex(ValueError,"rubric"):
            validate_blueprint(self.blueprint)

    def test_pending_written_marking_cannot_satisfy_contract(self):
        result=self.result()
        result["item_results"][-1]["marking_status"]="ai_suggested"
        checked=review_result_contract(self.blueprint,result,verified_transport=True)
        self.assertFalse(checked["contract_checks_passed"])
        self.assertIn("Written answer awaits human marking",checked["reasons"])

    def test_grade_identity_and_authentication_are_required(self):
        result=self.result()
        result["curriculum_version"]="different"
        result["status"]="submitted"
        checked=review_result_contract(self.blueprint,result)
        self.assertFalse(checked["contract_checks_passed"])
        self.assertGreaterEqual(len(checked["reasons"]),3)

    def test_missing_duplicate_and_nonfinite_scores_fail(self):
        for value in (float("nan"),"Infinity",-1,True,16):
            result=self.result()
            result["item_results"][-1]["score"]=value
            self.assertFalse(review_result_contract(self.blueprint,result,verified_transport=True)["contract_checks_passed"])
        result=self.result()
        result["item_results"][-1]=result["item_results"][0]
        self.assertFalse(review_result_contract(self.blueprint,result,verified_transport=True)["contract_checks_passed"])

    def test_complete_offline_result_still_cannot_authorise_certificate(self):
        checked=review_result_contract(self.blueprint,self.result(),verified_transport=True)
        self.assertTrue(checked["contract_checks_passed"])
        self.assertEqual(checked["score"],"100")
        self.assertFalse(checked["certificate_authorised"])
