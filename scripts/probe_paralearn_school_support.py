"""Read-only discovery. Never create questions, exams, candidates or attempts."""
import json
from pathlib import Path
import re
from urllib.request import Request, HTTPRedirectHandler, build_opener
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "production_courseware/private/school-phase2-2026-11-14"
OUT.mkdir(parents=True, exist_ok=True)
secret_file = ROOT / "production_courseware/private/assessment-import-2026-10-18/provider-secrets.json"
if secret_file.is_file():
    api_key = json.loads(secret_file.read_text())["apiKey"]
else:
    api_key = dotenv_values(OUT / ".env.production").get("PARALEARN_API_KEY")
if not api_key or api_key == "[SENSITIVE]":
    raise SystemExit("A private production environment export is required; no request made.")
base = "https://cbt.pln.ng"


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward an integration credential through an unexpected redirect.
        return None


opener = build_opener(NoRedirects())

def get(path, auth=False):
    headers = {"User-Agent": "SWEEP-Academy-integration-audit"}
    if auth:
        headers["Authorization"] = "Bearer " + api_key
    with opener.open(Request(base + path, headers=headers), timeout=35) as r:
        if r.url.split("/")[2] != "cbt.pln.ng":
            raise RuntimeError("Unexpected provider redirect host")
        return r.read().decode()

exams = json.loads(get("/api/cbt/exams", True))
if not isinstance(exams, list):
    raise RuntimeError("Unexpected provider exam listing")
print("Read-only provider access verified; exams:", len(exams))
home = get("/")
scripts = sorted(set(re.findall(r'<script[^>]+src="([^\"]+)"', home)))
findings = {"exam_count": len(exams), "scripts_checked": [], "markers": {}, "route_fragments": []}
for path in scripts:
    if not path.startswith("/_next/"):
        continue
    text = get(path)
    found = [x for x in ("SHORT_ESSAY", "LONG_ESSAY", "ESSAY", "gradingStatus", "FINALIZED", "PENDING", "SUBMITTED", "modelAnswer", "rubric") if x in text]
    if found:
        findings["scripts_checked"].append(path)
        findings["markers"][path] = found
        # Public client code only. Retain bounded excerpts for contract analysis.
        for match in re.finditer(r"(?:SHORT_ESSAY|LONG_ESSAY|gradingStatus|/api/cbt/attempts|/grade|/slip)", text):
            excerpt = text[max(0, match.start()-140):match.end()+220]
            findings["route_fragments"].append(excerpt)
        (OUT / (path.split("/")[-1].split("?")[0])).write_text(text, encoding="utf-8")
(OUT/"provider-readonly-discovery.json").write_text(json.dumps(findings, indent=2),encoding="utf-8")
print("Public-client evidence markers:", sorted({x for v in findings["markers"].values() for x in v}))
print("No provider records changed. Read-only evidence saved privately.")
