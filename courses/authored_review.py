"""Validate complete additive teaching drafts before any database operation."""
import hashlib
import json
import re

from courses.assessment_review_validation import validate_review_bank


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def lesson_text(module, references=()):
    refs = [r for r in references if r["id"] in module["sources"]]
    return "\n\n".join([*module["paragraphs"], "Worked case\n" + module["example"],
                        "Practice activity\n" + module["activity"], "Feedback\n" + module["feedback"],
                        *[f"[{r['id']}] {r['author']} ({r['year']}). {r['title']}. {r['url']}\nEvidence note: {r['appraisal']}" for r in refs]])


def course_values(course, references=()):
    return dict(title=course["title"], slug=course["slug"], course_code=course["code"],
                summary=course["outcome"], description=course["outcome"] + "\n\n" + course["audience"],
                learning_objectives="\n".join(m["outcome"] for m in course["modules"]),
                content="\n\n".join(m["title"] + "\n\n" + lesson_text(m, references) for m in course["modules"]),
                estimated_minutes=course["estimated_minutes"], passing_score=70, is_active=False)


def validate_package(package):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(package.get("status") == "draft_for_review", "Package must remain a draft")
    require(package.get("version") == "0.1.0", "Unsupported version")
    sources = package.get("references", [])
    source_ids = {r["id"] for r in sources}
    require(len(source_ids) == len(sources) > 0, "Missing or duplicate references")
    for ref in sources:
        require(all(ref.get(k) for k in ("title", "url", "kind", "use", "appraisal", "licence")), "Incomplete evidence record")
    courses = package.get("courses", [])
    require(bool(courses), "Empty package")
    require(len({c["code"] for c in courses}) == len(courses), "Duplicate course code")
    require(len({c["slug"] for c in courses}) == len(courses), "Duplicate course slug")
    require(len({c["title"].casefold() for c in courses}) == len(courses), "Duplicate course title")
    all_stems = []
    for course in courses:
        require(re.fullmatch(r"SWP-\d{3}", course["code"]), "Invalid course code")
        require(60 <= course["estimated_minutes"] <= 1200, "Unrealistic estimated time")
        require(len(course["title"]) <= 200 and len(course["outcome"]) <= 300, "Course field too long")
        require([m["order"] for m in course["modules"]] == [1, 2, 3], "Expected three ordered modules")
        for module in course["modules"]:
            require(len(" ".join(module["paragraphs"]).split()) >= 250, "Module teaching is incomplete")
            require(all(module.get(k) for k in ("outcome", "example", "activity", "feedback", "sources")), "Missing lesson component")
            require(set(module["sources"]) <= source_ids, "Unknown module reference")
            cited = set(re.findall(r"\b(?:S|R)\d+\b", " ".join(module["paragraphs"])))
            require(set(module["sources"]) == cited, "Module reference list must match in-text citations")
        bank = course["assessment"]
        require(bank["authoring_source_sha256"] == digest({k:v for k,v in course.items() if k != "assessment"}), "Authoring checksum mismatch")
        catalogue = dict(code=course["code"], title=course["title"], slug=course["slug"], modules=course["modules"])
        require(bank["catalogue_sha256"] == digest(catalogue), "Catalogue checksum mismatch")
        validate_review_bank(bank, catalogue, existing_stems=all_stems)
        all_stems.extend(q["question"] for q in bank["questions"])
    return {"courses":len(courses), "modules":sum(len(c["modules"]) for c in courses), "questions":len(all_stems)}
