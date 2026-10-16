"""Stage a small, approved-for-review catalogue without activating courses.

This command deliberately cannot publish content, modify school examinations,
or attach learners to a new course. It exists for a reviewed additive package:
the course remains inactive until the ordinary curriculum and content workflow
has recorded all approvals.
"""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from courses.curriculum_validation import CurriculumValidationError, validate_catalogue
from courses.models import Course, CourseModule
from schools.models import School


def module_content(course: dict, module: dict) -> str:
    return (
        f"This module focuses on {module['focus']}. It supports the course outcome: {course['outcome']} "
        "Use the approved learner guide and local policy to distinguish what is known, what needs verification, "
        "and when consultation, escalation, referral, or handover is needed."
    )


def course_fields(entry: dict) -> dict[str, str | int]:
    return {
        "course_code": entry["code"],
        "slug": entry["slug"],
        "summary": entry["outcome"][:300],
        "description": entry["outcome"],
        "learning_objectives": "\n".join(
            [entry["outcome"], *[f"Apply the key ideas from {module['title']}." for module in entry["modules"]]]
        ),
        "content": "\n\n".join(
            [f"{module['title']}: {module['focus']}." for module in entry["modules"]]
        ),
        "passing_score": 70,
    }


class Command(BaseCommand):
    help = "Stage one or more review-only courses as inactive records; no learner-visible catalogue changes are made."

    def add_arguments(self, parser):
        parser.add_argument("--catalogue", type=Path, required=True)
        parser.add_argument(
            "--expected-school-count",
            type=int,
            default=1,
            help="Number of schools represented in this additive review catalogue.",
        )
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Create or update only inactive review records after validation.",
        )

    def handle(self, *args, **options):
        catalogue_path = options["catalogue"].resolve()
        if not catalogue_path.is_file():
            raise CommandError("--catalogue must point to an existing JSON file.")
        try:
            catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
            summary = validate_catalogue(
                catalogue, expected_school_count=options["expected_school_count"]
            )
        except (OSError, json.JSONDecodeError, CurriculumValidationError) as exc:
            raise CommandError(str(exc)) from exc

        if not options["commit"]:
            self.stdout.write(self.style.SUCCESS(
                f"Validated {summary['courses']} review course(s) and {summary['modules']} modules. "
                "No database changes were made."
            ))
            return

        created_courses = 0
        updated_courses = 0
        staged_modules = 0
        with transaction.atomic():
            schools = {school.name: school for school in School.objects.select_for_update()}
            missing_schools = sorted({entry["school"] for entry in catalogue} - set(schools))
            if missing_schools:
                raise CommandError(
                    "The review catalogue refers to a school that does not exist: "
                    + ", ".join(missing_schools)
                )

            for entry in catalogue:
                school = schools[entry["school"]]
                candidates = {
                    course.id: course
                    for course in Course.objects.select_for_update().filter(
                        school=school
                    ).filter(
                        Q(course_code=entry["code"])
                        | Q(slug=entry["slug"])
                        | Q(title=entry["title"])
                    )
                }
                if len(candidates) > 1:
                    raise CommandError(
                        f"Review course identity collides with more than one existing course: {entry['title']}"
                    )
                course = next(iter(candidates.values()), None)
                if course is not None:
                    if course.is_active:
                        raise CommandError(
                            f"Refusing to overwrite active course {course.title!r}; stage a distinct review course instead."
                        )
                    if (
                        course.title,
                        course.course_code,
                        course.slug,
                    ) != (entry["title"], entry["code"], entry["slug"]):
                        raise CommandError(
                            f"Inactive course identity does not match the review catalogue: {course.title!r}"
                        )
                    unexpected_module_orders = set(course.modules.values_list("order", flat=True)) - {1, 2, 3}
                    if unexpected_module_orders:
                        raise CommandError(
                            f"Inactive course {course.title!r} has modules outside the staged three-module structure."
                        )
                    updated_courses += 1
                else:
                    next_order = (
                        school.courses.order_by("-order", "-id").values_list("order", flat=True).first() or 0
                    ) + 1
                    course = Course.objects.create(
                        school=school,
                        title=entry["title"],
                        order=next_order,
                        is_active=False,
                        **course_fields(entry),
                    )
                    created_courses += 1

                for field, value in course_fields(entry).items():
                    setattr(course, field, value)
                course.is_active = False
                course.save(update_fields=[*course_fields(entry).keys(), "is_active", "updated_at"])
                for module_data in entry["modules"]:
                    CourseModule.objects.update_or_create(
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
                    staged_modules += 1

        self.stdout.write(self.style.SUCCESS(
            f"Staged {created_courses} new and {updated_courses} existing review course(s), "
            f"with {staged_modules} modules. All staged courses remain inactive."
        ))
