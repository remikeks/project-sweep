"""Create the upload manifest for a generated SWEEP courseware release."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


MIME_TYPES = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_entry(entries, release, course, asset_path, asset_type, title, module_order=None):
    if not asset_path.is_file():
        raise FileNotFoundError(asset_path)
    entries.append(
        {
            "course_number": course["number"],
            "course_code": course["code"],
            "course_slug": course["slug"],
            "school": course["school"],
            "module_order": module_order or "",
            "title": title,
            "asset_type": asset_type,
            "path": asset_path.relative_to(release).as_posix(),
            "content_type": MIME_TYPES[asset_path.suffix.lower()],
            "size_bytes": asset_path.stat().st_size,
            "sha256": sha256(asset_path),
            "version": "1.0.0",
            "language": "en",
            "publication_status": "in_review",
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    args = parser.parse_args()
    release = args.release.resolve()
    catalogue = json.loads((release / "course_catalogue.json").read_text(encoding="utf-8"))
    entries = []
    for course in catalogue:
        prefix = f"{course['number']:02d}-{course['slug']}"
        add_entry(entries, release, course, release / "docx" / f"{prefix}-learner-guide.docx", "learner_guide", f"{course['title']} learner guide DOCX")
        add_entry(entries, release, course, release / "pdf" / f"{prefix}-learner-guide.pdf", "learner_guide", f"{course['title']} learner guide PDF")
        add_entry(entries, release, course, release / "pptx" / f"{prefix}-course-deck.pptx", "slides", f"{course['title']} slide deck PPTX")
        add_entry(entries, release, course, release / "docx" / f"{prefix}-practice-worksheet.docx", "worksheet", f"{course['title']} practice worksheet DOCX")
        add_entry(entries, release, course, release / "pdf" / f"{prefix}-practice-worksheet.pdf", "worksheet", f"{course['title']} practice worksheet PDF")
        for module in course["modules"]:
            module_order = module["order"]
            add_entry(
                entries,
                release,
                course,
                release / "docx" / f"{prefix}-module-{module_order}-video-plan-transcript.docx",
                "transcript",
                f"{course['title']} module {module_order} video plan and transcript DOCX",
                module_order,
            )
    if len(entries) != 240:
        raise ValueError(f"Expected 240 assets, found {len(entries)}.")
    (release / "upload_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
    with (release / "upload_manifest.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(entries[0]))
        writer.writeheader()
        writer.writerows(entries)
    print(f"Prepared {len(entries)} upload records for {len(catalogue)} courses.")


if __name__ == "__main__":
    main()
