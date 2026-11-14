"""Read-only production audit and private snapshot; works before new columns exist."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sweep.settings")
import django
django.setup()
from django.apps import apps
from django.db import connection, transaction
from schools.catalogue import refactor_manifest

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
data = refactor_manifest()
snapshot = {"purpose": "School realignment baseline; private backup", "tables": {}}
with transaction.atomic(), connection.cursor() as cursor:
    if connection.vendor == "postgresql":
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
    for label in ("schools", "courses", "learning", "credentials"):
        for model in apps.get_app_config(label).get_models():
            table = model._meta.db_table
            cursor.execute("SELECT * FROM " + connection.ops.quote_name(table) + " ORDER BY id")
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            snapshot["tables"][table] = {"columns": columns, "rows": rows}
            print(table, len(rows))
    courses = snapshot["tables"]["courses_course"]
    rows = [dict(zip(courses["columns"], row)) for row in courses["rows"]]
    expected = {c["code"]: c for c in data["courses"]}
    if len(rows) != 34 or {r["course_code"] for r in rows} != set(expected):
        raise SystemExit("Baseline mismatch; no database changes made.")
    for row in rows:
        if row["title"] != expected[row["course_code"]]["title"]:
            raise SystemExit("Title mismatch: " + row["course_code"])
        if not row["paralearn_assessment_id"]:
            raise SystemExit("Missing course assessment mapping: " + row["course_code"])
blob = json.dumps(snapshot, default=str, indent=2).encode("utf-8")
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("xb") as handle:
    handle.write(blob)
print("Read-only audit passed: 34 approved courses, all with existing CBT IDs.")
print("Private snapshot SHA256:", hashlib.sha256(blob).hexdigest())
