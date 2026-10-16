"""Validation shared by curriculum release build, audit, and sync commands.

The production catalogue deliberately stays at ten schools. Courses may be
added within those schools, so releases are checked for identity and package
completeness without assuming a fixed course total.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any


class CurriculumValidationError(ValueError):
    """Raised when a curriculum release is not safe to publish."""


def normalized(value: Any) -> str:
    """Return a stable comparison key while preserving the authored value."""
    return " ".join(str(value or "").split()).casefold()


def _require_text(row: dict[str, Any], field: str, label: str) -> str:
    value = str(row.get(field, "")).strip()
    if not value:
        raise CurriculumValidationError(f"{label} must include a {field!r} value.")
    return value


def _duplicates(values: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    counts = Counter(values)
    return sorted(key for key, count in counts.items() if count > 1)


def validate_catalogue(catalogue: Any, *, expected_school_count: int = 10) -> dict[str, int]:
    """Validate catalogue identities and the standard three-module structure."""
    if not isinstance(catalogue, list) or not catalogue:
        raise CurriculumValidationError("The catalogue must be a non-empty JSON list.")

    school_names: list[str] = []
    course_keys: list[tuple[str, str]] = []
    course_codes: list[tuple[str]] = []
    course_slugs: list[tuple[str]] = []
    course_numbers: list[tuple[int]] = []
    module_count = 0

    for position, row in enumerate(catalogue, start=1):
        if not isinstance(row, dict):
            raise CurriculumValidationError(f"Course {position} must be a JSON object.")
        school = _require_text(row, "school", f"Course {position}")
        title = _require_text(row, "title", f"Course {position}")
        code = _require_text(row, "code", f"Course {position}")
        slug = _require_text(row, "slug", f"Course {position}")
        try:
            number = int(row["number"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CurriculumValidationError(f"Course {title!r} must have a numeric course number.") from exc
        if number < 1:
            raise CurriculumValidationError(f"Course {title!r} must have a positive course number.")

        modules = row.get("modules")
        if not isinstance(modules, list) or len(modules) != 3:
            raise CurriculumValidationError(f"Course {title!r} must contain exactly three modules.")
        module_orders: list[int] = []
        module_titles: list[tuple[str]] = []
        for module_position, module in enumerate(modules, start=1):
            if not isinstance(module, dict):
                raise CurriculumValidationError(f"Course {title!r}, module {module_position} must be a JSON object.")
            module_title = _require_text(module, "title", f"Course {title!r}, module {module_position}")
            _require_text(module, "focus", f"Course {title!r}, module {module_position}")
            try:
                module_order = int(module["order"])
            except (KeyError, TypeError, ValueError) as exc:
                raise CurriculumValidationError(
                    f"Course {title!r}, module {module_position} must have a numeric order."
                ) from exc
            if module_order < 1:
                raise CurriculumValidationError(f"Course {title!r} has a non-positive module order.")
            module_orders.append(module_order)
            module_titles.append((normalized(module_title),))

        if len(set(module_orders)) != len(module_orders):
            raise CurriculumValidationError(f"Course {title!r} repeats a module order.")
        if _duplicates(module_titles):
            raise CurriculumValidationError(f"Course {title!r} repeats a module title.")

        school_names.append(school)
        course_keys.append((normalized(school), normalized(title)))
        course_codes.append((normalized(code),))
        course_slugs.append((normalized(slug),))
        course_numbers.append((number,))
        module_count += len(modules)

    unique_schools = {normalized(name) for name in school_names}
    if len(unique_schools) != expected_school_count:
        raise CurriculumValidationError(
            f"The catalogue must cover exactly {expected_school_count} schools; found {len(unique_schools)}."
        )
    for label, values in (
        ("course title within a school", course_keys),
        ("course code", course_codes),
        ("course slug", course_slugs),
        ("course number", course_numbers),
    ):
        if _duplicates(values):
            raise CurriculumValidationError(f"The catalogue repeats a {label}.")

    return {"schools": len(unique_schools), "courses": len(catalogue), "modules": module_count}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_manifest(
    manifest: Any,
    *,
    catalogue: Any | None = None,
    release: Path | None = None,
    expected_school_count: int = 10,
) -> dict[str, int]:
    """Validate an eight-asset package for every course in a release."""
    if not isinstance(manifest, list) or not manifest:
        raise CurriculumValidationError("The asset manifest must be a non-empty JSON list.")

    catalogue_by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    if catalogue is not None:
        validate_catalogue(catalogue, expected_school_count=expected_school_count)
        catalogue_by_identity = {
            (normalized(row["code"]), normalized(row["slug"])): row for row in catalogue
        }

    paths: list[tuple[str]] = []
    checksums: list[tuple[str]] = []
    asset_keys: list[tuple[str, str, str, str, str, str]] = []
    by_course: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for position, entry in enumerate(manifest, start=1):
        if not isinstance(entry, dict):
            raise CurriculumValidationError(f"Asset {position} must be a JSON object.")
        code = _require_text(entry, "course_code", f"Asset {position}")
        slug = _require_text(entry, "course_slug", f"Asset {position}")
        title = _require_text(entry, "title", f"Asset {position}")
        asset_type = _require_text(entry, "asset_type", f"Asset {position}")
        path = _require_text(entry, "path", f"Asset {position}")
        checksum = _require_text(entry, "sha256", f"Asset {position}")
        version = _require_text(entry, "version", f"Asset {position}")
        _require_text(entry, "content_type", f"Asset {position}")
        if len(checksum) != 64 or any(character not in "0123456789abcdefABCDEF" for character in checksum):
            raise CurriculumValidationError(f"Asset {path!r} has an invalid SHA-256 checksum.")
        try:
            size_bytes = int(entry["size_bytes"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CurriculumValidationError(f"Asset {path!r} must have a numeric byte size.") from exc
        if size_bytes < 1:
            raise CurriculumValidationError(f"Asset {path!r} must have a positive byte size.")

        course_key = (normalized(code), normalized(slug))
        if catalogue_by_identity and course_key not in catalogue_by_identity:
            raise CurriculumValidationError(f"Asset {path!r} points to a course that is not in the catalogue.")
        module_order = str(entry.get("module_order", "")).strip()
        paths.append((normalized(path),))
        checksums.append((normalized(checksum),))
        asset_keys.append((course_key[0], course_key[1], module_order, normalized(title), normalized(asset_type), normalized(version)))
        by_course.setdefault(course_key, []).append(entry)

        if release is not None:
            candidate = (release / path).resolve()
            if release not in candidate.parents or not candidate.is_file():
                raise CurriculumValidationError(f"Asset path is missing or outside the release directory: {path!r}.")
            if candidate.stat().st_size != size_bytes:
                raise CurriculumValidationError(f"Asset size changed after manifest generation: {path!r}.")
            if _file_sha256(candidate).casefold() != checksum.casefold():
                raise CurriculumValidationError(f"Asset checksum changed after manifest generation: {path!r}.")

    for label, values in (("path", paths), ("checksum", checksums), ("logical asset identity", asset_keys)):
        if _duplicates(values):
            raise CurriculumValidationError(f"The asset manifest repeats an asset {label}.")
    if catalogue_by_identity and set(by_course) != set(catalogue_by_identity):
        raise CurriculumValidationError("Every catalogue course must have a resource package and no extra packages are allowed.")

    for course_key, assets in by_course.items():
        if len(assets) != 8:
            raise CurriculumValidationError(f"Course {course_key[0]} must have exactly eight release assets.")
        types = Counter(str(asset["asset_type"]).strip() for asset in assets)
        if types != Counter({"learner_guide": 2, "slides": 1, "worksheet": 2, "transcript": 3}):
            raise CurriculumValidationError(f"Course {course_key[0]} does not have the standard eight-asset package.")
        transcript_orders = {str(asset.get("module_order", "")).strip() for asset in assets if asset["asset_type"] == "transcript"}
        if transcript_orders != {"1", "2", "3"}:
            raise CurriculumValidationError(f"Course {course_key[0]} must have one transcript for each module.")

    return {"assets": len(manifest), "asset_courses": len(by_course)}
