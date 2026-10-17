"""Replace the four unpublished expansion packages without creating duplicate rows.

Storage bytes are uploaded and downloaded for checksum verification before a
short database transaction. Prior paths stay in the rollback journal. No live
course, learner record, assessment mapping or publication state is changed.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from courses.content_storage import SupabaseStorageClient, build_storage_path, canonical_storage_url, validate_upload_metadata
from courses.curriculum_validation import validate_manifest
from courses.management.commands.upload_production_courseware import upload_bytes
from courses.models import Course, CourseAsset, CourseModule

CODES = ("SWP-031", "SWP-032", "SWP-033", "SWP-034")
ASSET_FIELDS = ("id", "course_id", "module_id", "title", "asset_type", "content_type", "status", "version", "storage_path", "external_url", "original_filename", "size_bytes")
MODULE_FIELDS = ("id", "course_id", "order", "title", "overview", "content", "module_summary", "knowledge_check", "practical_activity")


def snapshot(manifest, *, lock=False):
    courses = Course.objects.filter(course_code__in=CODES).order_by("pk")
    assets = CourseAsset.objects.filter(course__course_code__in=CODES).order_by("pk")
    modules = CourseModule.objects.filter(course__course_code__in=CODES).order_by("pk")
    if lock:
        courses, assets, modules = (q.select_for_update() for q in (courses, assets, modules))
    course_rows = list(courses.values("id", "course_code", "slug", "title", "is_active"))
    if len(course_rows) != 4 or any(c["is_active"] for c in course_rows):
        raise CommandError("Exactly four inactive expansion courses are required; active courses are never revised here.")
    asset_rows = list(assets.values(*ASSET_FIELDS))
    module_rows = list(modules.values(*MODULE_FIELDS))
    if len(asset_rows) != 32 or len(module_rows) != 12:
        raise CommandError("Expected exactly 32 staged asset rows and 12 modules.")
    if any(a["status"] != "in_review" for a in asset_rows):
        raise CommandError("Every target asset must still be in review.")
    by_code = {c["course_code"]: c for c in course_rows}
    matched = set()
    for entry in manifest:
        course = by_code[entry["course_code"]]
        if course["slug"] != entry["course_slug"]:
            raise CommandError("Course slug changed")
        order = int(entry["module_order"]) if entry.get("module_order") not in (None, "") else None
        module_matches = [m for m in module_rows if m["course_id"] == course["id"] and m["order"] == order]
        if order is not None and len(module_matches) != 1:
            raise CommandError("Module identity is ambiguous")
        module_id = module_matches[0]["id"] if order is not None else None
        matches = [a for a in asset_rows if a["course_id"] == course["id"] and a["module_id"] == module_id
                   and a["title"] == entry["title"] and a["asset_type"] == entry["asset_type"] and a["content_type"] == entry["content_type"]]
        if len(matches) != 1 or matches[0]["id"] in matched:
            raise CommandError("Asset identity is missing or ambiguous")
        matched.add(matches[0]["id"])
        entry["target_id"] = matches[0]["id"]
    return {"courses":course_rows, "assets":asset_rows, "modules":module_rows}


def save_journal(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temporary.replace(path)


def verify_remote(client, storage_path, digest):
    url = client.create_signed_download_url(storage_path)
    with urlopen(url, timeout=60) as response:
        checksum = hashlib.sha256(response.read()).hexdigest()
    if checksum != digest:
        raise CommandError("Uploaded bytes do not match the release checksum")


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("--release", type=Path, required=True)
        parser.add_argument("--teaching-source", type=Path, required=True)
        parser.add_argument("--journal", type=Path, required=True)
        parser.add_argument("--commit", action="store_true")

    def handle(self, *args, **options):
        release = options["release"].resolve()
        manifest_bytes = (release / "upload_manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        catalogue = json.loads((release / "course_catalogue.json").read_text(encoding="utf-8"))
        teaching_bytes = options["teaching_source"].read_bytes()
        teaching = json.loads(teaching_bytes)
        assessment_bytes = (options["teaching_source"].parent / "assessment_source.json").read_bytes()
        assessment = {c["code"]:c for c in json.loads(assessment_bytes)["courses"]}
        validate_manifest(manifest, catalogue=catalogue, release=release, expected_school_count=2)
        if {e["course_code"] for e in manifest} != set(CODES) or len(manifest) != 32:
            raise CommandError("This command is limited to the four expansion courses")
        if {c["code"] for c in teaching["courses"]} != set(CODES) or len(teaching["courses"]) != 4:
            raise CommandError("Teaching source must contain the four expansion courses exactly once")
        if any(e["version"] != "1.1.0" for e in manifest):
            raise CommandError("Expected evidence package version 1.1.0")
        for course in teaching["courses"]:
            if [m["order"] for m in course["modules"]] != [1, 2, 3]:
                raise CommandError("Teaching module orders must be 1, 2, 3")
        for entry in manifest:
            validate_upload_metadata(asset_type=entry["asset_type"], filename=Path(entry["path"]).name,
                                     content_type=entry["content_type"], size_bytes=entry["size_bytes"])
        before = snapshot(manifest)
        if not options["commit"]:
            self.stdout.write("Preflight passed: replace 32 in-review resources and teach 12 existing modules; create no rows. No changes made.")
            return
        receipt = json.loads((release / "evidence_receipt.json").read_text())
        if receipt.get("visual_review_complete") is not True or receipt.get("teaching_source_sha256") != hashlib.sha256(teaching_bytes).hexdigest():
            raise CommandError("A matching completed visual-review receipt is required")
        if receipt.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
            raise CommandError("Visual review does not cover the current manifest")
        if receipt.get("assessment_source_sha256") != hashlib.sha256(assessment_bytes).hexdigest():
            raise CommandError("Assessment teaching points changed after review")
        journal_path = options["journal"].resolve()
        identity = hashlib.sha256(manifest_bytes + teaching_bytes + assessment_bytes).hexdigest()
        if journal_path.exists():
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
            if journal["release_identity"] != identity:
                raise CommandError("Journal belongs to a different release")
            if journal.get("committed"):
                if before != journal["after"]:
                    raise CommandError("Database differs from the committed journal; review before continuing")
                self.stdout.write("Already committed; unchanged. No uploads or new rows.")
                return
            if before != journal["before"]:
                raise CommandError("Staged rows changed since the journal was created")
        else:
            if any(a["version"] != "1.0.0" for a in before["assets"]):
                raise CommandError("Initial revision requires the original 1.0.0 staged assets")
            journal = {"release_identity":identity, "before":before, "objects":{}, "committed":False}
            save_journal(journal_path, journal)
        client = SupabaseStorageClient()
        for entry in manifest:
            key = str(entry["target_id"])
            if key not in journal["objects"]:
                storage_path = build_storage_path(course_slug=entry["course_slug"], module_order=entry.get("module_order") or None, filename=Path(entry["path"]).name)
                journal["objects"][key] = {"path":storage_path, "verified":False}
                save_journal(journal_path, journal)
            item = journal["objects"][key]
            if not item["verified"]:
                try:
                    # Recover an upload that completed before a previous interruption.
                    verify_remote(client, item["path"], entry["sha256"])
                except Exception:
                    signed = client.create_signed_upload_url(item["path"])
                    upload_bytes(signed_url=signed.url, source=release / entry["path"], content_type=entry["content_type"])
                    verify_remote(client, item["path"], entry["sha256"])
                item["verified"] = True
                save_journal(journal_path, journal)
            else:
                # A prior run's receipt is not proof that the object still exists.
                verify_remote(client, item["path"], entry["sha256"])
            self.stdout.write(f"Verified replacement {key}")
        with transaction.atomic():
            if snapshot(manifest, lock=True) != before:
                raise CommandError("Rows changed during upload; no database changes applied")
            for entry in manifest:
                storage_path = journal["objects"][str(entry["target_id"])]["path"]
                CourseAsset.objects.filter(pk=entry["target_id"]).update(storage_path=storage_path,
                    external_url=canonical_storage_url(storage_path), version=entry["version"],
                    original_filename=Path(entry["path"]).name, size_bytes=entry["size_bytes"], updated_at=timezone.now())
            refs = {r["id"]:r for r in teaching["references"]}
            for course in teaching["courses"]:
                reference_text = "\n\n".join(f"{refs[k]['citation']} {refs[k]['url']}\n{refs[k]['limit']}" for k in course["references"])
                for module in course["modules"]:
                    points = next(m for m in assessment[course["code"]]["modules"] if m["order"] == module["order"])
                    CourseModule.objects.filter(course__course_code=course["code"], order=module["order"]).update(
                        overview=module["heading"], content="\n\n".join([*module["explanation"], module["example"], "Decision points", *[item[0] for item in points["items"]], "Sources and limits", reference_text]),
                        module_summary=module["feedback"], knowledge_check=module["activity"], practical_activity=module["activity"], updated_at=timezone.now())
            journal["after"] = snapshot(manifest)
        journal["committed"] = True
        save_journal(journal_path, journal)
        self.stdout.write("Revised 32 existing resources and 12 modules. Courses remain inactive and resources remain in review. Old objects retained in the rollback journal; no learner records changed.")
