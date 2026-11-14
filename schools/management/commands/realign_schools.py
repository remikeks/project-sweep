"""Move course school references only, with dry run, parity audit and rollback."""
import hashlib
import json
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from courses.models import Course
from learning.models import SchoolEnrollment
from schools.catalogue import refactor_manifest
from schools.models import School

VERSION = "schools-2026-11-v1"
SCHOOL_FIELDS = ("id", "name", "slug", "code", "is_active", "is_historical", "enrollment_open", "target_course_count", "description", "order")


def fingerprints():
    """Hash all course, learning, credential and exam values without exposing PII."""
    result = {}
    for label in ("courses", "learning", "credentials", "schools"):
        for model in apps.get_app_config(label).get_models():
            if model is School:
                continue
            fields = [f.attname for f in model._meta.concrete_fields if not (model is Course and f.name == "school")]
            digest = hashlib.sha256()
            count = 0
            for row in model.objects.order_by("pk").values_list(*fields).iterator():
                digest.update(json.dumps(row, default=str, ensure_ascii=False).encode())
                digest.update(b"\n")
                count += 1
            result[model._meta.label_lower] = {"count": count, "sha256": digest.hexdigest()}
    return result


def write_receipt(path, payload):
    # Exclusive create: never replace the only rollback record for an earlier run.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)


class Command(BaseCommand):
    help = "Dry-run or apply the 25-school realignment without changing course content or CBTs."

    def add_arguments(self, parser):
        parser.add_argument("--commit", action="store_true")
        parser.add_argument("--receipt", type=Path)
        parser.add_argument("--verify", type=Path, help="Read-only verification against a completed receipt.")
        parser.add_argument("--rollback", type=Path, help="Restore the original assignments from a completed receipt.")

    def handle(self, *args, **options):
        try:
            if options["verify"] or options["rollback"]:
                if options["verify"] and options["rollback"]:
                    raise CommandError("Choose --verify or --rollback.")
                return self.from_receipt(options)
            if options["commit"] and not options["receipt"]:
                raise CommandError("--commit requires a new --receipt path for the rollback record.")
            self.apply(options)
        except (ValueError, OSError) as exc:
            raise CommandError(str(exc)) from exc

    def validate_courses(self, data):
        courses = list(Course.objects.select_for_update().select_related("school").order_by("id"))
        if len(courses) != 34 or {c.course_code for c in courses} != {c["code"] for c in data["courses"]}:
            raise CommandError("Baseline drift: expected exactly the 34 approved course codes. Nothing changed.")
        by_code = {c.course_code: c for c in courses}
        school_rows = {s["code"]: s for s in data["schools"]}
        for row in data["courses"]:
            course = by_code[row["code"]]
            if course.title != row["title"]:
                raise CommandError(f"Course title drift for {row['code']}. Nothing changed.")
            if course.school.name not in (row["old_school"], school_rows[row["new_school"]]["name"]):
                raise CommandError(f"Unexpected source school for {row['code']}. Nothing changed.")
        return by_code

    @transaction.atomic
    def apply(self, options):
        data = refactor_manifest()
        schools = list(School.objects.select_for_update().all())
        expected = {s["code"] for s in data["schools"]}
        if any(s.code and s.code not in expected for s in schools):
            raise CommandError("Unrecognized coded schools; review the baseline before realignment.")
        allowed_names = {c["old_school"] for c in data["courses"]} | {s["name"] for s in data["schools"]}
        if any(s.is_active and s.name not in allowed_names for s in schools):
            raise CommandError("An unrecognized active school exists; nothing changed.")
        by_code = self.validate_courses(data)
        targets = {s.code: s for s in schools if s.code}
        for row in data["schools"]:
            if row["code"] in targets:
                target = targets[row["code"]]
                if target.name != row["name"] or target.target_course_count != row["target"]:
                    raise CommandError(f"School register drift for {row['code']}.")
            elif any(s.name == row["name"] or s.slug == slugify(row["name"]) for s in schools):
                raise CommandError(f"An uncoded or conflicting school exists for {row['code']}.")
        moved = sum(by_code[c["code"]].school.code != c["new_school"] for c in data["courses"])
        retired = [s for s in schools if not s.code and s.name in allowed_names]
        complete = (len(targets) == 25 and not moved and all(s.is_active for s in targets.values())
                    and all(s.is_historical and not s.is_active for s in retired))
        self.stdout.write(f"Validated 25 school definitions and 34 course assignments; {moved} courses need realignment.")
        if complete:
            self.stdout.write(self.style.SUCCESS("Already realigned. No changes made."))
            return
        if not options["commit"]:
            self.stdout.write("Dry run only. Course content, CBTs and learner records are unchanged.")
            return
        # Never silently reconstruct a learner's incomplete historical snapshot.
        if SchoolEnrollment.objects.filter(school__in=retired, curriculum_requirements__isnull=True).exists():
            raise CommandError("A legacy enrolment has no frozen requirements; review it before moving courses.")
        before = fingerprints()
        receipt = {"version": VERSION, "created_at": timezone.now().isoformat(), "status": "prepared",
                   "schools_before": list(School.objects.order_by("id").values(*SCHOOL_FIELDS)),
                   "courses_before": [{"id": c.id, "code": c.course_code, "school_id": c.school_id} for c in by_code.values()],
                   "before": before}
        write_receipt(options["receipt"], receipt)
        for row in data["schools"]:
            if row["code"] not in targets:
                targets[row["code"]] = School.objects.create(
                    code=row["code"], name=row["name"], order=row["number"],
                    target_course_count=row["target"], description=row["scope"], enrollment_open=False)
            else:
                School.objects.filter(pk=targets[row["code"]].pk).update(is_active=True, is_historical=False)
        for row in data["courses"]:
            Course.objects.filter(pk=by_code[row["code"]].pk).update(school_id=targets[row["new_school"]].pk)
        School.objects.filter(pk__in=[s.pk for s in retired]).update(is_active=False, is_historical=True, enrollment_open=False)
        if before != fingerprints():
            raise CommandError("Parity verification failed; the transaction was rolled back.")
        if School.objects.filter(is_active=True).count() != 25:
            raise CommandError("Active school count mismatch; transaction rolled back.")
        receipt.update(status="applied", targets={s.code: s.pk for s in targets.values()},
                       applied_at=timezone.now().isoformat())
        # A separate completed receipt avoids overwriting the durable pre-change record.
        completed = options["receipt"].with_name(options["receipt"].stem + ".applied.json")
        write_receipt(completed, receipt)
        self.stdout.write(self.style.SUCCESS(f"Realigned 34 courses into 25 schools. All protected record hashes match. Receipt: {completed}"))

    @transaction.atomic
    def from_receipt(self, options):
        path = options["verify"] or options["rollback"]
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt.get("version") != VERSION or receipt.get("status") != "applied":
            raise CommandError("Use a completed applied receipt for this refactor version.")
        # Strict verification is intentionally limited to the no-new-courses phase.
        # Legitimate new learner activity also changes these hashes; review rather than overwrite it.
        if fingerprints() != receipt["before"]:
            raise CommandError("Protected data has changed since the receipt; manual review required, nothing changed.")
        by_code = self.validate_courses(refactor_manifest())
        targets = receipt["targets"]
        expected_map = {c["code"]: targets[c["new_school"]] for c in refactor_manifest()["courses"]}
        if any(c.school_id != expected_map[code] for code, c in by_code.items()):
            raise CommandError("Assignment drift since the receipt. Nothing changed.")
        if options["verify"]:
            if School.objects.filter(is_active=True).count() != 25:
                raise CommandError("Active school count drift.")
            self.stdout.write(self.style.SUCCESS("Verified 25 schools, 34 assignments and all protected record hashes."))
            return
        if not options["commit"]:
            self.stdout.write("Rollback validated; add --commit to restore original assignments.")
            return
        target_ids = set(targets.values())
        if (SchoolEnrollment.objects.filter(school_id__in=target_ids).exists()
                or apps.get_model("credentials", "Certificate").objects.filter(school_id__in=target_ids).exists()):
            raise CommandError("New school learner records exist; do not roll back automatically.")
        for row in receipt["courses_before"]:
            Course.objects.filter(pk=row["id"], course_code=row["code"]).update(school_id=row["school_id"])
        original_ids = {s["id"] for s in receipt["schools_before"]}
        School.objects.filter(pk__in=target_ids - original_ids).update(is_active=False, enrollment_open=False)
        for school in receipt["schools_before"]:
            school = dict(school)
            pk = school.pop("id")
            School.objects.filter(pk=pk).update(**school)
        if fingerprints() != receipt["before"]:
            raise CommandError("Rollback parity check failed; transaction rolled back.")
        self.stdout.write(self.style.SUCCESS("Original school assignments restored; new school rows retained inactive. Protected data unchanged."))
