"""Archive public ERT evidence and explicit retrieval failures for staff review."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"production_courseware/private/phase-five/research"
SOURCES=[
    ("R1-copy","https://jyx.jyu.fi/bitstreams/80f6771b-b579-4eee-ad19-082676853ec7/download",None),
    ("R1","https://journals.sagepub.com/doi/full/10.1177/14680173251336105","10.1177/14680173251336105"),
    ("R2","https://pmc.ncbi.nlm.nih.gov/articles/PMC12569303/","10.1007/s13280-025-02202-z"),
    ("R3","https://link.springer.com/article/10.1007/s40572-026-00561-7","10.1007/s40572-026-00561-7"),
    ("S2","https://www.ipcc.ch/report/ar6/syr/downloads/report/IPCC_AR6_SYR_SPM.pdf",None),
    ("S3","https://www.cswe.org/sites/default/files/2026-07/2022_EPAS.pdf",None),
    ("S6","https://www.cswe.org/sites/default/files/2026-07/Curricular_Guide_Environmental_Justice_2015_EPAS.pdf",None),
    ("S4","https://www.who.int/docs/librariesprovider2/default-document-library/who-hhap-guidance-exec-summary-eng-2026.pdf?download=true",None),
    ("S5","https://www.who.int/publications/i/item/9789240034228",None),
    ("Q1","https://www.scimagojr.com/journalsearch.php?clean=0&q=22704&tip=sid",None),
]

def retrieve(row):
    rid,url,doi=row
    record=dict(id=rid,url=url)
    for kind,target in [("primary",url),*([("crossref","https://api.crossref.org/works/"+quote(doi,safe=""))] if doi else [])]:
        try:
            with urlopen(Request(target,headers={"User-Agent":"SWEEP-Academy-curriculum-evidence-review"}),timeout=40) as response:
                raw=response.read();mime=response.headers.get("Content-Type","");final=response.url
            suffix=".pdf" if raw.startswith(b"%PDF") else (".json" if kind=="crossref" else ".html")
            (OUT/(rid+"-"+kind+suffix)).write_bytes(raw)
            challenge=any(marker in raw for marker in (b"Client Challenge",b"JavaScript is disabled",b"Just a moment"))
            record[kind]=dict(url=final,bytes=len(raw),mime=mime,sha256=hashlib.sha256(raw).hexdigest(),
                content_status="challenge_page_not_evidence" if challenge else "retrieved_not_independently_appraised")
        except Exception as exc:
            record[kind]=dict(error=type(exc).__name__)
    return record

if __name__=="__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(retrieve,SOURCES))
    (OUT/"retrieval.json").write_text(json.dumps(records,indent=2)+"\n",encoding="utf-8")
    for row in records: print(row["id"],{k:row[k] for k in ("primary","crossref") if k in row})
