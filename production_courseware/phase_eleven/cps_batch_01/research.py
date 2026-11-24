"""Appraised sources and limits; no raw papers or protected tools redistributed."""
CHECKED_ON = '2026-11-24'


def ref(code, author, year, title, url, use, appraisal, licence, **extra):
    return dict(id=code, author=author, year=year, title=title, url=url, kind='practice_guidance' if code.startswith('S') else 'peer_reviewed_research', use=use, appraisal=appraisal, licence=licence, checked_on=CHECKED_ON, **extra)


REFERENCES = [
    ref('S41', 'Keeping Children Safe', 2024, 'International Child Safeguarding Standards: How to implement them',
        'https://www.keepingchildrensafe.global/wp-content/uploads/2024/08/KCS-ICS-Standards-EN-2024.pdf',
        'Compare organisational responsibility, accessible reporting, safer operations and accountability; develop original fictional review questions.',
        'Actual official 48-page PDF downloaded and extracted. Selected purpose/definitions and Policy, People, Procedures and Accountability sections read, including pages 17-22, 28-33, 42-47. Practice standards are not experimental evidence, Nigerian law or accreditation. A policy or course completion does not establish implementation or staff suitability.',
        'No explicit open adaptation licence established from the inspected PDF. Link and original factual commentary only; no checklists, assessment webs, forms, photos, logos or wording reproduced.',
        slide_title='Organisational child safeguarding standards', slide_limit='2024 practice comparator; local implementation and qualified review required.', link_label='keepingchildrensafe.global Standards'),
    ref('S42', 'Alliance for Child Protection in Humanitarian Action', 2019, 'Summary: Minimum Standards for Child Protection in Humanitarian Action, 2019 edition',
        'https://alliancecpha.org/sites/default/files/technical/attachments/2019_cpms_summary_v2_final_en.pdf',
        'Compare participation, information management, coordination, separation prevention and cross-sector child protection.',
        'Official 28-page summary read selectively: principles/context, standards 1-6, 13-20 and cross-sector guidance. Suggested citation dates the summary 2020 while the standards edition is 2019; later hosting/training dates are not new editions. Case management is Standard 18 in the inspected 2019 summary. Contextualisation and competent staff remain essential; this is a summary, not the full operational handbook.',
        'No assumption of unrestricted adaptation. Original factual commentary and links only; no source forms, indicators, diagrams or exercises reproduced.',
        slide_title='Child protection in humanitarian action', slide_limit='2019 standards / 2020 summary; introductory comparator, not deployment authority.', link_label='alliancecpha.org CPMS summary'),
    ref('S43', 'Alliance for Child Protection in Humanitarian Action', 2024, 'Inter-agency Child Protection Case Management Guidelines, second edition',
        'https://alliancecpha.org/en/technical-materials/inter-agency-guidelines-case-management-and-child-protection',
        'Identify the updated case-management resource and the need for current contextualised procedures; not a substitute for reading and applying the operational guidance under supervision.',
        'Official landing page dated 3 December 2024 read; indexed publisher PDF excerpts confirm second edition and CC BY-SA 4.0. The 49.58 MB full PDF exceeded the web reader limit and direct local retrieval returned 403; no whole-PDF appraisal or archive is claimed. No operational case-management sequence or global forms are reproduced from unread sections. Core information principles are supported separately by the actually read CPMS summary.',
        'Publisher indexed PDF acknowledgement states CC BY-SA 4.0. No source tools or adapted manual content distributed; original factual resource commentary and links only.',
        slide_title='Updated inter-agency case-management guidance', slide_limit='2024 resource identified; full PDF unavailable in this appraisal.', link_label='alliancecpha.org Case management'),
    ref('R51', 'McCafferty P and Mercado Garcia E', 2024, 'Children’s Participation in Child Welfare: A Systematic Review of Systematic Reviews',
        'https://doi.org/10.1093/bjsw/bcad167',
        'Question whether a process hears children, supports relationships and responds to their views; do not infer causal protection effects.',
        'Actual 18-file-page publisher PDF in Queen’s University Belfast repository read selectively: methods, synthesis and limitations. Advance publication 8 July 2023, journal issue 2024. Fourteen databases, 674 hits and 14 included reviews; JBI appraisal. Peer-reviewed inclusion and no grey-literature search may introduce publication bias. Reviews may share primary studies, so they are not 14 independent intervention replications. Findings concern voice, relationships and context; no universal effect size or Nigerian legal procedure is established.',
        'CC BY 4.0 stated on repository cover and publisher PDF. Original factual teaching only; no instruments, tables or quotations copied.',
        doi='10.1093/bjsw/bcad167', quartile='SCImago primary 2025 Social Work table reports British Journal of Social Work Q1; checked 24 November 2026. Journal rank does not validate individual findings. No JCR claim.', slide_author='McCafferty and Mercado Garcia', slide_title='Participation: umbrella review', slide_limit='Review synthesis; voice, relationships and context, not causal effect proof.'),
    ref('R52', 'Backhaus S, Blackwell A and Gardner F', 2025, 'The effectiveness of parenting interventions in reducing violence against children in humanitarian settings in low- and middle-income countries: A systematic review and meta-analysis',
        'https://doi.org/10.1016/j.chiabu.2024.106850',
        'Distinguish promising parenting support from guaranteed effects; check humanitarian setting, delivery capacity and outcome-specific evidence.',
        'Actual 16-file-page final published PDF via University of Amsterdam read: methods, results and limitations. Online 16 June 2024; issue 162(2) dated 2025. Search updated August 2022; 23 trials, with differing trial counts by outcome. Robust variance estimation addressed multiple estimates. Effects heterogeneous; most settings protracted/post-crisis, most outcomes unblinded self-report, little long-term evidence and limited evidence for some violence outcomes. No pooled numerical effect is taught as a local prediction and no programme manual is reproduced.',
        'CC BY-NC-ND 4.0 stated in publisher PDF/repository. Link and original factual commentary only; no translated/adapted article, programme manual, figures, measures or paper redistributed.',
        doi='10.1016/j.chiabu.2024.106850', quartile='SCImago primary 2025 Social Work table reports Child Abuse and Neglect Q1; checked 24 November 2026. No article-validity or JCR inference.', slide_author='Backhaus and colleagues', slide_title='Parenting support in humanitarian settings', slide_limit='23-trial synthesis; heterogeneity and limited acute-crisis/long-term evidence.'),
    ref('R53', 'Bruehl A and colleagues', 2025, 'Spillover mechanisms linking intimate partner violence and child maltreatment: a cross-sectional and longitudinal study among Eastern European mothers',
        'https://doi.org/10.1186/s12889-025-24955-8',
        'Explain why contemporaneous associations do not establish a causal pathway or justify blaming caregivers; support coordinated qualified help.',
        'Actual publisher full HTML methods, results and limitations read. Published 4 November 2025; data March 2019-May 2020. Sample 701 mothers with children 2-9 years in an Eastern European parenting programme. Cross-sectional indirect associations did not replicate longitudinally; intervention exposure, selective attrition and pandemic timing complicate interpretation. Maternal reports and selected population limit transfer. No diagnostic, causal or inevitable intergenerational claim is taught.',
        'Open-access publisher full text; no instruments or participant material copied. Original factual commentary and link only; exact reuse licence is not needed to reproduce a source instrument because none is reproduced.',
        doi='10.1186/s12889-025-24955-8', quartile='SCImago primary 2025 record for BMC Public Health reports Q1 in Public Health, Environmental and Occupational Health; checked 24 November 2026. No JCR claim.', slide_author='Bruehl and colleagues', slide_title='Family violence: associations and limits', slide_limit='2019-20 selected sample; cross-sectional pathways did not replicate longitudinally.'),
    ref('R54', 'Sim A and colleagues', 2026, 'Effects of an integrated parenting and mental health intervention on violence reduction and caregiver mental health among migrant and displaced families from Myanmar: a pragmatic randomized controlled trial',
        'https://doi.org/10.1111/jcpp.70241',
        'Consider supervised, context-sensitive caregiver support and distinguish caregiver outcomes from child outcomes and implementation readiness.',
        'Actual open-access publisher HTML methods, outcome tables and limitations read. First published 17 September 2026. Thailand-Myanmar border study July 2024-August 2025; 480 baseline caregivers, 477 in analysis, children 4-15. Individual randomisation to integrated support or treatment as usual; follow-up to six months. Self-reported outcomes, unmasked participants, underrepresentation of men and one displacement setting limit generalisation. Reported caregiver/parenting improvements did not establish improvement in every child outcome; no significant child emotional/behavioural effect was found. No intervention sessions, measures or clinical techniques reproduced; no local effect prediction.',
        'Publisher marks article open access; exact Creative Commons variant not established from inspected HTML. Original factual commentary and link only; no article adaptation or programme content reproduced.',
        doi='10.1111/jcpp.70241', quartile='SCImago primary 2025 journal record 15402 reports Q1 in Pediatrics, Perinatology and Child Health; checked 24 November 2026. No JCR claim or article-validity inference.', slide_author='Sim and colleagues', slide_title='Integrated support in a displacement setting', slide_limit='2026 pragmatic trial; one setting, self-reported outcomes and bounded transfer.'),
]

SEARCH_NOTES = [
    'IJSDS homepage and published-articles page checked 24 November 2026. Search did not identify a sufficiently appraisable CPS-specific paper; article listing returned no readable text. No unrelated IJSDS study was forced into child-protection teaching. Homepage now states CC BY 4.0, but article-specific rights still require checking; no IJSDS Q1/Q2 claim.',
    'November 2026 participation scoping review DOI 10.1016/j.chiabu.2026.108258 identified as open access in publisher indexing; direct full-text access returned 403. Logged as a current research lead, not a fully appraised teaching source.',
    'WHO parenting guideline identified as 2022 copyright / later dissemination. Full WHO PDF returned 403 and NCBI reader showed a browser check. No bypass and no whole-source appraisal claimed; not used to reproduce protocols.',
    'Lin et al. 2025 DOI 10.1186/s12889-025-23527-0 publisher full HTML inspected. Cross-sectional MICS data 2017-20, with 34-country/32-country reporting inconsistency. No causal or prevalence claims used; not needed for the selected course evidence map.',
]

METRIC_SOURCES = ['https://www.scimagojr.com/journalrank.php?category=3323', 'https://www.scimagojr.com/journalsearch.php?clean=0&q=19621&tip=sid', 'https://www.scimagojr.com/journalsearch.php?clean=0&q=15402&tip=sid']
