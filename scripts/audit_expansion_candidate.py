"""Audit baseline plus four staged packages in memory without copying or importing."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from courses.curriculum_validation import validate_catalogue, validate_manifest
from scripts.build_expansion_review import build


def audit():
    source = json.loads((ROOT / "production_courseware/expansion_review/assessment_source.json").read_text(encoding="utf-8"))
    packages = [(ROOT / "production_courseware/release-2026-10-03", 10)]
    packages.extend((ROOT / "production_courseware/drafts" / c["draft"], 1) for c in source["courses"])
    catalogue, manifest = [], []
    for folder, school_count in packages:
        entries = json.loads((folder / "course_catalogue.json").read_text(encoding="utf-8"))
        assets = json.loads((folder / "upload_manifest.json").read_text(encoding="utf-8"))
        validate_manifest(assets, catalogue=entries, release=folder.resolve(), expected_school_count=school_count)
        catalogue.extend(entries)
        manifest.extend(assets)
    counts = validate_catalogue(catalogue)
    counts.update(validate_manifest(manifest, catalogue=catalogue))
    if counts != {"schools": 10, "courses": 34, "modules": 102, "assets": 272, "asset_courses": 34}:
        raise ValueError(f"Unexpected candidate totals: {counts}")
    build()  # Validate the review banks and cross-bank exact-stem checks too.
    return {**counts, "release_files_checksum_verified": 272,
            "assessment_questions_drafted": 60, "publication_approved": False,
            "scope": "Local candidate only; no live database or storage mutation"}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
