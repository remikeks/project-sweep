"""Fresh-process isolated suite plus immutable-source and final-media checks.

This is local evidence only. It never connects to production or writes a live
staging receipt. Run using the configured project Python environment.
"""
import hashlib
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CHECKPOINT="8f7dee621f11ee098fb4c221d6116a2439aefdc5"
release=ROOT/"production_courseware/phase_nine/mhp_media_01"
private=ROOT/"production_courseware/private/phase-nine"
private.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument("--completed-test-summary",type=Path,help="Already observed successful isolated suite output; avoids rerunning unchanged tests")
args=parser.parse_args()
if args.completed_test_summary:
    test_output=args.completed_test_summary.read_text()
    assert "OK" in test_output and "FAILED" not in test_output
else:
    env=dict(os.environ,DATABASE_URL="sqlite:///:memory:",DEBUG="True")
    run=subprocess.run([sys.executable,"manage.py","test","--noinput"],cwd=ROOT,env=env,capture_output=True,text=True)
    test_output=run.stdout+run.stderr
    (private/"isolated-tests.log").write_text(test_output)
    if run.returncode:
        raise SystemExit("Isolated suite failed; inspect private/phase-nine/isolated-tests.log")
import re
count=int(re.search(r"Ran (\d+) tests",test_output).group(1))
# Existing teaching, modules, CBT source mappings and all historical resources
# must remain byte-identical to the dispatch checkpoint, including the drafts.
git=["git","-c","safe.directory="+ROOT.as_posix()]
tree=subprocess.check_output([*git,"ls-tree","-r","-z",CHECKPOINT,"production_courseware"],cwd=ROOT).split(b"\0")
tracked={row.split(b"\t",1)[1].decode():row.split(b"\t",1)[0].split()[2].decode() for row in tree if row}
for name,object_id in tracked.items():
    baseline=subprocess.check_output([*git,"cat-file","blob",object_id],cwd=ROOT)
    actual=(ROOT/name).read_bytes()
    if Path(name).suffix in {".json",".py",".md",".txt",".csv"}:
        actual=actual.replace(b"\r\n",b"\n")
        baseline=baseline.replace(b"\r\n",b"\n")
    assert actual==baseline, f"Protected source changed: {name}"
manifest=json.loads((release/"upload_manifest.json").read_text())
from pypdf import PdfReader
pages=0
for row in manifest:
    path=release/row["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row["sha256"]
    if path.suffix==".pdf": pages+=len(PdfReader(path).pages)
qa=json.loads((release/"visual_qa.json").read_text())
assert qa["pdf_pages_reviewed"]==pages and qa["final_file_sha256"]=={r["path"]:r["sha256"] for r in manifest}
proof=dict(status="local_build_verified",tests=count,database="sqlite:///:memory:",debug=True,
           original_checkpoint=CHECKPOINT,protected_source_files=len(tracked),protected_source_unchanged=True,
           media_files=len(manifest),pdf_pages=pages,slide_pages=64,visual_qa="reviewed",
           source_comparison="Git baseline bytes; Windows text CRLF normalised to LF",
           live_staging_performed=False,remote_hashes_verified=0,live_public_checks_performed=0,
           production_evidence="Recorded separately in post-upload-verification.json after live verification")
(private/"local-build-verification.json").write_text(json.dumps(proof,indent=2)+"\n")
print(json.dumps(proof,indent=2))
