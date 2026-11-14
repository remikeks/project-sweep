"""Read-only verification of an additive course-and-media phase."""
import argparse
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
parser=argparse.ArgumentParser()
for name in ["package","release","private"]:parser.add_argument("--"+name,type=Path,required=True)
parser.add_argument("--school",required=True)
for name in ["total","active","assets","school-count","target"]:parser.add_argument("--expected-"+name,type=int,required=True)
args=parser.parse_args()
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sweep.settings")
import django
django.setup()
from django.core.management import call_command
from courses.authored_review import digest,validate_package,course_values,lesson_text
from courses.management.commands.stage_authored_review import snapshot
from courses.models import Course,CourseAsset
from schools.models import School

package=json.loads(args.package.read_text(encoding="utf-8"));summary=validate_package(package)
private=args.private
cp=json.loads((private/"courses.applied.json").read_text())
ap=json.loads((private/"resources.applied.json").read_text())
assert cp["package_sha256"]==digest(package)
assert len(cp["new_course_ids"])==summary["courses"] and len(cp["new_module_ids"])==summary["modules"]
assert len(ap["new_asset_ids"])==4*summary["courses"]
call_command("stage_pdf_slide_resources",release=args.release,manifest=args.release/"upload_manifest.json",verify=private/"resources.applied.json")
excluded={"courses.course":cp["new_course_ids"],"courses.coursemodule":cp["new_module_ids"],"courses.courseasset":ap["new_asset_ids"]}
assert snapshot(excluded)==cp["before"]==cp["after"]
for entry in package["courses"]:
    course=Course.objects.get(course_code=entry["code"],slug=entry["slug"])
    assert course.school.code==entry["school_code"]==args.school and not course.paralearn_assessment_id
    for field,value in course_values(entry,package["references"]).items():assert getattr(course,field)==value,(entry["code"],field)
    for module,expected in zip(course.modules.order_by("order"),entry["modules"],strict=True):
        assert module.title==expected["title"] and module.content==lesson_text(expected,package["references"])
    assert course.assets.count()==4
assert CourseAsset.objects.filter(pk__in=ap["new_asset_ids"],status="in_review").count()==4*summary["courses"]
assert Course.objects.count()==args.expected_total and Course.objects.filter(is_active=True).count()==args.expected_active
assert CourseAsset.objects.count()==args.expected_assets
assert School.objects.filter(code__isnull=False,is_active=True).count()==25
assert not School.objects.filter(code__isnull=False,enrollment_open=True).exists()
school=School.objects.get(code=args.school)
assert school.courses.count()==args.expected_school_count and school.target_course_count==args.expected_target

def fetch(path):
    try:
        with urlopen(Request("https://sweepacademy.org"+path,headers={"Cache-Control":"no-cache"}),timeout=40) as response:
            return response.status,html.unescape(" ".join(re.sub("<[^>]+>"," ",response.read().decode()).split()))
    except HTTPError as exc:return exc.code,""

checks=[]
status,body=fetch("/courses/?authored_phase="+args.school.lower())
assert status==200 and f"{args.expected_active} Courses shown" in body
checks.append(dict(path="/courses/",status=status,passed=True))
drafts=Course.objects.filter(school__code__isnull=False,is_active=False).order_by("course_code")
for course in drafts:
    assert course.title not in body
    status,_=fetch(course.get_absolute_url());assert status==404
    checks.append(dict(path=course.get_absolute_url(),status=status,passed=True))
for course in school.courses.filter(is_active=True):
    status,text=fetch(course.get_absolute_url());assert status==200 and course.title in text
    checks.append(dict(path=course.get_absolute_url(),status=status,passed=True))
proof=dict(school_code=args.school,source_courses_verified=summary["courses"],private_resources_verified=4*summary["courses"],
    preexisting_parity=True,active_courses=args.expected_active,inactive_drafts=args.expected_total-args.expected_active,
    school_courses=args.expected_school_count,school_target=args.expected_target,total_courses=args.expected_total,total_assets=args.expected_assets,
    closed_coded_schools=25,public_checks=checks)
with (private/"post-upload-verification.json").open("x",encoding="utf-8") as handle:json.dump(proof,handle,indent=2)
print(f"Verified {summary['courses']} source courses, {4*summary['courses']} private resources, retained-record parity and {len(checks)} public checks.")
