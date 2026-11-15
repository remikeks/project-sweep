"""Retrieve primary completion-batch evidence; keep raw records private."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gbv8_fetch",Path(__file__).with_name("fetch_ert_research.py"))
fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
fetch.OUT=ROOT/"production_courseware/private/phase-eight/research"
SOURCES=[
 ("S14-overview","https://www.who.int/publications/i/item/9789240107281",None),
 ("S16","https://www.unfpa.org/sites/default/files/pub-pdf/RESPECT%20framework%20second%20edition%20%281%29.pdf",None),
 ("S17","https://knowledge.unwomen.org/sites/default/files/2025-12/un-women-strategy-preventing-and-eliminating-technology-facilitated-violence-against-women-and-girls-en.pdf",None),
 ("S18","https://www.techsafety.org/resources-survivors/technology-safety-plan",None),
 ("S19-page","https://www.unfpa.org/publications/guidance-note-safe-and-ethical-management-analysis-and-sharing-gbv-service-data",None),
 ("S19","https://www.unfpa.org/sites/default/files/pub-pdf/Safe%20and%20Ethical%20Management%20of%20GBV%20Service%20Data_EN.pdf",None),
 ("S20-page","https://asiapacific.unfpa.org/en/publications/survivor-centred-approach-monitoring-gender-based-violence-response-programming-0",None),
 ("S20","https://asiapacific.unfpa.org/sites/default/files/pub-pdf/2024-10/A%20SURVIVOR-CENTERED%20APPROACH%20TO%20MONITORING%20GBV%20RESPONSE%20PROGRAMMING%20%20V5%20%282%29.pdf",None),
 ("R24-publisher","https://jogh.org/2023/jogh-13-04115/","10.7189/jogh.13.04115"),
 ("R25-publisher","https://bmjpublichealth.bmj.com/content/bmjph/3/1/e001126.full.pdf","10.1136/bmjph-2024-001126"),
 ("R26-publisher","https://obgyn.onlinelibrary.wiley.com/doi/full/10.1002/ijgo.70758","10.1002/ijgo.70758"),
 ("R27","https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0354526","10.1371/journal.pone.0354526"),
 ("R28","https://www.jmir.org/2026/1/e90068/","10.2196/90068"),
 ("Q-JMIR","https://www.jmir.org/announcements/701",None),
]
if __name__=="__main__":
 fetch.OUT.mkdir(parents=True,exist_ok=True)
 target=fetch.OUT/"retrieval.json"
 if target.exists():raise SystemExit("Preserve existing receipt; use a separate record for further retrievals")
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch.retrieve,SOURCES))
 target.write_text(json.dumps(records,indent=2)+"\n",encoding="utf-8")
 for r in records:print(r["id"],r.get("primary",{}).get("content_status",r.get("primary",{}).get("error")))
