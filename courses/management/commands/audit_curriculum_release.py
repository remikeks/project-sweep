"""Audit a generated curriculum release before it is uploaded or published."""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from courses.curriculum_validation import CurriculumValidationError, validate_catalogue, validate_manifest


class Command(BaseCommand):
    help = "Validate catalogue identities, course packages, and optional release checksums without changing data."

    def add_arguments(self, parser):
        parser.add_argument("--catalogue", type=Path, required=True)
        parser.add_argument("--manifest", type=Path, required=True)
        parser.add_argument(
            "--release",
            type=Path,
            help="Verify that every manifest file exists and has the recorded size and checksum.",
        )
        parser.add_argument(
            "--expected-school-count",
            type=int,
            default=10,
            help="Number of schools represented in this release. Use 1 only for an additive course draft.",
        )

    def handle(self, *args, **options):
        catalogue_path = options["catalogue"].resolve()
        manifest_path = options["manifest"].resolve()
        release = options.get("release")
        if not catalogue_path.is_file() or not manifest_path.is_file():
            raise CommandError("--catalogue and --manifest must point to existing JSON files.")
        if release is not None:
            release = release.resolve()
            if not release.is_dir():
                raise CommandError("--release must point to an existing release directory.")
        try:
            catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            catalogue_summary = validate_catalogue(
                catalogue, expected_school_count=options["expected_school_count"]
            )
            manifest_summary = validate_manifest(
                manifest,
                catalogue=catalogue,
                release=release,
                expected_school_count=options["expected_school_count"],
            )
        except (OSError, json.JSONDecodeError, CurriculumValidationError) as exc:
            raise CommandError(str(exc)) from exc

        verification = " and verified every release file" if release else ""
        self.stdout.write(self.style.SUCCESS(
            "Curriculum release audit passed: "
            f"{catalogue_summary['schools']} schools, {catalogue_summary['courses']} courses, "
            f"{catalogue_summary['modules']} modules, {manifest_summary['assets']} assets "
            f"across {manifest_summary['asset_courses']} course packages{verification}."
        ))
