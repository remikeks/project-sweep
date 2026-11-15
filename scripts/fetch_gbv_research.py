"""Archive public GBV evidence and retrieval failures for private staff appraisal."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gbv_fetch",Path(__file__).with_name("fetch_ert_research.py"))
fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
fetch.OUT=ROOT/"production_courseware/private/phase-seven/research"
SOURCES=[
    ("S10","https://unfpa.org/sites/default/files/pub-pdf/19-200_Minimun_Standards_Report_ENGLISH-Nov.FINAL_.pdf",None),
    ("S11","https://www.gbvims.com/wp/wp-content/uploads/Interagency-GBV-Case-Management-Guidelines_Final_2017_Low-ResEn.pdf",None),
    ("S12-page","https://gbvguidelines.org/en/pocketguide/",None),
    ("S12","https://gbvguidelines.org/wp/wp-content/uploads/2018/03/GBV_PocketGuide021718.pdf",None),
    ("S13","https://www.who.int/publications/i/item/9789240087873",None),
    ("R21","https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0334905","10.1371/journal.pone.0334905"),
    ("R22","https://journals.sagepub.com/doi/10.1177/15248380251383933","10.1177/15248380251383933"),
    ("R23","https://link.springer.com/article/10.1186/s12905-026-04790-8","10.1186/s12905-026-04790-8"),
    ("IJSDS-articles","https://www.ijsds.org/articles",None),
    ("Q-TVA","https://www.scimagojr.com/journalsearch.php?clean=0&q=13124&tip=sid",None),
    ("Q-PLOS","https://www.scimagojr.com/journalrank.php?ord=desc&order=titem&type=j&wos=true",None),
]
if __name__=="__main__":
    fetch.OUT.mkdir(parents=True,exist_ok=True)
    receipt=fetch.OUT/"retrieval.json"
    if receipt.exists():raise SystemExit("Existing evidence receipt; use a fresh batch rather than overwrite")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch.retrieve,SOURCES))
    receipt.write_text(json.dumps(records,indent=2)+"\n",encoding="utf-8")
    for record in records:print(record["id"],record.get("primary",{}).get("content_status",record.get("primary",{}).get("error")))
