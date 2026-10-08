"""Upload a verified courseware release to private Supabase Storage.

New assets are registered in ``in_review``. This command deliberately does
not mark content approved or published because that workflow must identify a
real reviewer and publisher after jurisdictional and subject-matter checks.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.content_storage import (
    StorageConfigurationError,
    StorageRequestError,
    SupabaseStorageClient,
    build_storage_path,
    canonical_storage_url,
    storage_is_configured,
    validate_upload_metadata,
)
from courses.content_workflow import create_external_asset, transition_asset
from courses.models import Course, CourseAsset, CourseModule


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def upload_bytes(*, signed_url: str, source: Path, content_type: str) -> None:
    request = Request(
        signed_url,
        data=source.read_bytes(),
        method="PUT",
        headers={"Content-Type": content_type, "x-upsert": "false"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            if response.status not in {200, 201}:
                raise CommandError("Supabase Storage did not accept the upload.")
    except HTTPError as exc:
        raise CommandError(f"Supabase Storage rejected {source.name} with HTTP {exc.code}.") from exc
    except URLError as exc:
        raise CommandError(f"Supabase Storage could not be reached for {source.name}.") from exc
    except OSError as exc:
        raise CommandError(f"Could not upload {source.name} to Supabase Storage.") from exc


class Command(BaseCommand):
    help = "Upload a generated production courseware manifest to private Storage and register assets as in review."

    def add_arguments(self, parser):
        parser.add_argument("--release", type=Path, required=True)
        parser.add_argument("--manifest", type=Path, required=True)
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Upload and register assets. Without this flag the command validates files and metadata only.",
        )
        parser.add_argument(
            "--register-local",
            action="store_true",
            help="Register assets in the database without uploading bytes to remote Supabase Storage.",
        )

    def handle(self, *args, **options):
        release = options["release"].resolve()
        manifest_path = options["manifest"].resolve()
        if not release.is_dir() or not manifest_path.is_file():
            raise CommandError("--release must be a directory and --manifest must be an existing JSON file.")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError("The upload manifest must be valid JSON.") from exc
        if not isinstance(manifest, list) or len(manifest) != 240:
            raise CommandError("The upload manifest must contain exactly 240 release assets.")
        for entry in manifest:
            source = (release / entry["path"]).resolve()
            if release not in source.parents or not source.is_file():
                raise CommandError(f"Manifest path is missing or outside the release directory: {entry.get('path')}")
            if source.stat().st_size != int(entry["size_bytes"]):
                raise CommandError(f"Size changed after manifest generation: {source.name}")
            if file_sha256(source) != entry["sha256"]:
                raise CommandError(f"Checksum changed after manifest generation: {source.name}")
            validate_upload_metadata(
                asset_type=entry["asset_type"],
                filename=source.name,
                content_type=entry["content_type"],
                size_bytes=source.stat().st_size,
            )
        if not options["commit"]:
            self.stdout.write(self.style.SUCCESS("Validated 240 courseware files, checksums, and Storage-compatible metadata. No upload or database changes were made."))
            return
        register_local = bool(options.get("register_local"))
        if not register_local and not storage_is_configured():
            raise CommandError("Supabase Storage is not configured in the protected environment. Use --register-local to register assets locally.")
        client = None if register_local else SupabaseStorageClient()
        created = 0
        skipped = 0
        for entry in manifest:
            source = (release / entry["path"]).resolve()
            try:
                course = Course.objects.get(course_code=entry["course_code"], slug=entry["course_slug"])
            except Course.DoesNotExist as exc:
                raise CommandError(f"Course is not synchronised for asset {source.name}: {entry['course_code']}") from exc
            module = None
            if entry.get("module_order") not in (None, ""):
                try:
                    module = CourseModule.objects.get(course=course, order=int(entry["module_order"]))
                except CourseModule.DoesNotExist as exc:
                    raise CommandError(f"Module is not synchronised for asset {source.name}.") from exc
            if CourseAsset.objects.filter(
                course=course,
                module=module,
                title=entry["title"],
                version=entry["version"],
                content_type=entry["content_type"],
            ).exists():
                skipped += 1
                continue
            try:
                storage_path = build_storage_path(
                    course_slug=course.slug,
                    module_order=module.order if module else None,
                    filename=source.name,
                )
                if not register_local:
                    signed = client.create_signed_upload_url(storage_path)
                    upload_bytes(signed_url=signed.url, source=source, content_type=entry["content_type"])
                payload = {
                    "title": entry["title"],
                    "asset_type": entry["asset_type"],
                    "external_url": canonical_storage_url(storage_path),
                    "storage_path": storage_path,
                    "original_filename": source.name,
                    "content_type": entry["content_type"],
                    "size_bytes": source.stat().st_size,
                    "version": entry["version"],
                    "language": entry["language"],
                    "order": 0,
                    "is_downloadable": True,
                }
                with transaction.atomic():
                    asset = create_external_asset(user=None, course=course, module=module, payload=payload)
                    transition_asset(user=None, asset=asset, action="submit")
                created += 1
            except (StorageConfigurationError, StorageRequestError) as exc:
                raise CommandError(f"Storage setup failed while processing {source.name}: {exc}") from exc
        action_verb = "Registered" if register_local else "Uploaded and registered"
        self.stdout.write(self.style.SUCCESS(
            f"{action_verb} {created} assets as in review; skipped {skipped} matching existing assets."
        ))
