"""The owner-approved 25-school register, independent of the legacy releases."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def refactor_manifest():
    data = json.loads(Path(__file__).with_name("refactor_2026_11.json").read_text(encoding="utf-8"))
    codes = [s["code"] for s in data["schools"]]
    courses = [c["code"] for c in data["courses"]]
    if len(codes) != 25 or len(set(codes)) != 25 or len(courses) != 34 or len(set(courses)) != 34:
        raise ValueError("The realignment manifest must contain 25 unique schools and 34 unique courses.")
    if any(c["new_school"] not in codes for c in data["courses"]):
        raise ValueError("Every course must have a registered destination.")
    if any(not 5 <= s["target"] <= 10 for s in data["schools"]):
        raise ValueError("School targets must be between five and ten courses.")
    return data


def successor_codes(school_name):
    return sorted({c["new_school"] for c in refactor_manifest()["courses"] if c["old_school"] == school_name})
