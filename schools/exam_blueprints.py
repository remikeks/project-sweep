"""Internal mixed-exam authoring contract. This is not a ParaLearn API schema.

Validation proves structural coverage only. It cannot approve content, establish
provider support, finalise a grade or authorise a certificate.
"""
from collections import Counter
from decimal import Decimal, InvalidOperation


def validate_blueprint(blueprint):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(blueprint.get("status") == "draft_for_review", "Blueprint must remain a draft")
    require(blueprint.get("provider") == "ParaLearn CBT", "School exams must use ParaLearn CBT")
    require(blueprint.get("provider_assessment_id") is None, "An unverified draft cannot claim a provider exam")
    require(blueprint.get("provider_contract_verified") is False, "Draft provider support must not be inferred")
    codes = blueprint.get("required_courses", [])
    require(5 <= len(codes) <= 10 and len(set(codes)) == len(codes), "Expected five to ten unique curriculum courses")
    require(blueprint.get("curriculum_version") and blueprint.get("school_code"), "Missing curriculum identity")
    items = blueprint.get("items", [])
    require(Counter(i["type"] for i in items) == {"MCQ":40, "SHORT_ANSWER":6, "ESSAY":2}, "Expected 40 MCQs, six short answers and two essays")
    require(len({i["id"] for i in items}) == len(items), "Duplicate exam item identity")
    marks = {"MCQ":1, "SHORT_ANSWER":5, "ESSAY":15}
    coverage = Counter()
    written_coverage = set()
    for item in items:
        require(item["marks"] == marks[item["type"]], "Incorrect item weighting")
        require(bool(item["course_codes"]) and set(item["course_codes"]) <= set(codes), "Item refers to an unknown or missing course")
        if item["type"] == "MCQ":
            require(len(item["course_codes"]) == 1, "MCQ coverage must identify one primary course")
            coverage.update(item["course_codes"])
            require(item.get("question_binding") is None, "Unreviewed blueprint slots must remain unbound")
        else:
            written_coverage.update(item["course_codes"])
            require(item.get("prompt") and item.get("model_answer"), "Written question needs a prompt and marking guidance")
            rubric = item.get("rubric", [])
            require(rubric and all(r.get("criterion") and type(r.get("marks")) is int and r["marks"] > 0 for r in rubric), "Missing written rubric")
            require(sum(r["marks"] for r in rubric) == item["marks"], "Rubric marks must match item marks")
            require(item.get("human_marking_required") is True, "Written answers require human marking")
    require(all(coverage[c] >= 2 for c in codes), "Every curriculum course needs at least two MCQs")
    require(written_coverage == set(codes), "Written questions must collectively cover every curriculum course")
    require(sum(i["marks"] for i in items) == 100, "Exam must total 100 marks")
    policy = blueprint.get("marking_policy", {})
    require(policy.get("moderation_required") is True and policy.get("ai_only_finalisation") is False, "Written results require moderation and cannot be finalised by AI alone")
    require(policy.get("proposed_pass_percent") == 70, "Unexpected proposed pass mark")
    return {"courses":len(codes), "items":len(items), "marks":100, "unbound_mcqs":40, "ready_for_launch":False}


def review_result_contract(blueprint, result, *, verified_transport=False):
    """Offline acceptance checks for future integration; never issues a credential.

    Only a future authenticated server adapter may set verified_transport. No
    existing webhook or learner endpoint calls this function.
    """
    validate_blueprint(blueprint)
    reasons = []
    if not verified_transport:
        reasons.append("Provider result has not been authenticated and reconciled")
    if result.get("school_code") != blueprint["school_code"] or result.get("curriculum_version") != blueprint["curriculum_version"]:
        reasons.append("School or curriculum identity mismatch")
    if set(result.get("completed_courses", [])) != set(blueprint["required_courses"]):
        reasons.append("Required course completions are incomplete or mismatched")
    if result.get("status") != "finalized" or result.get("moderation_status") != "approved":
        reasons.append("Marking and moderation are not final")
    expected = {i["id"]:i for i in blueprint["items"]}
    rows = result.get("item_results", [])
    if len(rows) != len(expected) or {r.get("id") for r in rows} != set(expected):
        reasons.append("Missing or duplicate item results")
    score = Decimal(0)
    for row in rows:
        item = expected.get(row.get("id"))
        if not item:
            continue
        try:
            if isinstance(row.get("score"), bool):
                raise ValueError()
            value = Decimal(str(row.get("score")))
            if not value.is_finite() or not Decimal(0) <= value <= item["marks"]:
                raise ValueError()
            score += value
        except (InvalidOperation, ValueError):
            reasons.append("Invalid item score")
        if item["type"] != "MCQ" and (row.get("marking_status") != "marked" or not row.get("human_marker_id")):
            reasons.append("Written answer awaits human marking")
    if score < blueprint["marking_policy"]["proposed_pass_percent"]:
        reasons.append("School exam pass threshold not met")
    # This authoring contract intentionally cannot turn on certification.
    return {"contract_checks_passed":not reasons, "reasons":sorted(set(reasons)),
            "score":str(score), "certificate_authorised":False,
            "release_blockers":["Draft curriculum and question bindings", "Live ParaLearn mixed-exam verification", "Approved signatories"]}
