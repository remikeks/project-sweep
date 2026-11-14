"""Read-only database and public-visibility checks for the inactive FSW batch."""
import json
import html
import os
from pathlib import Path
import sys
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sweep.settings")
import django
django.setup()
from courses.authored_review import course_values, digest, lesson_text, validate_package
from courses.management.commands.stage_authored_review import snapshot
from courses.models import Course
from schools.models import School

folder=ROOT/"production_courseware/private/school-phase2-2026-11-14"
receipt=json.loads((folder/"fsw-staging.applied.json").read_text())
package=json.loads((ROOT/"production_courseware/phase_two/fsw_batch_01/review_package.json").read_text(encoding="utf-8"))
validate_package(package)
assert digest(package)==receipt["package_sha256"],"Staged package checksum changed"
current=snapshot({"courses.course":receipt["new_course_ids"],"courses.coursemodule":receipt["new_module_ids"]})
assert current==receipt["before"]==receipt["after"],"Pre-existing record drift; review without overwriting records"
assert Course.objects.filter(is_active=True).count()==34
assert School.objects.filter(code__isnull=False,is_active=True).count()==25
assert not School.objects.filter(code__isnull=False,enrollment_open=True).exists()
for entry in package["courses"]:
    course=Course.objects.get(course_code=entry["code"])
    assert course.pk in receipt["new_course_ids"] and course.school.code==entry["school_code"]
    assert not course.paralearn_assessment_id and not course.is_active
    for key,value in course_values(entry,package["references"]).items():
        assert getattr(course,key)==value, f"Staged field drift: {entry['code']} {key}"
    assert course.modules.count()==3
    for m in entry["modules"]:
        row=course.modules.get(order=m["order"])
        assert row.pk in receipt["new_module_ids"] and row.content==lesson_text(m,package["references"])
    assert not course.enrollments.exists() and not course.assets.exists() and not course.questions.exists()

def fetch(path):
    try:
        with urlopen(Request("https://sweepacademy.org"+path,headers={"Cache-Control":"no-cache"}),timeout=40) as response:
            body=response.read().decode()
            return response.status,html.unescape(" ".join(re.sub("<[^>]+>"," ",body).split()))
    except HTTPError as exc:
        return exc.code,""

checks=[]
status,body=fetch("/courses/?phase_two_staging=2026-11-14")
assert status==200 and "34 Courses shown" in body
assert all(c["title"] not in body for c in package["courses"])
checks.append(dict(path="/courses/",status=status,check="34 active courses; draft titles absent"))
for entry in package["courses"]:
    course=Course.objects.get(course_code=entry["code"])
    status,_=fetch(course.get_absolute_url())
    assert status==404,"An inactive draft became publicly accessible"
    checks.append(dict(path=course.get_absolute_url(),status=status,check="draft hidden"))
course=Course.objects.get(course_code="SWP-016")
status,body=fetch(course.get_absolute_url())
assert status==200 and course.title in body
checks.append(dict(path=course.get_absolute_url(),status=status,check="existing course still accessible"))
report=dict(preexisting_record_parity=True,active_courses=34,inactive_new_courses=2,new_modules=6,
            coded_schools=25,open_coded_schools=0,public_checks=checks,package_sha256=digest(package))
with (folder/"staging-verification.json").open("x",encoding="utf-8") as handle:
    json.dump(report,handle,indent=2)
print("Verified: 34 unchanged active courses, two hidden drafts, six new modules, 25 closed coded schools; all four public checks passed.")
