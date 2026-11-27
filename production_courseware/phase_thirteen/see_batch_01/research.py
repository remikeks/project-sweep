"""Primary evidence inspected 27 November 2026; no source tools reproduced."""
CHECKED_ON = '2026-11-27'


def ref(code, author, year, title, url, use, appraisal, rights, short, limit, **extra):
    return dict(id=code, author=author, year=year, title=title, url=url,
        kind='practice_guidance' if code.startswith('S') else 'peer_reviewed_research', use=use,
        appraisal=appraisal, licence=rights, checked_on=CHECKED_ON, slide_title=short,
        slide_limit=limit, **extra)


ORIGINAL = 'Links and original factual commentary only; no source instrument, questionnaire, framework graphic, table, template or raw paper redistributed or adapted.'
REFERENCES = [
    ref('S61', 'U.S. Small Business Administration', 'accessed 2026', 'Plan your business: market research, planning, startup costs and break-even',
        'https://www.sba.gov/counseling/plan-your-business/', 'Support elementary market, cost and financial-planning questions using original invented numbers.',
        'Actual current official HTML sections read. Earlier market-research and startup-cost URLs redirect to this combined page. General enterprise guidance, not Nigerian tax, credit, registration or financial advice; forecasts are assumptions, not evidence of future sales.',
        ORIGINAL, 'Enterprise planning: market and cost questions', 'US guidance; invented arithmetic, no local tax or credit rule.', link_label='sba.gov Plan your business'),
    ref('S62', 'European Commission Joint Research Centre', 2016, 'EntreComp: competence areas and learning progress',
        'https://joint-research-centre.ec.europa.eu/scientific-activities/key-competences-lifelong-learning/entrecomp-entrepreneurship-competence-framework/competence-areas-and-learning-progress_en',
        'Compare foundation-level opportunity, resources and action domains; value may be social as well as financial.',
        'Actual official competence/progression HTML read; original framework is 2016, while a current download listing carries an August 2026 date. Foundation learning involves external support; a short course does not establish expert autonomy or degree equivalence.',
        ORIGINAL, 'Entrepreneurship: opportunity resources action', '2016 framework; current webpage is not a new framework edition.', link_label='ec.europa.eu EntreComp'),
    ref('S63', 'International Cooperative Alliance', 1995, 'Cooperative identity, values and principles',
        'https://www.ica.coop/en/cooperatives/cooperative-identity', 'Examine voluntary membership, democratic control and the relationship between external capital and member autonomy.',
        'Actual official identity page read, including the 1995 statement and its description of guidance notes. Current consultation pages discuss possible revisions; a discussion draft is not treated as an adopted replacement. Identity principles do not establish Nigerian registration, deposit-taking permission or investment protection.',
        ORIGINAL, 'Cooperative identity and member control', '1995 statement on current official page; not local registration law.', link_label='ica.coop Cooperative identity'),
    ref('S64', 'OECD and European Union', 2024, 'Measure, Manage and Maximise Your Impact: A Guide for the Social Economy',
        'https://www.oecd.org/en/publications/measure-manage-and-maximise-your-impact_2238c1f1-en.html',
        'Use proportionate evidence, stakeholder relevance and learning rather than equating a metric with impact.',
        'Actual official abstract/executive-summary HTML and full-report contents inspected. Published 15 April 2024; 114-page guide not read in full. Practice guidance and consultation-based principles are not a controlled effectiveness evaluation or proof that one indicator set suits every enterprise.',
        'OECD rights apply. ' + ORIGINAL, 'Impact evidence for mission and learning', '2024 guidance; proportionate evidence, not automatic causal proof.', doi='10.1787/2238c1f1-en', link_label='doi.org/10.1787/2238c1f1-en'),
    ref('R71', 'Eckerle C and Terzidis O', 2025, 'From ambition to evidence: a practical tool for startup impact assessment',
        'https://doi.org/10.1007/s11187-025-01101-7', 'Distinguish a useful planning tool and output proxy from measured beneficiary change.',
        'Actual publisher HTML design cycles, limitations and rights read. Online 4 August 2025; issue January 2026. Design-science interviews and few user tests in artificial settings, not a trial of social outcomes. Methods and later summary give differing interview/startup counts; no exact count is relied on. Revenue-linked tool requires an operating revenue history; it is not validated for every pre-revenue venture.',
        'Publisher states CC BY 4.0. ' + ORIGINAL, 'Startup assessment: design and proxy limits', '2025 online / 2026 issue; artificial tests do not prove social outcomes.', slide_author='Eckerle and Terzidis', doi='10.1007/s11187-025-01101-7', quartile='SCImago primary 2025 Small Business Economics record: Q1 Economics and Econometrics. Checked 27 November 2026; no JCR or article-validity claim.'),
    ref('R72', 'Fathi LI and colleagues', 2025, 'Mission and money: a scoping review of social enterprise business models as a solution to sustaining health-promoting food and nutrition-based initiatives',
        'https://doi.org/10.1186/s12889-025-24891-7', 'Question how income arrangements, operating conditions and mission interact without guaranteeing longevity.',
        'Actual publisher HTML methods, results, limitations and rights inspected. Published 31 October 2025; search November 2023 and web checks July 2024. Narrative synthesis of heterogeneous mostly case-based reports, no formal quality appraisal. Counts of studies, enterprises and verified operating status do not reconcile simply; no survival rate or comparative model superiority is inferred. Sector and publication-selection limits prevent a universal business prescription.',
        'Publisher states CC BY 4.0. ' + ORIGINAL, 'Mission and money: a sector scoping review', '2023 search / 2024 checks; case-rich synthesis, no guaranteed survival.', slide_author='Fathi and colleagues', doi='10.1186/s12889-025-24891-7', quartile='SCImago primary 2025 BMC Public Health record: Q1 Public Health, Environmental and Occupational Health. Checked 27 November 2026; no JCR or individual-study validation claim.'),
    ref('R73', 'Crnigoj M and Slavec Gomezel A', 2026, 'Organisational and Entrepreneurial Drivers of Social Impact Measurement Adoption in Social Enterprises',
        'https://doi.org/10.1080/19420676.2026.2669929', 'Examine financing and learning incentives while separating measurement adoption from actual impact.',
        'Publisher-indexed methods, results and rights read; direct reader returned 403. Online 13 May 2026. Slovenian December 2021 survey: 61 responses from 269 registered organisations, linked 2018-21 accounts; logistic models of measurement adoption. Non-response, small contextual sample and observational design limit causal transfer. Measuring more does not establish delivering more impact; reported associations are not financing recommendations.',
        'Publisher indexed PDF states CC BY-NC-ND 4.0. No article or adapted tool used; factual commentary and links only. ' + ORIGINAL,
        'Measurement adoption: observational evidence', '2026 paper / 2021 survey; adoption is not effectiveness.', slide_author='Crnigoj and Slavec Gomezel', doi='10.1080/19420676.2026.2669929', quartile='Official publisher metrics report 2025 SJR best quartile Q1 for Journal of Social Entrepreneurship; checked 27 November 2026. Best quartile is not every category or a JCR claim.'),
    ref('R74', 'Wang R', 2025, 'Building Cross-Sector Collaboration and Managing Institutional Tensions in Social Enterprise Organizations',
        'https://doi.org/10.1007/s11266-025-00744-0', 'Ask how partnership roles and mission tensions interact in an invented enterprise.',
        'Actual publisher HTML abstract, analytical discussion and limitations inspected; no claim of complete interview-protocol appraisal. Online 30 May 2025. Interviews with 15 enterprises in one southeastern US state: qualitative contextual accounts, not a representative national estimate or causal test of partnership success. Collaboration can introduce dependencies as well as resources.',
        'Publisher states CC BY 4.0. ' + ORIGINAL, 'Partnerships and competing enterprise goals', 'Fifteen US enterprises; qualitative context, no universal effect.', slide_author='Wang', doi='10.1007/s11266-025-00744-0'),
]
SEARCH_NOTES = [
    'IJSDS homepage and targeted entrepreneurship/cooperative queries checked 27 November 2026. No sufficiently appraisable SEE-specific full paper identified in returned results; no unrelated paper forced into teaching and no IJSDS quartile claimed.',
    'Current 2026 mission-drift supporting tables identified on Mendeley, but a dataset is not an independently appraised review article or a validated diagnostic instrument; not adopted as an assessment tool.',
    'The 2026 staged-impact-assessment paper DOI 10.1080/19420676.2026.2720900 identified as a lead; not needed for teaching claims without fuller appraisal.',
    'No source questionnaire, financial calculator, canvas, scoring instrument or research figure reproduced. Original cases and arithmetic only. No browser challenge bypassed.',
]
METRIC_SOURCES = ['https://www.scimagojr.com/journalsearch.php?q=29104&tip=sid', 'https://www.scimagojr.com/journalsearch.php?clean=0&q=19621&tip=sid', 'https://www.tandfonline.com/action/journalInformation?journalCode=rjse20']
