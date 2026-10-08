"""Management command to inspect and map ParaLearn CBT assessment IDs across all SWEEP courses.

Usage examples:
    # Inspect current mapping status:
    python manage.py map_paralearn_assessments --status

    # Populate mock/staging IDs (e.g. pl-cbt-swp-001) for dev/test:
    python manage.py map_paralearn_assessments --set-mock

    # Import production ParaLearn exam IDs from a JSON mapping file:
    python manage.py map_paralearn_assessments --from-json path/to/mapping.json
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models import Course


class Command(BaseCommand):
    help = "Inspect and map ParaLearn CBT assessment IDs across SWEEP courses."

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            action="store_true",
            help="Display the current ParaLearn assessment ID configuration for all courses.",
        )
        parser.add_argument(
            "--set-mock",
            action="store_true",
            help="Assign deterministic mock assessment IDs (e.g. pl-cbt-swp-001) to courses with empty IDs.",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default="pl-cbt-",
            help="Prefix to use with --set-mock (default: 'pl-cbt-').",
        )
        parser.add_argument(
            "--from-json",
            type=Path,
            help="Path to a JSON file containing course_code -> examId mappings.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear paralearn_assessment_id across all courses.",
        )

    def handle(self, *args, **options):
        courses = Course.objects.all().order_by("order", "course_code")

        if options["clear"]:
            with transaction.atomic():
                count = courses.exclude(paralearn_assessment_id="").update(paralearn_assessment_id="")
            self.stdout.write(self.style.WARNING(f"Cleared ParaLearn assessment IDs for {count} courses."))
            return

        if options["from_json"]:
            json_path = options["from_json"].resolve()
            if not json_path.is_file():
                raise CommandError(f"Mapping file not found: {json_path}")
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise CommandError(f"Invalid JSON file: {exc}") from exc

            # Support both {"SWP-001": "id_1"} and [{"course_code": "SWP-001", "exam_id": "id_1"}]
            mapping = {}
            if isinstance(data, dict):
                mapping = data
            elif isinstance(data, list):
                for item in data:
                    code = item.get("course_code") or item.get("code")
                    exam_id = item.get("exam_id") or item.get("paralearn_assessment_id") or item.get("examId")
                    if code and exam_id:
                        mapping[code] = str(exam_id).strip()

            updated = 0
            with transaction.atomic():
                for course in courses:
                    if course.course_code in mapping:
                        new_id = mapping[course.course_code]
                        if course.paralearn_assessment_id != new_id:
                            course.paralearn_assessment_id = new_id
                            course.save(update_fields=["paralearn_assessment_id"])
                            updated += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully mapped {updated} courses from JSON file."))
            return

        if options["set_mock"]:
            prefix = options["prefix"]
            updated = 0
            with transaction.atomic():
                for course in courses:
                    code = (course.course_code or f"swp-{course.order:03d}").lower()
                    mock_id = f"{prefix}{code}"
                    if not course.paralearn_assessment_id:
                        course.paralearn_assessment_id = mock_id
                        course.save(update_fields=["paralearn_assessment_id"])
                        updated += 1
            self.stdout.write(self.style.SUCCESS(f"Assigned mock ParaLearn assessment IDs to {updated} courses."))
            return

        # Default / --status: Print configuration table
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("SWEEP COURSES: PARALEARN ASSESSMENT ID STATUS")
        self.stdout.write("=" * 70)

        configured_count = 0
        unconfigured_count = 0

        for course in courses:
            code = course.course_code or "---"
            exam_id = course.paralearn_assessment_id
            if exam_id:
                configured_count += 1
                status_str = self.style.SUCCESS(f"[OK] {exam_id}")
            else:
                unconfigured_count += 1
                status_str = self.style.WARNING("[--] [not configured yet]")

            self.stdout.write(f"[{code:7}] {course.title[:38]:38} -> {status_str}")

        self.stdout.write("-" * 70)
        self.stdout.write(
            f"Total: {courses.count()} courses | "
            f"Configured: {configured_count} | "
            f"Unconfigured: {unconfigured_count}\n"
        )
