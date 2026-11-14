"""Retrieve public publisher and DOI metadata for the foundational review batch."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "production_courseware/private/school-phase2-2026-11-14/research"
OUT.mkdir(parents=True, exist_ok=True)
records = [
    ("R1", "10.1371/journal.pone.0303013", "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0303013"),
    ("R2", "10.3389/fresc.2024.1383995", "https://www.frontiersin.org/journals/rehabilitation-sciences/articles/10.3389/fresc.2024.1383995/full"),
    ("R3", "10.3389/frhs.2025.1632307", "https://www.frontiersin.org/journals/health-services/articles/10.3389/frhs.2025.1632307/full"),
    ("R4", "10.1186/s12910-025-01330-1", "https://link.springer.com/article/10.1186/s12910-025-01330-1"),
    ("R5", "10.67007/ijsds-2026-v2_i1_008", "https://www.ijsds.org/article/corruption-professional-social-work-and-social-welfare-delivery-in-nigeria-a-qualitative-analysis-of-institutional-barriers-to-social-justice+10.67007-ijsds-2026-v2_i1_008"),
]
receipts=[]
for rid,doi,url in records:
    receipt={"id":rid,"doi":doi,"publisher":url}
    for kind,target in [("crossref", "https://api.crossref.org/works/"+quote(doi,safe="")),("publisher",url)]:
        try:
            with urlopen(Request(target,headers={"User-Agent":"SWEEP-Academy-curriculum-evidence-review"}),timeout=40) as r:
                raw=r.read()
                receipt[kind]={"status":r.status,"url":r.url,"sha256":hashlib.sha256(raw).hexdigest()}
                (OUT/(rid+"-"+kind+(".json" if kind=="crossref" else ".html"))).write_bytes(raw)
                if kind=="crossref":
                    msg=json.loads(raw)["message"]
                    receipt["title"]=msg.get("title",[])
                    receipt["year"]=msg.get("published",{}).get("date-parts",[])
                    receipt["licence"]=msg.get("license",[])
                    receipt["corrections"]=msg.get("update-to",[])
        except Exception as exc:
            receipt[kind]={"error_type":type(exc).__name__}
    receipts.append(receipt)
    print(rid, receipt.get("title",["Metadata not verified"])[0], {k:v.get("status",v.get("error_type")) for k,v in receipt.items() if k in ("publisher","crossref")})
(OUT/"retrieval-receipts.json").write_text(json.dumps(receipts,indent=2),encoding="utf-8")
