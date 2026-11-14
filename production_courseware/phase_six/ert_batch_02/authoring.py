"""Original ERT completion-batch teaching and evidence records."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
previous=json.loads((ROOT/"production_courseware/phase_five/ert_batch_01/review_package.json").read_text(encoding="utf-8"))
REFERENCES=[r for r in previous["references"] if r["id"] in {"S1","S2","S3","R2","R8"}]
REFERENCES += [
dict(id="S7",author="Global Protection Cluster",year=2025,title="Role of Protection Clusters in Durable Solutions for Internally Displaced Persons Practical Guidance",
    url="https://globalprotectioncluster.org/sites/default/files/2025-03/ds_guidance_full_document_annex_2025.03.19_pm.pdf",kind="interagency operational guidance",
    use="Voluntary informed decisions, participation, livelihoods and rights-based review of displacement support.",
    appraisal="Official 54-page guidance file; relevant decision-making, pathways, evidence and early-groundwork sections read. An operational framework, not an individual legal determination, Nigerian policy substitute or proof that relocation is safe or a durable solution has been achieved.",
    licence="Official linked guidance; original teaching only, no tools or annexes reproduced",slide_author="Global Protection Cluster",slide_title="Durable solutions: protection-cluster practical guidance",link_label="globalprotectioncluster.org Guidance 2025",slide_limit="Operational framework. No individual legal status or safety certification."),
dict(id="S8",author="Global Indigenous Data Alliance",year=2022,title="Indigenous Data Sovereignty and Governance",
    url="https://www.gida-global.org/s/Final_Attribution_NonCommercial_NoDerivatives_4_International.pdf",kind="Indigenous data-governance educational resource",
    use="Collective benefit, authority to control, responsibility and ethics when discussing knowledge use.",
    appraisal="The actual linked file is a 29-page 2022 presentation, not a two-page CARE poster. Read with GIDA's CARE principles page. Indigenous-led governance benchmark; it does not identify a Nigerian group's protocols, replace individual rights or settle local legal authority.",
    licence="CC BY-NC-ND 4.0. Linked resource and original factual commentary only; no slides, graphics, translated principles sheet or adapted exercises reproduced",slide_author="GIDA",slide_title="Indigenous Data Sovereignty and Governance (2022)",link_label="gida-global.org Governance and CARE",slide_limit="Community authority needs local agreement. No unrestricted sharing implied."),
dict(id="S9",author="OECD",year=2021,title="Applying Evaluation Criteria Thoughtfully",
    doi="10.1787/543e84ed-en",url="https://www.oecd.org/en/publications/2021/03/applying-evaluation-criteria-thoughtfully_45a54ea7.html",kind="evaluation guidance",
    use="Purpose-driven evaluation questions concerning relevance, coherence, effectiveness, efficiency, impact and sustainability.",
    appraisal="Guidance and relevant criteria/application sections read in the official 84-page PDF file. Criteria are evaluative lenses, not a causal-identification method or mandatory identical checklist. No source examples or scoring instrument are reproduced.",
    licence="Copyright OECD 2021. Linked guidance and original commentary only",slide_title="Applying Evaluation Criteria Thoughtfully",slide_limit="Choose criteria for purpose. Criteria alone do not establish attribution."),
dict(id="R4",author="Sengupta M",year=2025,title="Environmental immobility: A systematic review of empirical research",
    doi="10.1007/s13280-025-02195-9",url="https://pmc.ncbi.nlm.nih.gov/articles/PMC12480326/",kind="systematic empirical-literature review",
    use="Choices, constraints and changing mobility/staying aspirations in environmental change.",
    appraisal="55 studies; English-language Scopus/Web of Science search in February 2024, with supplementary searching. Uneven geography, including 20 Bangladesh studies, and mainly qualitative evidence. Not a Nigerian prevalence estimate, event attribution or validated tool for assigning people a fixed mobility category.",
    licence="CC BY 4.0; original commentary, no source diagram or cases copied",quartile="Ambio: SCImago search-indexed 2025 SJR Q1 record, as in the preceding batch; direct table access restricted and JCR not independently verified.",slide_limit="Uneven contexts and methods. Ask about preferences and constraints directly."),
dict(id="R5",author="Dorji T and colleagues",year=2024,title="Understanding How Indigenous Knowledge Contributes to Climate Change Adaptation and Resilience: A Systematic Literature Review",
    doi="10.1007/s00267-024-02032-x",url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11549107/",kind="systematic literature review",
    use="Diversity of knowledge practices and the importance of context in community stewardship.",
    appraisal="71 English-language Scopus papers from 2014 to May 2024, narrowed by indexed keywords; substantial Africa/Asia concentration. Maps reported practices, not a pooled effectiveness estimate or permission to transfer a practice, publish restricted knowledge or provide treatment. Full methods and conclusion read.",
    licence="CC BY 4.0; original commentary only; no cultural practices, source figures or exercises reproduced",quartile="Environmental Management quartile not independently verified for this batch",slide_author="Dorji T and colleagues",slide_title="Indigenous knowledge, climate adaptation and resilience: a review",slide_limit="Context-specific reported practices. No universal transfer or treatment advice."),
dict(id="R7",author="Rastogi S, Werner M, van Cauwenbergh N and van den Homberg M",year=2026,title="Operationalising local knowledge to enhance climate services: evidence from a systematic review",
    doi="10.1016/j.cliser.2026.100665",url="https://doi.org/10.1016/j.cliser.2026.100665",kind="systematic review of literature and project documents",
    use="Decision-focused knowledge relationships across climate-service roles.",
    appraisal="119 articles and documentation of 22 operational projects; Scopus-based search and uneven project reporting. Publisher indexed methods/results and TU Delft repository record read; full PDF retrieval restricted. Findings inform questions about knowledge use and participation, not a tested local intervention effect or equivalence between Indigenous and all local knowledge.",
    licence="CC BY 4.0 verified in Crossref and TU Delft record; original commentary only",quartile="Climate Services: SCImago's indexed 2025 provider record reports SJR 1.342 Q1. Direct table retrieval not independently downloaded. https://www.scimagojr.com/journalsearch.php?clean=0&q=21100463842&tip=sid",slide_author="Rastogi S and colleagues",slide_title="Operationalising local knowledge to enhance climate services",slide_limit="Review and project reporting. No local effect or unrestricted-use permission."),
dict(id="R10",author="Horneman F, Torresan S, Furlan E and Critto A",year=2026,title="Exploring nature-based solutions' effectiveness indicators for climate change adaptation: a systematic review",
    doi="10.3389/fenvs.2025.1603919",url="https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2025.1603919/full",kind="systematic review and scientometric analysis",
    use="Selecting indicators that cover intended outcomes, social effects and trade-offs.",
    appraisal="Published 9 January 2026 despite 2025 DOI/volume. 27 articles, 36 coastal/transitional case studies, English Scopus literature through June 2023. Limited socio-economic coverage and no universal evaluation tool. Full primary methods/results read. This course uses evaluation questions, not engineering designs or ecological effect estimates.",
    licence="CC BY 4.0; original commentary, no figures or tables reproduced",quartile="Frontiers' 2026 impact table reports 2025 Environmental Science JIF Q2 and CiteScore Q1. Publisher-reported; category details and independent JCR verification not obtained. https://www.frontiersin.org/about/impact",slide_author="Horneman F and colleagues",slide_title="Nature-based adaptation: effectiveness indicators review",slide_limit="Coastal/transitional cases; literature to 2023. No universal indicator set."),
]
EVIDENCE_NOTE="Evidence checked 14 November 2026. Publication dates and reviewed evidence periods are distinguished. Journal metrics are limited to identified provider records and are not article-quality certification. No IJSDS, Environmental Management or independent JCR quartile is claimed. Guidance supports original practice exercises; local authority, community protocols and independent academic review remain necessary."

def m(title,outcome,paragraphs,example,activity,feedback,sources,items):
    return dict(title=title,outcome=outcome,paragraphs=paragraphs,example=example,activity=activity,feedback=feedback,sources=sources,items=items)

def c(code,title,slug,cover,outcome,modules):
    return dict(code=code,title=title,slug=slug,cover_title=cover,school_code="ERT",
        school_name="School of Ecosocial Resilience and Environmental Social Work",school_display="Ecosocial Resilience and\nEnvironmental Social Work",
        estimated_minutes=180,audience="Beginning community practitioners and social work learners applying ecosocial practice under appropriate authority and supervision.",outcome=outcome,modules=modules)

COURSES=[]
for filename in ["displacement.py","stewardship.py","evaluation.py"]:
    spec=importlib.util.spec_from_file_location("ert_completion_"+Path(filename).stem,Path(__file__).with_name(filename))
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    COURSES.append(source.course(c,m))
