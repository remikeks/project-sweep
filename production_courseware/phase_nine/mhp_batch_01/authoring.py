"""Original MHP extension teaching; retained clinical/addiction courses unchanged."""
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
old=json.loads((ROOT/"production_courseware/phase_eight/gbv_batch_02/review_package.json").read_text(encoding="utf-8"))
REFERENCES=[dict(r) for r in old["references"] if r["id"]=="S1"]
def ref(id,author,year,title,url,kind,use,appraisal,licence,slide_title,slide_limit,**extra):
    return dict(id=id,author=author,year=year,title=title,url=url,kind=kind,use=use,appraisal=appraisal,licence=licence,
        slide_author=author,slide_title=slide_title,slide_limit=slide_limit,**extra)
REFERENCES += [
ref("S21","WHO",2021,"Guidance on community mental health services: promoting person-centred and rights-based approaches",
    "https://www.who.int/publications/i/item/9789240025707","international service-system guidance",
    "Benchmark supported choice, inclusion, peer roles, community networks and accountable service design.",
    "Actual 296-file-page official PDF retrieved. Selected person-centred/rights-based principles, supported decisions, community inclusion and action sections read, not every case example. Published June 2021, not a newly issued 2026 standard. Service-system guidance and examples are not an approved academy curriculum, a Nigerian legal ruling or evidence that any particular local service is available.",
    "CC BY-NC-SA 3.0 IGO. Link and original factual commentary only; no source tools, models, forms, exercises, text or logos adapted/reproduced",
    "Community mental health: person-centred rights-based services","2021 system guidance. Local capacity, law and professional scope require review.",link_label="who.int Community mental health services"),
ref("S22","WHO",2025,"Guidance on mental health policy and strategic action plans: Module 1. Introduction, purpose and use of the guidance",
    "https://www.who.int/publications/i/item/9789240106796","policy framework introduction",
    "Connect service reform with lived-experience participation, workforce, governance and social/structural determinants.",
    "Actual 44-page official PDF retrieved; selected introduction, reform priorities, lived-experience and social/structural determinants sections read. Published 24 March 2025. This is Module 1, not appraisal of all five modules or detailed Module 2 directives. Policy framework is a comparator, not proof of legal compliance, clinical competence or local effectiveness.",
    "CC BY-NC-SA 3.0 IGO. Link and original factual commentary only; no source tables, action tools, exercises or logos copied/adapted",
    "Mental health policy reform: Module 1","2025 policy introduction. No claim to have reviewed all five modules.",link_label="who.int Mental health policy guidance 2025"),
ref("S23","WHO and UNICEF",2024,"Mental health of children and young people: service guidance",
    "https://www.who.int/publications/i/item/9789240100374","child/youth mental health service guidance",
    "Compare developmental fit, child participation, family roles, confidentiality, intersectoral support and transitions.",
    "Actual official linked PDF has 112 file pages, while the WHO publication page lists 122; discrepancy retained. Selected rights, participation, community/family support and integrated/transition sections read. No single service model fits every setting. Not training to diagnose or treat children, decide legal consent or substitute for qualified safeguarding and local procedures.",
    "CC BY-NC-SA 3.0 IGO. Link and original factual commentary only; no source service models, cases, forms, exercises or images reproduced/adapted",
    "Children and young people: mental health service guidance","112 PDF pages versus 122 in metadata. Developmental and local fit matter.",link_label="who.int Child and youth service guidance"),
ref("R29","MacRae A and colleagues",2026,"Understanding Trauma-Informed Care Across Settings: A Contemporary Definition, Values, Model, and Framework From an Integrative Review",
    "https://journals.sagepub.com/doi/10.1177/15248380261451829","conceptual integrative review",
    "Distinguish organisational trauma-informed support from trauma-focused clinical treatment and assess service conditions.",
    "Primary publisher indexed methods and limitations read; direct retrieval restricted, not archived full text. Online 22 May 2026; academic/grey searches to December 2024, English full-text frameworks. Rapid methods use single-reviewer screening/extraction with checks on 32 sources. Synthesises concepts, not intervention effects; proposed cross-sector model requires setting-specific validation and cannot prove recovery or diagnose trauma.",
    "CC BY-NC 4.0 in publisher/Crossref. Original factual commentary only; no model/framework diagrams, tables, exercises or quotations reproduced/adapted",
    "Trauma-informed care across settings: integrative review","Conceptual synthesis; rapid methods. Not a treatment-effect review.",doi="10.1177/15248380261451829",
    quartile="SCImago's own indexed 2025 Trauma Violence and Abuse record: SJR 2.896 Q1. Direct table restricted; no independent JCR claim. https://www.scimagojr.com/journalsearch.php?clean=0&q=13124&tip=sid"),
ref("R30","Croke S and colleagues",2026,"Digital peer support interventions for people with mental health conditions in outpatient settings: a systematic review and meta-analysis",
    "https://mentalhealth.bmj.com/content/ebmental/29/1/e302275.full.pdf","systematic review and meta-analysis",
    "Distinguish person-defined recovery/support from clinical outcomes and check access, training, safety and evidence limits.",
    "Actual eight-page publisher PDF retrieved; methods/results/limitations read. Published February 2026; search to January 2025, 29 studies/5,825 participants, variable bias and scarce long-term/safety reporting. Text says five databases but names four; limitation also says non-English excluded despite unrestricted-language search wording. Discrepancies retained; no numerical effect or universal safety/engagement claim taught. Mostly Western outpatient digital support, not all peers or Nigerian crisis care.",
    "CC BY 4.0 confirmed in PDF. Original commentary only; no source figures, datasets or intervention tools reproduced",
    "Digital peer support: systematic review and meta-analysis","Outpatient digital support; limited long-term/safety evidence. No universal effect.",doi="10.1136/bmjment-2025-302275",
    quartile="BMJ publisher 2025 metrics page reports SJR 2.833 and JIF 6.6; primary quartile table not obtained, so no BMJ Q1/Q2 claim in this batch. https://mentalhealth.bmj.com/pages/about/"),
ref("R31","Desatnik A and colleagues",2026,"Universal Parenting Interventions for Parents of Adolescents: A Systematic Review",
    "https://link.springer.com/article/10.1007/s10826-026-03286-1","systematic review with narrative synthesis",
    "Check voluntary participation, age range, caregiver involvement, accessibility and limits of programme transfer.",
    "Primary publisher indexed methods/results/limitations read; direct retrieval returned challenge, not archived full text. Published 18 March 2026, searches December 2022/repeated December 2023; 24 publications/20 interventions, parents of ages 11-21, face-to-face components, English and voluntary samples. Mostly single screening after a 20% reliability sample; registration retrospective. Heterogeneous outcomes/no meta-analysis; not evidence for all younger children, mandated child protection, digital-only support or a copied parenting programme.",
    "CC BY 4.0 publisher/Crossref. Original commentary; no source programme content, instruments or exercises copied",
    "Universal parenting for adolescents: narrative review","Search ends December 2023. Voluntary face-to-face programmes; transfer limits.",doi="10.1007/s10826-026-03286-1",
    quartile="SCImago's own indexed 2025 Journal of Child and Family Studies record: SJR 0.882 Q2 (including Life-span and Life-course Studies). Direct table restricted; no independent JCR claim. https://www.scimagojr.com/journalsearch.php?clean=0&q=15399&tip=sid"),
ref("R32","Isaacs AN and Duncan Z",2025,"Care coordination for persons with mental health challenges: a scoping review",
    "https://link.springer.com/article/10.1186/s13033-025-00679-5","adult care-coordination scoping review",
    "Clarify coordination roles, service eligibility, barriers and the difference between non-clinical navigation and treatment coordination.",
    "Primary publisher indexed methods/results/limitations read; direct HTML challenge, not archived full text. Published 18 August 2025; 18 papers, mostly USA/Australia, adults and diverse designs. Search excluded case-management/alternative terminology and multiple populations/settings, potentially missing similar models; no clear search end date established from inspected main methods. Scoping map and reported benefits are not a rigorous causal effectiveness estimate or universal eligibility standard. Clinical and non-clinical authority must be determined locally.",
    "CC BY-NC-ND 4.0 publisher/Crossref. Link and original factual commentary only; no source tables, model, tools or exercises copied/adapted",
    "Care coordination: adult mental health scoping review","Terminology and population exclusions. Effectiveness still needs rigorous studies.",doi="10.1186/s13033-025-00679-5"),
ref("R34","Linton S, Oduola S and Teague B",2026,"Perceptions and Experiences of Personal Recovery for Ethnic Minority People with Severe Mental Illness: A UK-informed Qualitative Systematic Review",
    "https://link.springer.com/article/10.1007/s10597-026-01676-9","qualitative systematic review",
    "Ask about personally meaningful identity, family and faith supports without assuming group consensus or benefit.",
    "Primary publisher indexed methods/findings/limitations read; direct HTML challenge, not archived full text. Published 28 July 2026; updated search 21 November 2025, 20 studies and Western settings with UK-informed severe-illness definitions. Within/between-group differences and lifespan variation insufficiently resolved; no causal treatment effect or universal Nigerian cultural rule. July 31 table-caption correction noted. Family may support or obstruct; faith is not assumed desired or a substitute for care.",
    "CC BY 4.0 publisher/Crossref. Original commentary only; no participant quotations, themes table, figures or tools reproduced",
    "Culture and personal recovery: qualitative synthesis","Western settings and differing illness definitions. Ask individuals; avoid stereotypes.",doi="10.1007/s10597-026-01676-9"),
ref("R35","Ejekaru GU and Adebusuyi JR",2025,"Sociocultural Factors Influencing Mental Health Rehabilitation in Ibadan, Oyo State",
    "https://www.ijsds.org/article/sociocultural-factors-influencing-mental-health-rehabilitation-in-ibadan-oyo-state%2B10.67007-ijsds-2025-0200036","single-hospital descriptive provider survey",
    "Use Nigerian context to pose questions about stigma, chosen supports and service barriers while critically appraising evidence.",
    "Actual linked 19-file-page IJSDS PDF retrieved, including issue front matter; selected abstract, methods, results and limitations read. 41 purposively sampled providers at Adeoyo, not service-user outcomes or a representative Nigerian sample. Cross-sectional self-report/selection bias; methods describe chi-square/correlation while abstract/results use regression, with inconsistent regression table degrees-of-freedom/sums/mean squares. Numerical findings are not taught or treated as causal proof; independent methods review needed. Used only as bounded contextual discussion alongside stronger guidance/syntheses.",
    "PDF front matter says all rights reserved; Crossref supplies no licence. Link and original factual commentary only; no full PDF, source text, tables, data or exercises redistributed/adapted",
    "Ibadan mental health rehabilitation: provider survey","Small single-site provider sample; inconsistent analysis reporting. No causal claim.",doi="10.67007/ijsds-2025-0200036",
    quartile="No Q1/Q2 status claimed for IJSDS"),
]
EVIDENCE_CHECKED_ON="2026-11-15"
EVIDENCE_NOTE="Checked 15 November 2026. Current OA studies complement WHO/UNICEF service guidance and Nigerian IJSDS context. Publication and evidence dates differ. Actual file-page counts, reporting inconsistencies, restricted retrievals and rights are explicit. Q1/Q2 statements use SCImago's own indexed records for Trauma Violence and Abuse/Journal of Child and Family Studies; direct tables restricted, no independent JCR claim. Rank is not article validity. Clinical/safeguarding, Nigerian practice/legal, lived-experience, accessibility/pilot and supervised-skills reviews remain pending."
REVIEW_REQUIREMENTS=dict(clinical_and_child_safeguarding="pending",lived_experience_review="pending",supervised_skills_demonstration="pending")
def m(title,outcome,paragraphs,example,activity,feedback,sources,items):
    return dict(title=title,outcome=outcome,paragraphs=paragraphs,example=example,activity=activity,feedback=feedback,sources=sources,items=items)
def c(code,title,slug,cover,outcome,modules):
    return dict(code=code,title=title,slug=slug,cover_title=cover,school_code="MHP",school_name="School of Mental Health and Psychosocial Care",school_display="Mental Health and\nPsychosocial Care",estimated_minutes=180,
        audience="Introductory social work and community-service learners using fictional scenarios. No diagnosis, therapy, prescribing, crisis-triage authority or independent child/clinical practice is conferred. Qualified roles, local procedures and supervised skills remain necessary.",
        study_guidance="Use only the supplied non-graphic fictional scenarios and invented aggregate data. Do not seek personal trauma histories, interview children or submit real health/service records. Write reasoning before checking feedback. You may pause or use an alternative fictional exercise. Supervised skills observation is separate.",
        practice_safety_note="Use only the supplied non-graphic fictional scenario or invented aggregate data. Do not collect personal trauma histories, interview children or submit real health records. You may pause or use an alternative fictional exercise. Record reasoning before checking guide feedback.",outcome=outcome,modules=modules)
COURSES=[]
for filename in ["cultural_care.py","rights_recovery.py","child_family.py","coordination.py"]:
    spec=importlib.util.spec_from_file_location("mhp_"+Path(filename).stem,Path(__file__).with_name(filename))
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    COURSES.append(source.course(c,m))
