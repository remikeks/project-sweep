"""Create-only, transactional staging of full teaching content, with parity proof."""
import json
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from courses.authored_review import course_values, digest, lesson_text, validate_package
from courses.models import Course, CourseModule
from schools.models import School


def snapshot(excluded=None):
    """Hash all pre-existing academy data, including existing CBT mappings."""
    excluded = excluded or {}
    result = {}
    for label in ("schools", "courses", "learning", "credentials"):
        for model in apps.get_app_config(label).get_models():
            rows = list(model.objects.exclude(pk__in=excluded.get(model._meta.label_lower, [])).order_by("pk").values())
            result[model._meta.label_lower] = {"count":len(rows), "sha256":digest(json.loads(json.dumps(rows, default=str)))}
    return result


class Command(BaseCommand):
    help = "Validate or create inactive authored courses; never modify an existing course, CBT or learner record."

    def add_arguments(self, parser):
        parser.add_argument("--package", type=Path, required=True)
        parser.add_argument("--commit", action="store_true")
        parser.add_argument("--receipt", type=Path)

    def handle(self, *args, **options):
        try:
            package = json.loads(options["package"].read_text(encoding="utf-8"))
            summary = validate_package(package)
            if not options["commit"]:
                self.stdout.write(f"Validated {summary}; no changes made.")
                return
            receipt = options["receipt"]
            if not receipt:
                raise CommandError("--commit requires a new --receipt path")
            if receipt.with_suffix(".applied.json").exists():
                raise CommandError("Applied receipt already exists; use a new receipt path")
            receipt.parent.mkdir(parents=True, exist_ok=True)
            # Reserve the audit path before any mutation. Failure records remain for investigation.
            with receipt.open("x", encoding="utf-8") as handle:
                json.dump({"status":"reserved", "package_sha256":digest(package)}, handle)
            result = self.stage(package)
            result.update(status="staged_inactive", timestamp=timezone.now().isoformat(), package_sha256=digest(package))
            with receipt.with_suffix(".applied.json").open("x", encoding="utf-8") as handle:
                json.dump(result, handle, indent=2)
            self.stdout.write(f"Created {len(result['new_course_ids'])} inactive courses and {len(result['new_module_ids'])} modules; all pre-existing records unchanged.")
        except (ValueError, OSError, KeyError, TypeError) as exc:
            raise CommandError(str(exc)) from exc

    @transaction.atomic
    def stage(self, package):
        schools = {s.code:s for s in School.objects.select_for_update().filter(code__in={c["school_code"] for c in package["courses"]})}
        for course in package["courses"]:
            school = schools.get(course["school_code"])
            if not school or school.is_historical or school.enrollment_open:
                raise CommandError("Draft courses require an existing coded school with enrolment closed")
            if Course.objects.filter(Q(course_code=course["code"]) | Q(slug=course["slug"]) | Q(title__iexact=course["title"])).exists():
                raise CommandError(f"Course identity already exists: {course['code']}; create-only staging refused")
        before = snapshot()
        new_courses, new_modules = [], []
        for entry in package["courses"]:
            school = schools[entry["school_code"]]
            order = (school.courses.order_by("-order").values_list("order", flat=True).first() or 0) + 1
            course = Course.objects.create(school=school, order=order, **course_values(entry, package["references"]))
            new_courses.append(course.pk)
            for module in entry["modules"]:
                row = CourseModule.objects.create(course=course, order=module["order"], title=module["title"],
                    overview=module["outcome"], content=lesson_text(module, package["references"]), duration="About 60 min including practice",
                    module_summary=module["outcome"], practical_activity=module["activity"],
                    knowledge_check="Complete the practice activity, then compare your reasoning with the feedback.",
                    module_type=CourseModule.ModuleType.ARTICLE)
                new_modules.append(row.pk)
        after = snapshot({"courses.course":new_courses, "courses.coursemodule":new_modules})
        if before != after:
            raise CommandError("Pre-existing record parity failed; transaction rolled back")
        return dict(new_course_ids=new_courses, new_module_ids=new_modules, before=before, after=after)
