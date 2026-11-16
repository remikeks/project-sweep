"""Retrieve primary MHP evidence; receipts and raw content remain private."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("mhp_fetch",Path(__file__).with_name("fetch_ert_research.py"))
fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
fetch.OUT=ROOT/"production_courseware/private/phase-nine/research"
SOURCES=[
 ("S21","https://iris.who.int/server/api/core/bitstreams/184ff4ef-9c4c-4aad-b1c5-437b08bc0184/content",None),
 ("S22","https://iris.who.int/server/api/core/bitstreams/b11d4d36-6e4b-47bb-977a-16d092c37a3d/content",None),
 ("S23","https://iris.who.int/server/api/core/bitstreams/5f3697e2-0696-48c1-a6e0-21c51b7da1a0/content",None),
 ("R29","https://journals.sagepub.com/doi/10.1177/15248380261451829","10.1177/15248380261451829"),
 ("R30","https://mentalhealth.bmj.com/content/ebmental/29/1/e302275.full.pdf","10.1136/bmjment-2025-302275"),
 ("R31","https://link.springer.com/article/10.1007/s10826-026-03286-1","10.1007/s10826-026-03286-1"),
 ("R32","https://link.springer.com/article/10.1186/s13033-025-00679-5","10.1186/s13033-025-00679-5"),
 ("R34","https://link.springer.com/article/10.1007/s10597-026-01676-9","10.1007/s10597-026-01676-9"),
 ("R35","https://www.ijsds.org/article/sociocultural-factors-influencing-mental-health-rehabilitation-in-ibadan-oyo-state%2B10.67007-ijsds-2025-0200036","10.67007/ijsds-2025-0200036"),
 ("R35-full","https://www.ijsds.org/api/pdf/bd8bac0e-f32d-4dcb-83de-d4382f3c8e8c.pdf",None),
]
def retrieve(source):
    record=fetch.retrieve(source)
    if record.get("primary",{}).get("bytes")==0:
        record["primary"]["content_status"]="empty_response_not_evidence"
    return record
if __name__=="__main__":
    fetch.OUT.mkdir(parents=True,exist_ok=True)
    target=fetch.OUT/"retrieval.json"
    if target.exists():raise SystemExit("Preserve existing research receipt")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(retrieve,SOURCES))
    with target.open("x",encoding="utf-8") as handle:json.dump(records,handle,indent=2)
    for r in records:print(r["id"],r.get("primary",{}).get("content_status",r.get("primary",{}).get("error")))
