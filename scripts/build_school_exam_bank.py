"""Build fact-bound school certification items from the approved course outline."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def title_case(value: str) -> str:
    return value[:1].upper() + value[1:] if value else value


def options(correct: str, *distractors: str) -> list[dict]:
    choices = [(correct, True), *[(text, False) for text in distractors]]
    # Stable ordering avoids making the correct response predictably first while
    # keeping repeated releases reproducible.
    choices.sort(key=lambda item: hashlib.sha256(item[0].encode("utf-8")).hexdigest())
    return [{"text": text, "is_correct": is_correct, "order": index + 1} for index, (text, is_correct) in enumerate(choices)]


def module_items(course: dict) -> list[dict]:
    items = []
    for module in course["modules"]:
        items.append(
            {
                "text": (
                    f"According to the {course['title']} course, which topic belongs in the module "
                    f"{module['title']}?"
                ),
                "choices": options(
                    title_case(module["focus"]),
                    "A topic reserved for a different module in the course",
                    "A local procedure that must be verified before use",
                    "A claim that is not part of the approved course outline",
                ),
                "objective": module["title"],
            }
        )
    return items


def integrated_items(school: str, courses: list[dict]) -> list[dict]:
    first, second, third = courses
    return [
        {
            "text": f"Which statement best describes the shared learning approach in the {school} catalogue?",
            "choices": options(
                "Use the course material with the governing local law, organisational policy, supervision requirements, and approved referral pathways.",
                "Treat the course material as a replacement for every local procedure.",
                "Use a single international rule without checking the delivery setting.",
                "Ignore the learner's scope of role when applying course content.",
            ),
            "objective": "safe local application",
        },
        {
            "text": "What information should a learner leave out of a course worksheet or assessment response?",
            "choices": options(
                "Identifying details about a client, family, patient, student, colleague, or community member.",
                "A de-identified explanation of the learning activity.",
                "A question about information that needs verification.",
                "A reflection on when supervision may be needed.",
            ),
            "objective": "confidentiality and de-identification",
        },
        {
            "text": f"Which course outcome is associated with {first['title']}?",
            "choices": options(
                first["outcome"],
                second["outcome"],
                third["outcome"],
                "A course outcome not included in the approved catalogue.",
            ),
            "objective": first["title"],
        },
        {
            "text": f"Which course outcome is associated with {second['title']}?",
            "choices": options(
                second["outcome"],
                first["outcome"],
                third["outcome"],
                "A course outcome not included in the approved catalogue.",
            ),
            "objective": second["title"],
        },
        {
            "text": f"Which course outcome is associated with {third['title']}?",
            "choices": options(
                third["outcome"],
                first["outcome"],
                second["outcome"],
                "A course outcome not included in the approved catalogue.",
            ),
            "objective": third["title"],
        },
        {
            "text": "When a decision is outside a learner's authority, competence, or supervision arrangement, what does the course material direct the learner to do?",
            "choices": options(
                "Pause and use the correct local consultation, escalation, referral, or handover route.",
                "Make a final decision without checking the applicable procedure.",
                "Use a fictional example as a substitute for local guidance.",
                "Omit the issue from documentation and reflection.",
            ),
            "objective": "professional limits and escalation",
        },
    ]


def build_bank(catalogue: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for course in catalogue:
        grouped[course["school"]].append(course)
    bank = []
    for school, courses in grouped.items():
        if len(courses) != 3:
            raise ValueError(f"Expected three courses for {school}, found {len(courses)}.")
        questions = []
        for course in courses:
            questions.extend(module_items(course))
        questions.extend(integrated_items(school, courses))
        if len(questions) != 15:
            raise ValueError(f"Expected 15 questions for {school}, found {len(questions)}.")
        for order, question in enumerate(questions, start=1):
            question["order"] = order
        bank.append({"school": school, "passing_score": 70, "questions": questions})
    if len(bank) != 10:
        raise ValueError(f"Expected ten schools, found {len(bank)}.")
    return bank


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalogue = json.loads(args.catalogue.read_text(encoding="utf-8"))
    bank = build_bank(catalogue)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bank, indent=2), encoding="utf-8")
    print(f"Built {sum(len(entry['questions']) for entry in bank)} questions across {len(bank)} school exams.")


if __name__ == "__main__":
    main()
