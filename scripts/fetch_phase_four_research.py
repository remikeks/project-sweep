"""Retrieve public evidence for FSW batch two; never contact learner services."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"production_courseware/private/phase-four/research"
OUT.mkdir(parents=True,exist_ok=True)
sources=[
    ("R6","10.1093/bjsw/bcaf310","https://academic.oup.com/bjsw/article/56/4/2037/8425635"),
    ("R7","10.1093/bjsw/bcaf029","https://academic.oup.com/bjsw/article/55/5/1976/8015828"),
    ("R8","10.67007/ijsds-2026-v2_i2_002","https://www.ijsds.org/article/compounding-vulnerabilities-an-architectural-study-of-the-socio-spatial-economic-and-environmental-characteristics-of-marginalized-waterfront-communities-in-port-harcourt-nigeria-and-its-implications-for-social-work-and-development-practice+10.67007-ijsds-2026-v2_i2_002"),
    ("R9","10.1177/14680173261435141","https://journals.sagepub.com/doi/full/10.1177/14680173261435141"),
    ("R10","10.1093/bjsw/bcae124","https://oro.open.ac.uk/98873/8/98873final.pdf"),
    ("S5",None,"https://ndpc.gov.ng/wp-content/uploads/2025/03/NDP-ACT-GAID-2025-MARCH-20TH.pdf"),
    ("S4",None,"https://openstax.org/books/lifespan-development/pages/1-4-contexts-and-settings-of-development"),
]

def get(url):
    with urlopen(Request(url,headers={"User-Agent":"SWEEP-Academy-curriculum-evidence-review"}),timeout=40) as r:
        return r.read(),r.headers.get("Content-Type",""),r.url

def fetch(source):
    rid,doi,url=source
    record=dict(id=rid,doi=doi,url=url)
    for kind,target in [("publisher",url),*([("crossref","https://api.crossref.org/works/"+quote(doi,safe=""))] if doi else [])]:
        try:
            raw,mime,final=get(target)
            suffix=".json" if kind=="crossref" else (".pdf" if raw.startswith(b"%PDF") else ".html")
            (OUT/(rid+"-"+kind+suffix)).write_bytes(raw)
            record[kind]=dict(bytes=len(raw),mime=mime,url=final,sha256=hashlib.sha256(raw).hexdigest())
            if kind=="crossref":
                m=json.loads(raw)["message"]
                record.update(title=m.get("title"),authors=[a.get("given","")+" "+a.get("family","") for a in m.get("author",[])],year=m.get("published",{}).get("date-parts"),licence=m.get("license",[]),updates=m.get("update-to",[]))
            if rid=="R8" and kind=="publisher":
                links=re.findall(r'href="([^"]+\.pdf)"',raw.decode("utf-8"))
                for link in links[:1]:
                    pdf,_,_=get(link);(OUT/(rid+"-fulltext.pdf")).write_bytes(pdf)
                    record["pdf"]=dict(url=link,bytes=len(pdf),sha256=hashlib.sha256(pdf).hexdigest())
        except Exception as exc:
            record[kind]=dict(error=type(exc).__name__)
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(fetch,sources))
(OUT/"retrieval.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
for r in results:
    print(r["id"],r.get("title"),r.get("authors"),{k:r.get(k) for k in ("publisher","pdf")})

# Public institutional OA copies, not an access-control workaround. HTTP errors
# remain explicit; a successful download is not evidence that the text was read.
repositories=[
    ("R6","https://jyx.jyu.fi/bitstreams/48e24f4e-a53a-4173-95e9-55ee3ddaa83e/download"),
    ("R7","https://ueaeprints.uea.ac.uk/id/eprint/98303/1/RGI_paper_accepted_submission.pdf"),
]
copies=[]
for rid,url in repositories:
    try:
        raw,mime,final=get(url)
        if not raw.startswith(b"%PDF"): raise ValueError("Expected a public PDF")
        name=rid+"-fulltext.pdf"
        (OUT/name).write_bytes(raw)
        copies.append(dict(name=name,url=final,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    except Exception as exc:
        copies.append(dict(id=rid,url=url,error=type(exc).__name__))
(OUT/"repository-retrieval.json").write_text(json.dumps(copies,indent=2)+"\n",encoding="utf-8")
