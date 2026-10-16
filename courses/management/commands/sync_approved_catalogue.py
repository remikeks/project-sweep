"""Synchronise the approved SWEEP course catalogue and certification items.

This command never runs by accident: --commit is required for database writes,
and replacing a school exam needs its own explicit flag. It preserves learner
records and course assets; it only updates the approved catalogue fields,
course modules, and the requested school exam bank.
"""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.curriculum_validation import CurriculumValidationError, validate_catalogue as validate_release_catalogue
from courses.models import Course, CourseModule
from schools.models import School, SchoolExamChoice, SchoolExamQuestion


def as_text(value) -> str:
    return str(value or "").strip()


def module_content(course: dict, module: dict) -> str:
    return (
        f"This module focuses on {module['focus']}. It supports the course outcome: {course['outcome']} "
        "Use the approved learner guide and local policy to distinguish what is known, what needs verification, "
        "and when consultation, escalation, referral, or handover is needed."
    )


def validate_catalogue(catalogue: list[dict], exams: list[dict]) -> dict[str, int]:
    try:
        catalogue_summary = validate_release_catalogue(catalogue)
    except CurriculumValidationError as exc:
        raise CommandError(str(exc)) from exc
    if not isinstance(exams, list) or len(exams) != 10:
        raise CommandError("The school exam bank must contain exactly ten schools.")
    catalogue_schools = {as_text(row.get("school")) for row in catalogue}
    exam_schools = {as_text(row.get("school")) for row in exams}
    if catalogue_schools != exam_schools:
        raise CommandError("The catalogue and school exam bank must cover the same ten schools.")
    for exam in exams:
        questions = exam.get("questions")
        if not isinstance(questions, list) or len(questions) != 15:
            raise CommandError(f"{exam.get('school', 'A school')} must have exactly 15 certification questions.")
        for question in questions:
            choices = question.get("choices")
            if not isinstance(choices, list) or len(choices) != 4:
                raise CommandError("Every certification question must have four choices.")
            if sum(bool(choice.get("is_correct")) for choice in choices) != 1:
                raise CommandError("Every certification question must have exactly one correct choice.")
    return catalogue_summary


class Command(BaseCommand):
    help = "Synchronise an approved ten-school catalogue, three modules per course, and 15 certification questions per school."

    def add_arguments(self, parser):
        parser.add_argument("--catalogue", type=Path, required=True)
        parser.add_argument("--exam-bank", type=Path, required=True)
        parser.add_argument(
            "--replace-school-exams",
            action="store_true",
            help="Replace only the certification questions for schools in the supplied exam bank.",
        )
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Write the approved catalogue after validation. Without this flag the command validates only.",
        )
        parser.add_argument(
            "--create-missing-courses",
            action="store_true",
            help="Create a course absent from the database. Requires --commit and should only follow curriculum approval.",
        )

    def handle(self, *args, **options):
        catalogue_path = options["catalogue"].resolve()
        exam_path = options["exam_bank"].resolve()
        if not catalogue_path.is_file() or not exam_path.is_file():
            raise CommandError("Both --catalogue and --exam-bank must point to existing JSON files.")
        try:
            catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
            exams = json.loads(exam_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError("The supplied catalogue files must be valid JSON.") from exc
        catalogue_summary = validate_catalogue(catalogue, exams)
        if options["create_missing_courses"] and not options["commit"]:
            raise CommandError("--create-missing-courses requires --commit.")
        if not options["commit"]:
            self.stdout.write(self.style.SUCCESS(
                f"Validated {catalogue_summary['courses']} courses, {catalogue_summary['modules']} modules, "
                "and 150 school certification questions. No database changes were made."
            ))
            return

        exams_by_school = {entry["school"]: entry for entry in exams}
        with transaction.atomic():
            schools = {school.name: school for school in School.objects.select_for_update().all()}
            missing_schools = sorted({entry["school"] for entry in catalogue} - set(schools))
            if missing_schools:
                raise CommandError(
                    "The catalogue schools do not exist. Run the non-destructive seed_data command first: "
                    + ", ".join(missing_schools)
                )
            updated_courses = 0
            created_courses = 0
            updated_modules = 0
            for entry in catalogue:
                school = schools[entry["school"]]
                try:
                    course = Course.objects.select_for_update().get(school=school, title=entry["title"])
                except Course.DoesNotExist as exc:
                    if not options["create_missing_courses"]:
                        raise CommandError(f"Course is missing from {school.name}: {entry['title']}") from exc
                    next_order = (school.courses.order_by("-order", "-id").values_list("order", flat=True).first() or 0) + 1
                    course = Course.objects.create(
                        school=school,
                        title=entry["title"],
                        slug=entry["slug"],
                        course_code=entry["code"],
                        order=next_order,
                    )
                    created_courses += 1
                course.course_code = entry["code"]
                # Keep the course's canonical URL aligned with the release manifest.
                course.slug = entry["slug"]
                course.summary = entry["outcome"][:300]
                course.description = entry["outcome"]
                course.learning_objectives = "\n".join(
                    [entry["outcome"], *[f"Apply the key ideas from {module['title']}." for module in entry["modules"]]]
                )
                course.content = "\n\n".join(
                    [
                        f"{module['title']}: {module['focus']}."
                        for module in entry["modules"]
                    ]
                )
                course.passing_score = 70
                course.is_active = True
                course.save(update_fields=[
                    "course_code", "slug", "summary", "description", "learning_objectives", "content", "passing_score", "is_active", "updated_at"
                ])
                updated_courses += 1
                for module_data in entry["modules"]:
                    module, _ = CourseModule.objects.update_or_create(
                        course=course,
                        order=module_data["order"],
                        defaults={
                            "title": module_data["title"],
                            "duration": "10 to 15 min",
                            "module_type": CourseModule.ModuleType.MIXED,
                            "learning_mode": CourseModule.LearningMode.SELF_PACED,
                            "overview": module_data["focus"],
                            "content": module_content(entry, module_data),
                            "module_summary": f"Review {module_data['focus']} before progressing.",
                            "knowledge_check": (
                                f"What information would you verify before applying {module_data['title'].lower()}, "
                                "and what would need supervision or a local policy check?"
                            ),
                            "practical_activity": (
                                "Use the course worksheet with a de-identified scenario. Record observations, your action within role, "
                                "and any consultation, referral, or escalation needed."
                            ),
                        },
                    )
                    updated_modules += 1
            if not options["replace_school_exams"]:
                existing = SchoolExamQuestion.objects.filter(school__name__in=exams_by_school).exists()
                if existing:
                    raise CommandError(
                        "School certification questions already exist. Re-run with --replace-school-exams only if replacing this exam bank is intended."
                    )
            if options["replace_school_exams"]:
                SchoolExamQuestion.objects.filter(school__name__in=exams_by_school).delete()
            created_questions = 0
            for school_name, exam in exams_by_school.items():
                school = schools[school_name]
                school.passing_score = int(exam.get("passing_score", 70))
                school.save(update_fields=["passing_score", "updated_at"])
                for question_data in exam["questions"]:
                    question = SchoolExamQuestion.objects.create(
                        school=school,
                        text=question_data["text"],
                        order=question_data["order"],
                    )
                    SchoolExamChoice.objects.bulk_create([
                        SchoolExamChoice(
                            question=question,
                            text=choice["text"],
                            is_correct=choice["is_correct"],
                            order=choice["order"],
                        )
                        for choice in question_data["choices"]
                    ])
                    created_questions += 1
        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated_courses} courses, created {created_courses} new courses, structured {updated_modules} modules, "
            f"and created {created_questions} school certification questions."
        ))
