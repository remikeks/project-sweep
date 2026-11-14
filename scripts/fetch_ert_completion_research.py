"""Archive public ERT completion-batch research without altering prior receipts."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ert_retrieval",Path(__file__).with_name("fetch_ert_research.py"))
fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
fetch.OUT=ROOT/"production_courseware/private/phase-six/research"
SOURCES=[
    ("R10","https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1603919/full","10.3389/fenvs.2025.1603919"),
    ("R11","https://www.nature.com/articles/s44168-026-00384-0","10.1038/s44168-026-00384-0"),
    ("R9","https://pmc.ncbi.nlm.nih.gov/articles/PMC13158384/","10.1016/j.joclim.2026.100666"),
    ("R7-copy","https://research.tudelft.nl/files/282545346/1-s2.0-S2405880726000336-main.pdf",None),
    ("R4","https://pmc.ncbi.nlm.nih.gov/articles/PMC12480326/","10.1007/s13280-025-02195-9"),
    ("R5","https://pmc.ncbi.nlm.nih.gov/articles/PMC11549107/","10.1007/s00267-024-02032-x"),
    ("R6","https://link.springer.com/article/10.1186/s13561-026-00840-x","10.1186/s13561-026-00840-x"),
    ("R7","https://www.sciencedirect.com/science/article/pii/S2405880726000336","10.1016/j.cliser.2026.100665"),
    ("S7","https://globalprotectioncluster.org/sites/default/files/2025-03/ds_guidance_full_document_annex_2025.03.19_pm.pdf",None),
    ("S8","https://www.gida-global.org/s/Final_Attribution_NonCommercial_NoDerivatives_4_International.pdf",None),
    ("S9","https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/03/applying-evaluation-criteria-thoughtfully_45a54ea7/543e84ed-en.pdf",None),
]
if __name__=="__main__":
    fetch.OUT.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch.retrieve,SOURCES))
    (fetch.OUT/"retrieval.json").write_text(json.dumps(records,indent=2)+"\n",encoding="utf-8")
    for record in records:print(record["id"],{k:record[k] for k in ("primary","crossref") if k in record})
