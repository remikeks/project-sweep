"""Read-only post-upload verification and public catalogue checks."""
import html
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sweep.settings")
import django
django.setup()
from django.core.management import call_command
from courses.models import Course,CourseAsset
from schools.models import School

release=ROOT/"production_courseware/phase_three/fsw_media_01"
private=ROOT/"production_courseware/private/phase-three"
receipt=private/"fsw-resources.applied.json"
call_command("stage_pdf_slide_resources",release=release,manifest=release/"upload_manifest.json",verify=receipt)
proof=json.loads(receipt.read_text())
assert len(proof["new_asset_ids"])==8
assert set(CourseAsset.objects.filter(pk__in=proof["new_asset_ids"]).values_list("status",flat=True))=={"in_review"}
assert Course.objects.filter(is_active=True).count()==34
assert Course.objects.count()==36
assert School.objects.filter(code__isnull=False,is_active=True).count()==25
assert not School.objects.filter(code__isnull=False,enrollment_open=True).exists()

def fetch(path):
    try:
        with urlopen(Request("https://sweepacademy.org"+path,headers={"Cache-Control":"no-cache"}),timeout=40) as response:
            return response.status,html.unescape(" ".join(re.sub("<[^>]+>"," ",response.read().decode()).split()))
    except HTTPError as exc:
        return exc.code,""

checks=[]
status,body=fetch("/courses/?phase_three_media=2026-11-14")
assert status==200 and "34 Courses shown" in body
checks.append(dict(path="/courses/",status=status,passed=True))
for code in ["SWP-035","SWP-036"]:
    course=Course.objects.get(course_code=code)
    assert course.title not in body
    status,_=fetch(course.get_absolute_url())
    assert status==404
    checks.append(dict(path=course.get_absolute_url(),status=status,passed=True))
existing=Course.objects.get(course_code="SWP-016")
status,text=fetch(existing.get_absolute_url())
assert status==200 and existing.title in text
checks.append(dict(path=existing.get_absolute_url(),status=status,passed=True))
with (private/"post-upload-verification.json").open("x",encoding="utf-8") as handle:
    json.dump(dict(private_resources_verified=8,preexisting_parity=True,active_courses=34,inactive_drafts=2,
        closed_coded_schools=25,public_checks=checks),handle,indent=2)
print("Post-upload verification passed: eight private resources, 34 retained active courses, two hidden drafts and four public checks.")
