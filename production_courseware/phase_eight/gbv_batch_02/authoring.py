"""Original GBV completion drafts; no clinical, legal or live assessment approval."""
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
previous=json.loads((ROOT/"production_courseware/phase_seven/gbv_batch_01/review_package.json").read_text(encoding="utf-8"))
REFERENCES=[dict(r) for r in previous["references"] if r["id"] in {"S1","S10","S11"}]
next(r for r in REFERENCES if r["id"]=="S11").update(
    use="Age-appropriate communication, best interests, evolving capacities, consent/assent and specialist safeguarding in child-marriage support.",
    appraisal="Actual 260-page official PDF retained from Phase 7. Selected updated child-marriage chapter, including best interests, evolving capacities and consent/assent, read for this phase. Its 2017 filename is not the chapter revision date: updated chapter announced October 2025. Introductory recognition and supervised referral boundaries only, not qualification for child casework, family mediation, clinical care or a Nigerian mandatory-reporting/legal-age decision.",
    slide_limit="Updated child-marriage chapter. Specialist safeguarding and local legal review required.")

def ref(id,author,year,title,url,kind,use,appraisal,licence,slide_title,slide_limit,**extra):
    return dict(id=id,author=author,year=year,title=title,url=url,kind=kind,use=use,appraisal=appraisal,
        licence=licence,slide_author=author,slide_title=slide_title,slide_limit=slide_limit,**extra)

REFERENCES += [
ref("S14","WHO",2025,"WHO guideline on the prevention of female genital mutilation and clinical management of complications",
    "https://www.who.int/publications/i/item/9789240107281","official guideline overview",
    "Distinguish prevention and access to qualified care from clinical procedures or medicalisation.",
    "Official 28 April 2025 publication overview read. Expanded prevention scope and training/educational recommendations compared; full 104-page guideline was not retrieved (IRIS returned HTML), so no full-guideline appraisal or clinical recommendation is claimed. Clinical procedures, diagnosis, treatment, examination and legal decisions excluded from this course.",
    "Link and original factual commentary only; no guideline text, diagrams, recommendations table or exercises reproduced",
    "FGM prevention and care: guideline overview","Overview only. No clinical procedures or specialist competence conferred.",link_label="who.int FGM guideline 2025"),
ref("S16","WHO",2025,"RESPECT women: preventing violence against women, second edition",
    "https://www.unfpa.org/sites/default/files/pub-pdf/RESPECT%20framework%20second%20edition%20%281%29.pdf","evidence-informed prevention framework",
    "Compare a prevention theory of change, sustained resources, participation and evaluation with a multi-strategy benchmark.",
    "Actual 34-page PDF retrieved; selected framework, implementation and monitoring sections read. Published 19 November 2025, not the 2019 first edition. Seven strategy domains are programme guidance, not proof that a short local awareness event reduces violence. Evidence and contextual adaptation still require critical review.",
    "CC BY-NC-SA 3.0 IGO. Linked source and original commentary only; no framework chart, tools, source exercises or logo reused",
    "RESPECT women: prevention framework, second edition","Programme framework. Local effect and implementation quality need evidence.",link_label="unfpa.org RESPECT second edition"),
ref("S17","UN Women",2025,"UN Women strategy: preventing and eliminating technology-facilitated violence against women and girls",
    "https://knowledge.unwomen.org/sites/default/files/2025-12/un-women-strategy-preventing-and-eliminating-technology-facilitated-violence-against-women-and-girls-en.pdf","institutional strategy",
    "Examine digital/offline continuity, gendered power, AI-related amplification and coordinated survivor-centred responses.",
    "Actual 51-page PDF retrieved; selected definition, technology/AI, survivor-centred response and monitoring sections read. Produced November 2025; URL upload month is not its publication date. Policy strategy, not a forensic test, platform-specific instruction, current Nigerian law or an intervention-effect trial. No headline global prevalence estimate is taught.",
    "CC BY-NC-ND 3.0 IGO. Link and original factual commentary only; no figures, strategy tables, source text, logo or adapted training tools",
    "Strategy on technology-facilitated violence","Strategy rather than a diagnostic test, legal rule or proven local intervention.",link_label="knowledge.unwomen.org TF VAWG strategy"),
ref("S18","NNEDV Safety Net",2018,"Technology Safety Plan: A Guide for Survivors and Advocates",
    "https://www.techsafety.org/resources-survivors/technology-safety-plan","specialist survivor-support guidance",
    "Prioritise an agreed safe channel and specialist planning before changing access, deleting content or reporting.",
    "Primary guidance page read; copyright 2018 is retained, not relabelled 2026. US legal/service references and older device examples are not Nigerian procedures or reliable diagnostic indicators. No single data-use or battery cue establishes spyware. No universal reset, deletion, disconnection or evidence-retention instruction is taught.",
    "Copyright NNEDV. Link and original commentary only; no adapted safety-plan template or copied instructions",
    "Technology safety: survivor-led planning","2018 US guidance. Current local specialist advice is needed.",link_label="techsafety.org Technology safety plan"),
ref("S19","UNFPA",2026,"Guidance note on safe and ethical management, analysis and sharing of GBV service data in the context of integrated SRH-GBV programming",
    "https://www.unfpa.org/sites/default/files/pub-pdf/Safe%20and%20Ethical%20Management%20of%20GBV%20Service%20Data_EN.pdf","service-data governance guidance",
    "Distinguish health records and GBV case information, minimise data and limit purpose-specific sharing.",
    "Actual 16-page PDF retrieved; purpose, definitions, consent, management, sharing and interpretation sections read. Official publication page dates this October 2026. Does not authorise research, prevalence estimation, access to clinical files or automatic linkage of co-located services. Context-specific reporting exceptions require qualified organisational/legal handling; none invented here.",
    "Copyright UNFPA. Linked guidance and original commentary only; no source forms, dilemma exercises or tools copied",
    "Safe and ethical GBV service data","October 2026 guidance. Service records are not population prevalence data.",link_label="unfpa.org Safe ethical GBV service data"),
ref("S20","UNFPA Asia and the Pacific",2024,"A Survivor-Centred Approach to Monitoring Gender-based Violence Response Programming",
    "https://asiapacific.unfpa.org/sites/default/files/pub-pdf/2024-10/A%20SURVIVOR-CENTERED%20APPROACH%20TO%20MONITORING%20GBV%20RESPONSE%20PROGRAMMING%20%20V5%20%282%29.pdf","response-programme monitoring guidance",
    "Check purpose, denominators, indirect identification, sensitive reporting and feasible accountability.",
    "Actual 29-page PDF retrieved, copyright 2024 confirmed on front matter; selected principles, stakeholder needs, sensitive data and risk sections read. Regional programming guidance, not a Nigerian research approval or permission for learners to gather survivor data. Published sample indicators are not copied or assumed validated for this academy.",
    "Copyright UNFPA 2024. Link and original commentary; no source indicator tables, forms or participant exercises reproduced",
    "Survivor-centred response monitoring","Monitoring requires specialist safeguards. Aggregate data can remain sensitive.",link_label="asiapacific.unfpa.org Response monitoring"),
ref("R24","Leight J and colleagues",2023,"Effectiveness of community mobilisation and group-based interventions for preventing intimate partner violence against women in low- and middle-income countries: A systematic review and meta-analysis",
    "https://jogh.org/2023/jogh-13-04115/","systematic review and RCT meta-analysis",
    "Interpret prevention evidence without transferring a pooled estimate or programme design directly to a new setting.",
    "Primary publisher indexed methods/results/limitations read; direct PDF download returned a restriction page, not an archived PDF. Search to 20 July 2021; 30 studies of 27 unique RCTs, substantial heterogeneity (I-squared 83%), English-only studies and self-report/selection limitations. Odds are not risks; neither a promised local effect nor a synthesis of attitude/norm outcomes is justified.",
    "Open-access publisher article. Link and original commentary only; no figures, participant data or intervention manuals reproduced",
    "Community/group IPV prevention: RCT synthesis","Search through July 2021; heterogeneous trials. No guaranteed local effect.",doi="10.7189/jogh.13.04115",
    quartile="SCImago provider-indexed 2025 Journal of Global Health record lists SJR Q1 (Health Policy). Direct table restricted; no independent JCR claim. https://www.scimagojr.com/journalsearch.php?clean=0&q=21100787508&tip=sid"),
ref("R25","Ullman C and colleagues",2025,"Interventions to prevent violence against women and girls globally: a global systematic review of reviews to update the RESPECT women framework",
    "https://bmjpublichealth.bmj.com/content/3/1/e001126","systematic review of reviews",
    "Compare strategy-level prevention evidence while examining quality, period and context.",
    "Actual 12-page primary publisher PDF read in selected methods/limitations sections. 178 reviews, searched January 2013-April 2022 despite January 2025 publication; variable review quality and omission of non-experimental policy evidence constrain conclusions. A review of reviews does not turn every activity under a strategy heading into an effective intervention.",
    "CC BY 3.0 IGO per publisher/Crossref. Original commentary only; no source tables or copied exercises",
    "RESPECT evidence: global review of reviews","Search ends April 2022. Variable review quality; no automatic local transfer.",doi="10.1136/bmjph-2024-001126"),
ref("R26","Meremikwu A and colleagues",2026,"A systematic review of group education or one-on-one counseling for the prevention of female genital mutilation in communities that perform female genital mutilation",
    "https://obgyn.onlinelibrary.wiley.com/doi/full/10.1002/ijgo.70758","systematic review of educational interventions",
    "Separate knowledge, attitude and reported commitment outcomes from demonstrated prevention of FGM.",
    "Primary publisher indexed methods, results and limitations read; direct download restricted, not archived full text. Online 26 January 2026; search to May 2023, four observational studies and very low-certainty findings. Outcomes concern knowledge/attitudes/commitment and reinfibulation requests; not proof of reduced incidence or a universally effective counselling technique. Nigerian Cochrane contributors do not make every included context Nigerian.",
    "CC BY-NC 4.0 per publisher/Crossref. Original factual commentary only; no figures or adapted tools",
    "Education and FGM prevention: evidence review","Four observational studies; very low certainty. No incidence-reduction claim.",doi="10.1002/ijgo.70758"),
ref("R27","Tarefa YA and Abdulai AF",2026,"Technology-facilitated gender-based violence against women and girls in sub-Saharan Africa: A scoping review",
    "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0354526","regional scoping review",
    "Examine digital abuse and access questions with regional and population coverage limits visible.",
    "Full primary publisher HTML methods/results/gaps read. Published 19 August 2026; search conducted September-November 2025. Reports 17 included studies/reports (14 original research), concentrated in a few countries and university/young populations. Maps reported forms and experiences, not representative regional prevalence, causation or an individual spyware diagnostic test.",
    "CC BY 4.0. Original commentary only; no source figures, survey items or participant accounts reproduced",
    "Technology-facilitated GBV in sub-Saharan Africa","Scoping map with uneven geographic/population coverage. No prevalence claim.",doi="10.1371/journal.pone.0354526",
    quartile="SCImago provider-indexed 2025 PLOS ONE record lists SJR Q1; direct table restricted. No independently verified JCR category claim. https://www.scimagojr.com/journalrank.php?ord=desc&order=titem&type=j&wos=true"),
ref("R28","Pak SHL and colleagues",2026,"Measuring Technology-Facilitated Sexual Violence and Abuse: Scoping Review of Existing Measures",
    "https://www.jmir.org/2026/1/e90068/","measurement scoping review",
    "Check construct, context and validation before treating a measure as suitable evidence of change.",
    "Primary publisher indexed methods/results/limitations read; local HTML retrieval returned empty content, so no archived full text claimed. Published 14 April 2026, search to 13 January 2026; 319 studies/218 measures, heavily Western high-income settings. No study-quality appraisal or measurement-robustness conclusion. TFSVA measures are narrower than all GBV; mental-health instruments used alongside them were not the review's object. A catalogue confers neither Nigerian validation nor permission to reproduce a questionnaire.",
    "Open-access publisher article. Linked source and original commentary only; no source instruments, item wording or figures copied",
    "Measuring technology-facilitated sexual violence","Scoping review without quality appraisal. Catalogue does not establish validity.",doi="10.2196/90068",
    quartile="Publisher announcement 18 June 2026 reports 2025 JIF Q1 in Health Care Sciences & Services and Medical Informatics. Publisher-reported, not an independent JCR download. https://www.jmir.org/announcements/701"),
]
EVIDENCE_CHECKED_ON="2026-11-15"
EVIDENCE_NOTE="Checked 15 November 2026. Publication dates and evidence periods are distinguished. Current 2025/2026 guidance and OA research are appraised alongside older specialist resources. Provider-indexed SJR and publisher-reported JIF Q1 status are identified with access limits; no BMJ Public Health, IJGO or IJSDS quartile is asserted. Journal rank is not article validity. Independent GBV/safeguarding, Nigerian practice/legal, accessibility, pilot and supervised skills reviews remain pending."
REVIEW_REQUIREMENTS=dict(specialist_GBV_and_safeguarding="pending",supervised_skills_demonstration="pending")
def m(title,outcome,paragraphs,example,activity,feedback,sources,items):
    return dict(title=title,outcome=outcome,paragraphs=paragraphs,example=example,activity=activity,feedback=feedback,sources=sources,items=items)
def c(code,title,slug,cover,outcome,modules):
    return dict(code=code,title=title,slug=slug,cover_title=cover,school_code="GBV",school_name="School of Gender Studies and Gender-Based Violence Prevention",school_display="Gender Studies and\nGBV Prevention",estimated_minutes=180,
        audience="Introductory social work and community-service learners using non-graphic fictional scenarios. No specialist child/GBV casework, clinical, forensic, legal or research competence is conferred; supervised skills and safeguarding review are separate requirements.",
        study_guidance="Use only the supplied non-graphic fictional scenarios and aggregate exercise data. Do not seek real disclosures, investigate allegations or submit survivor records, passwords or images. Write your reasoning before checking feedback. You may pause or use an alternative fictional exercise; supervised skills review remains separate.",
        practice_safety_note="Use only the supplied non-graphic fictional scenario or aggregate exercise data. Do not collect real disclosures or submit survivor records, passwords or images. You may pause or use an alternative fictional exercise. Record reasoning before checking guide feedback.",outcome=outcome,modules=modules)
COURSES=[]
for filename in ["prevention.py","harmful_practices.py","digital_safety.py","ethical_data.py"]:
    spec=importlib.util.spec_from_file_location("gbv_completion_"+Path(filename).stem,Path(__file__).with_name(filename))
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    COURSES.append(source.course(c,m))
