"""Versioned, optional reading notes. No provider calls or learner writes."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def reading_catalogue():
    return json.loads(Path(__file__).with_name("research_readings.json").read_text(encoding="utf8"))


def reading_for_module(course_code, module_order):
    if module_order != 1:
        return None
    return reading_catalogue()["readings"].get(course_code)
