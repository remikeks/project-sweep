"""Original ERT foundation teaching, evidence appraisal and review questions."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
old=json.loads((ROOT/"production_courseware/phase_four/fsw_batch_02/review_package.json").read_text(encoding="utf-8"))
REFERENCES=[r for r in old["references"] if r["id"] in {"S1","R8"}]
REFERENCES += [
dict(id="S2",author="IPCC",year=2023,title="Climate Change 2023 Synthesis Report Summary for Policymakers",
    url="https://www.ipcc.ch/report/ar6/syr/downloads/report/IPCC_AR6_SYR_SPM.pdf",kind="intergovernmental evidence assessment",
    use="Risk context, adaptation, equity and possible maladaptation.",appraisal="Global synthesis, especially A.2, A.3 and C.5. It cannot specify a site's engineering design, predict an individual's outcome or attribute a local event without suitable evidence.",
    licence="Linked official report and original commentary only",link_label="ipcc.ch AR6 synthesis summary",slide_limit="Global assessment. Local decisions need appropriate site evidence."),
dict(id="S3",author="Council on Social Work Education",year=2022,title="Educational Policy and Accreditation Standards for Baccalaureate and Master's Social Work Programs",
    url="https://www.cswe.org/sites/default/files/2026-07/2022_EPAS.pdf",kind="professional education benchmark",
    use="Environmental justice, research-informed practice, assessment, intervention and evaluation competencies.",
    appraisal="Current adopted 2022 US degree-programme standards checked on 14 November 2026. A 2029 draft is not treated as adopted. Selected learning-domain mapping does not confer accreditation, degree equivalence or Nigerian professional registration.",
    licence="All rights reserved. Link and original curriculum commentary only; no exercises or text reproduced",link_label="cswe.org 2022 EPAS",slide_author="CSWE",slide_title="2022 Educational Policy and Accreditation Standards",slide_limit="US degree benchmark. No accreditation or registration conferred."),
dict(id="S6",author="Council on Social Work Education",year=2020,title="Curricular Guide for Environmental Justice 2015 EPAS Curricular Guide Resource Series",
    url="https://www.cswe.org/sites/default/files/2026-07/Curricular_Guide_Environmental_Justice_2015_EPAS.pdf",kind="specialist curriculum resource",
    use="Environmental-justice relevance across generalist social work learning domains.",
    appraisal="2020 guide aligned to the older 2015 EPAS. Used as a supplementary subject map, read alongside adopted 2022 EPAS, not a current accreditation standard or a Nigerian curriculum mandate.",
    licence="All rights reserved; individual reading only. Linked benchmark; no guide text, assignments or exercises copied or adapted",link_label="cswe.org Environmental justice guide",slide_author="CSWE",slide_title="Curricular Guide for Environmental Justice (2020)",slide_limit="Supplementary 2015-EPAS guide. Read with current adopted standards."),
dict(id="S4",author="WHO Regional Office for Europe",year=2026,title="Heat-health action plans guidance second edition Executive summary",
    url="https://www.who.int/docs/librariesprovider2/default-document-library/who-hhap-guidance-exec-summary-eng-2026.pdf?download=true",kind="public health implementation guidance",
    use="Coordinated heat preparedness, communication, social-care access and monitoring.",
    appraisal="Official 26-page executive-summary file read, not the complete 272-page report. Designed for the European Region; Nigerian application needs local public-health authorities, capacity checks and approved response arrangements. Not an individual treatment protocol.",
    licence="CC BY-NC-SA 3.0 IGO stated for the linked guidance. Original commentary only; no message bank or figures reproduced",link_label="who.int Heat-health guidance 2026",slide_author="WHO Europe",slide_limit="European guidance. Adapt through authorised local public-health arrangements."),
dict(id="S5",author="World Health Organization",year=2021,title="WHO global air quality guidelines particulate matter ozone nitrogen dioxide sulfur dioxide and carbon monoxide",
    url="https://www.who.int/publications/i/item/9789240034228",kind="public health guideline overview",
    use="Distinguish measured pollutant concentrations, health guidance and local regulatory standards.",
    appraisal="Official publication overview checked. No numerical guideline or clinical threshold is reproduced. A technical reading needs pollutant, unit, averaging period, instrument quality and applicable local interpretation; a smell report does not establish a measured concentration.",
    licence="Official linked overview; original commentary only",link_label="who.int Global air quality guidelines",slide_author="WHO",slide_title="WHO global air quality guidelines (2021)",slide_limit="Guideline overview, not a Nigerian legal limit or personal diagnosis."),
dict(id="R1",author="Narhi K, Matthies AL, Stamm I and Hirvilammi T",year=2025,title="Social work practitioners' views of ecosocial work",
    doi="10.1177/14680173251336105",url="https://doi.org/10.1177/14680173251336105",kind="qualitative focus-group study",
    use="Human-nature relationships and organisational conditions for ecosocial practice.",
    appraisal="Published online June 2025, issue January 2026. Fourteen already-interested social workers in three Finnish locations; focus groups over three cycles. Selected practitioner perspectives in a Nordic welfare setting, not representative Nigerian findings or tested intervention effects. Publisher methods and limitations read through indexed full text.",
    licence="CC BY 4.0; original commentary, no participant quotes or figures reproduced",quartile="Journal quartile not independently verified for this batch",slide_title="Social work practitioners' views of ecosocial work",slide_author="Narhi K and colleagues",slide_limit="Fourteen selected Finnish practitioners. No representative or causal claim."),
dict(id="R2",author="Parsons M and colleagues",year=2025,title="Participatory approaches to climate adaptation, resilience, and mitigation: A systematic review",
    doi="10.1007/s13280-025-02202-z",url="https://pmc.ncbi.nlm.nih.gov/articles/PMC12569303/",kind="systematic thematic review",
    use="Power, meaningful influence and exclusion in participatory climate processes.",
    appraisal="187 English-language peer-reviewed articles from Scopus covering 2015-2020 despite 2025 publication. Excludes grey and non-English knowledge; thematic interpretation rather than a pooled effectiveness estimate. Full text read. A local meeting's fairness or impact still needs direct checking.",
    licence="CC BY 4.0; original commentary only",quartile="SCImago's search-indexed 2025 Ambio record reports SJR Q1 (including Geography Planning and Development). Direct table access returned 403; JCR quartile not independently verified. https://www.scimagojr.com/journalsearch.php?clean=0&q=22704&tip=sid",
    slide_title="Participatory approaches to climate adaptation, resilience and mitigation",slide_limit="Thematic review; 2015-2020 literature. No local effectiveness guarantee."),
dict(id="R3",author="Wright CY and colleagues",year=2026,title="Air Pollution and Heat Impacts on Respiratory Morbidity and Mortality Outcomes in Africa: A Systematic Review Towards a Meta-analysis",
    doi="10.1007/s40572-026-00561-7",url="https://doi.org/10.1007/s40572-026-00561-7",kind="rapid systematic review",
    use="African pollution evidence and the gap in evidence on heat-respiratory interactions.",
    appraisal="Thirteen included studies with mixed observational designs, despite the stated case-control focus. Limited database coverage and heterogeneous reporting. Abstract says only three considered temperature and none tested heat-respiratory interactions. Protocol/preprint references and inconsistent design counts warrant caution. No pooled local effect or proven heat-pollution interaction is used here. Publisher methods, quality appraisal and limitations read through indexed full text; direct HTML was a challenge page, not archived full text.",
    licence="CC BY 4.0 verified through publisher/Crossref metadata; original commentary only",
    quartile="SCImago's indexed Switzerland journal table reports SJR Q1 for Current Environmental Health Reports; category/year table and JCR quartile were not independently downloaded. https://www.scimagojr.com/journalrank.php?country=CH&ord=desc&order=rpd&type=j&wos=true",
    slide_title="Air pollution and heat: African respiratory-health evidence review",slide_limit="Mixed study designs. No heat-respiratory interaction established."),
]
EVIDENCE_NOTE="Evidence checked 14 November 2026. Sources distinguish adopted standards, supplementary curricula, public-health guidance and research. SCImago Q1 records were visible in the provider's search-indexed results; direct ranking-table access was restricted. No JCR quartile or IJSDS quartile is claimed. Journal ranking does not establish article validity. Review the limits alongside every application."

def m(title,outcome,paragraphs,example,activity,feedback,sources,items):
    return dict(title=title,outcome=outcome,paragraphs=paragraphs,example=example,activity=activity,feedback=feedback,sources=sources,items=items)

def c(code,title,slug,cover,outcome,modules):
    return dict(code=code,title=title,slug=slug,cover_title=cover,school_code="ERT",
        school_name="School of Ecosocial Resilience and Environmental Social Work",school_display="Ecosocial Resilience and\nEnvironmental Social Work",
        estimated_minutes=180,audience="Beginning community practitioners and social work learners working within authorised roles and supervision.",outcome=outcome,modules=modules)

COURSES=[]
for filename in ["ecosocial.py","assessment.py","adaptation.py","heat_pollution.py"]:
    spec=importlib.util.spec_from_file_location("ert_"+Path(filename).stem,Path(__file__).with_name(filename))
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    COURSES.append(source.course(c,m))
