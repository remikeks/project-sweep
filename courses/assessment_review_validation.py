"""Read-only structural checks for unpublished curriculum assessment drafts."""

import re
import unicodedata
from collections import Counter


class AssessmentReviewError(ValueError):
    pass


def normalise(text):
    return re.sub(r"[\W_]+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def validate_review_bank(bank, catalogue, existing_stems=()):
    """Validate review data, never infer approval or a remote assessment ID."""
    def require(condition, message):
        if not condition:
            raise AssessmentReviewError(message)

    require(bank.get("status") == "draft_for_review", "Bank must remain draft_for_review")
    require(bank.get("assessment_id") is None, "Local drafts cannot claim a remote assessment ID")
    require(bank.get("course_code") == catalogue["code"], "Course code mismatch")
    require(bank.get("title") == catalogue["title"], "Course title mismatch")
    require(bank.get("course_slug") == catalogue["slug"], "Course slug mismatch")
    require(bank.get("version") == "0.1.0", "Unsupported review version")
    require(bank.get("proposed_pass_percent") == 70, "Unexpected proposed pass mark")
    require(bank.get("minimum_correct") == 11, "Whole-mark threshold must round upward")
    require(bank.get("source_hash_encoding") == "canonical-json-sorted-keys-utf8", "Unknown source hash encoding")
    require(bool(re.fullmatch(r"[a-f0-9]{64}", bank.get("catalogue_sha256", ""))), "Missing catalogue checksum")
    require(bool(re.fullmatch(r"[a-f0-9]{64}", bank.get("authoring_source_sha256", ""))), "Missing authoring checksum")
    modules = bank.get("modules", [])
    require([m["order"] for m in modules] == [1, 2, 3], "Expected three ordered modules")
    require([m["title"] for m in modules] == [m["title"] for m in catalogue["modules"]], "Module titles mismatch")
    points = {}
    for module in modules:
        require(bool(module.get("outcome", "").strip()), "Missing measurable module outcome")
        require(len(module.get("teaching_points", [])) == 5, "Expected five teaching points per module")
        for point in module["teaching_points"]:
            require(point["id"] not in points, "Duplicate teaching-point ID")
            require(bool(point.get("text", "").strip()), "Empty teaching point")
            points[point["id"]] = module["order"]
    questions = bank.get("questions", [])
    require(len(questions) == 15, "Expected 15 questions")
    require(Counter(q.get("module_order") for q in questions) == {1: 5, 2: 5, 3: 5}, "Expected five questions per module")
    require(Counter(q.get("teaching_point_id") for q in questions) == Counter({p: 1 for p in points}), "Each teaching point needs one question")
    ids, seen = set(), {normalise(s) for s in existing_stems}
    for question in questions:
        qid = question.get("id", "")
        require(qid.startswith(bank["course_code"] + "-Q"), "Question ID must belong to course")
        require(qid not in ids, "Duplicate question ID")
        ids.add(qid)
        stem = normalise(question.get("question", ""))
        require(bool(stem) and stem not in seen, "Empty or duplicate question stem")
        seen.add(stem)
        require(points.get(question.get("teaching_point_id")) == question["module_order"], "Question teaching-point module mismatch")
        require(question.get("marks") == 1 and question.get("type") == "MCQ", "Expected one-mark MCQ")
        options = question.get("options", [])
        require(len(options) == 4, "Expected four options")
        require(all(type(o.get("correct")) is bool for o in options), "Answer keys must be booleans")
        require(sum(o["correct"] for o in options) == 1, "Expected exactly one correct answer")
        texts = [normalise(o.get("text", "")) for o in options]
        require(all(texts) and len(set(texts)) == 4, "Options must be non-empty and distinct")
        require(bool(question.get("rationale", "").strip()), "Missing rationale")
    return {"course_code": bank["course_code"], "questions": len(questions), "modules": len(modules)}
