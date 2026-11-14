"""Read-only live HTTP checks for the phase-one school refactor."""
import concurrent.futures
import html
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sweep.settings")
import django
django.setup()
from courses.models import Course
from schools.models import School

base = "https://sweepacademy.org"
jobs = [("/schools/", "25 Schools"), ("/courses/", "34 Courses shown")]
for school in School.objects.filter(is_active=True):
    jobs.append((school.get_absolute_url(), "School pathway in development"))
for school in School.objects.filter(is_historical=True):
    jobs.append((school.get_absolute_url(), "School catalogue update"))
for course in Course.objects.filter(is_active=True):
    jobs.append((course.get_absolute_url(), course.title))


def check(job):
    path, expected = job
    request = Request(base + path + "?refactor_check=2026-11-v1", headers={"Cache-Control": "no-cache"})
    try:
        with urlopen(request, timeout=45) as response:
            text = html.unescape(" ".join(re.sub("<[^>]+>", " ", response.read().decode()).split()))
            ok = response.status == 200 and expected in text and "Traceback" not in text
            return {"path": path, "status": response.status, "passed": ok}
    except Exception as exc:
        return {"path": path, "passed": False, "error_type": type(exc).__name__}


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(check, jobs))
failed = [r for r in results if not r["passed"]]
receipt = ROOT / "production_courseware/private/school-refactor-2026-11-14/live-verification.json"
receipt.write_text(json.dumps({"base": base, "checks": results}, indent=2), encoding="utf-8")
print(f"Live checks: {len(results) - len(failed)}/{len(results)} passed")
for row in failed:
    print("Failed:", row)
raise SystemExit(bool(failed))
