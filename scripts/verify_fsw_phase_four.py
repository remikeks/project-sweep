"""Verify the combined phase-four additions and retained public catalogue."""
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
from courses.authored_review import digest,course_values,lesson_text
from courses.management.commands.stage_authored_review import snapshot
from courses.models import Course,CourseAsset
from schools.models import School

release=ROOT/"production_courseware/phase_four/fsw_media_02"
private=ROOT/"production_courseware/private/phase-four"
package=json.loads((ROOT/"production_courseware/phase_four/fsw_batch_02/review_package.json").read_text(encoding="utf-8"))
course_proof=json.loads((private/"fsw-courses.applied.json").read_text())
asset_proof=json.loads((private/"fsw-resources.applied.json").read_text())
assert digest(package)==course_proof["package_sha256"]
call_command("stage_pdf_slide_resources",release=release,manifest=release/"upload_manifest.json",verify=private/"fsw-resources.applied.json")
assert len(course_proof["new_course_ids"])==5 and len(course_proof["new_module_ids"])==15
assert len(asset_proof["new_asset_ids"])==20
excluded={"courses.course":course_proof["new_course_ids"],"courses.coursemodule":course_proof["new_module_ids"],"courses.courseasset":asset_proof["new_asset_ids"]}
assert snapshot(excluded)==course_proof["before"]==course_proof["after"]
for entry in package["courses"]:
    course=Course.objects.get(course_code=entry["code"],slug=entry["slug"])
    assert course.school.code=="FSW" and not course.paralearn_assessment_id
    for field,value in course_values(entry,package["references"]).items():
        assert getattr(course,field)==value,(entry["code"],field)
    for module,expected in zip(course.modules.order_by("order"),entry["modules"],strict=True):
        assert module.title==expected["title"] and module.content==lesson_text(expected,package["references"])
    assert course.assets.count()==4
assert CourseAsset.objects.filter(pk__in=asset_proof["new_asset_ids"],status="in_review").count()==20
assert Course.objects.filter(is_active=True).count()==34 and Course.objects.count()==41
assert CourseAsset.objects.count()==300
assert School.objects.filter(code__isnull=False,is_active=True).count()==25
assert not School.objects.filter(code__isnull=False,enrollment_open=True).exists()
fsw=School.objects.get(code="FSW")
assert fsw.courses.count()==10 and fsw.courses.filter(is_active=False).count()==7

def fetch(path):
    try:
        with urlopen(Request("https://sweepacademy.org"+path,headers={"Cache-Control":"no-cache"}),timeout=40) as response:
            return response.status,html.unescape(" ".join(re.sub("<[^>]+>"," ",response.read().decode()).split()))
    except HTTPError as exc:
        return exc.code,""

checks=[]
status,body=fetch("/courses/?phase_four=2026-11-14")
assert status==200 and "34 Courses shown" in body
checks.append(dict(path="/courses/",status=status,passed=True))
for code in [f"SWP-{n:03}" for n in range(35,42)]:
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
    json.dump(dict(private_resources_verified=20,preexisting_parity=True,active_courses=34,inactive_drafts=7,
        fsw_courses=10,closed_coded_schools=25,public_checks=checks),handle,indent=2)
print("Verified twenty private resources, five exact source matches, retained-record parity, ten FSW courses and nine public checks.")
