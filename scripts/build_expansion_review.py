"""Build or check local assessment-review packs. No database or network access."""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from courses.assessment_review_validation import validate_review_bank

REVIEW = ROOT / "production_courseware/expansion_review"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_fingerprint(value):
    # Stable across Git's Windows/Unix newline conversion and harmless indentation changes.
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def build():
    source_bytes = (REVIEW / "assessment_source.json").read_bytes()
    source = json.loads(source_bytes)
    if source["status"] != "draft_for_review" or source["version"] != "0.1.0":
        raise ValueError("Authoring source must be review version 0.1.0")
    if {c["code"] for c in source["courses"]} != {f"SWP-{n:03d}" for n in range(31, 35)} or len(source["courses"]) != 4:
        raise ValueError("Expected exactly the four expansion courses")
    existing = []
    baseline_files = sorted((ROOT / "production_courseware/qa").glob("paralearn-swp-*-questions.json"))
    for path in baseline_files:
        existing.extend(q["question"] for q in json.loads(path.read_text(encoding="utf-8"))["questions"])
    outputs, manifest = {}, []
    for course in source["courses"]:
        catalogue_path = ROOT / "production_courseware/drafts" / course["draft"] / "course_catalogue.json"
        catalogue_bytes = catalogue_path.read_bytes()
        catalogue = json.loads(catalogue_bytes)[0]
        if catalogue["code"] != course["code"]:
            raise ValueError("Authoring source refers to the wrong course catalogue")
        bank = {
            "course_code": course["code"], "title": catalogue["title"], "course_slug": catalogue["slug"],
            "version": source["version"], "status": "draft_for_review", "assessment_id": None,
            "proposed_pass_percent": 70, "minimum_correct": 11,
            "catalogue_path": catalogue_path.relative_to(ROOT).as_posix(),
            "catalogue_sha256": json_fingerprint(json.loads(catalogue_bytes)),
            "authoring_source_sha256": json_fingerprint(source),
            "source_hash_encoding": "canonical-json-sorted-keys-utf8",
            "reference_framework": course["reference"], "modules": [], "questions": [],
        }
        if [m["order"] for m in course["modules"]] != [1, 2, 3]:
            raise ValueError("Authoring modules must be ordered 1, 2, 3")
        # Balanced key positions, reproducibly shuffled per course (not a repeating ABCD pattern).
        rng = random.Random(course["code"] + ":" + source["version"])
        positions = [0, 1, 2, 3] * 3 + [0, 1, 2]
        rng.shuffle(positions)
        for module, catalogue_module in zip(course["modules"], catalogue["modules"]):
            teaching = []
            for point_no, row in enumerate(module["items"], 1):
                point, stem, correct, distractors, rationale = row
                if len(distractors) != 3:
                    raise ValueError("Every item needs three distractors")
                point_id = f"{course['code']}-M{module['order']}-P{point_no}"
                teaching.append({"id": point_id, "text": point})
                qno = len(bank["questions"]) + 1
                wrong = list(distractors)
                rng.shuffle(wrong)
                options = [{"text": text, "correct": False} for text in wrong]
                options.insert(positions[qno - 1], {"text": correct, "correct": True})
                bank["questions"].append({
                    "id": f"{course['code']}-Q{qno:02d}", "module_order": module["order"],
                    "teaching_point_id": point_id, "question": stem, "type": "MCQ", "marks": 1,
                    "options": options, "rationale": rationale,
                })
            bank["modules"].append({"order": module["order"], "title": catalogue_module["title"],
                                    "outcome": module["outcome"], "teaching_points": teaching})
        validate_review_bank(bank, catalogue, existing)
        existing.extend(q["question"] for q in bank["questions"])
        stem = course["code"].lower()
        json_text = json.dumps(bank, ensure_ascii=False, indent=2) + "\n"
        outputs[f"{stem}-assessment-review.json"] = json_text
        lines = [f"# {course['code']} — {bank['title']}", "", "Draft 0.1.0 — NOT approved or imported into ParaLearn.", "",
                 "15 questions; five per module; one mark each. Proposed pass: 11/15 (70% threshold rounded upward).", "",
                 "These teaching notes are review material, not a replacement for the complete learner package.", "",
                 f"Reference framework: {course['reference']}. See README for source links and limitations.", ""]
        for module in bank["modules"]:
            lines.extend([f"## Module {module['order']}: {module['title']}", "", f"Outcome: {module['outcome']}", "", "### Teaching notes", ""])
            for point in module["teaching_points"]:
                lines.extend([f"- **{point['id']}**: {point['text']}", ""])
            lines.extend(["### Assessment items", ""])
            for question in (q for q in bank["questions"] if q["module_order"] == module["order"]):
                lines.extend([f"#### {question['id']}", "", question["question"], ""])
                for label, option in zip("ABCD", question["options"]):
                    lines.append(f"- {label}. {option['text']}" + (" **[Key]**" if option["correct"] else ""))
                lines.extend(["", f"Rationale: {question['rationale']}", "", f"Teaching link: {question['teaching_point_id']}", ""])
        outputs[f"{stem}-assessment-review.md"] = "\n".join(lines)
        manifest.append({"course_code": course["code"], "questions": 15,
                         "json": f"{stem}-assessment-review.json", "sha256": sha256(json_text.encode("utf-8"))})
    outputs["review_manifest.json"] = json.dumps({
        "status": "draft_for_review", "version": source["version"], "banks": manifest,
        "bank_hash_encoding": "utf8-lf",
        "baseline_comparison": {"local_banks": len(baseline_files), "limitation": "Exact normalised stems only; SWP-001–006 local exports absent. Semantic overlap needs human review."},
    }, indent=2) + "\n"
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated files match source without writing")
    args = parser.parse_args()
    outputs = build()
    for name, content in outputs.items():
        path = REVIEW / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Outdated or missing review artifact: {name}")
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    print(f"{'Verified' if args.check else 'Built'} four review banks: 60 questions, 12 modules, 60 teaching links. No publication or remote changes.")


if __name__ == "__main__":
    main()
