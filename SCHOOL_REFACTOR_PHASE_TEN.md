# Phase 10 PCEI - verified build and private staging

Verified locally on 19 November 2026: 198 isolated tests passed in 209.410 seconds; 645 protected courseware files preserved; all 128 final PDF pages visually reviewed. Live create-only staging and read-only verification passed: five inactive additions, 15 modules, 20 private in-review resources, 20 fresh remote hashes, retained-record parity and all 35 public checks. Observed totals are 65 courses (34 active originals and 31 inactive drafts), 396 assets, eight PCEI titles and 25 closed coded schools. `production_courseware/phase_ten/build_summary.json` contains a non-sensitive completion summary. Academic release remains pending.

## Scope

PCEI is the School of Community Development and Participatory Engagement, with a target of eight courses. Preserve SWP-013 Community Needs Assessment, SWP-014 Community Organizing & Coalition Building and SWP-015 Program Development & Evaluation, including teaching, outcomes, modules, assets and existing CBT mappings.

Add these five inactive academic review drafts, each with three modules and 15 original point-mapped MCQs:

| Code | Course |
| --- | --- |
| SWP-061 | Participatory Facilitation and Community Dialogue |
| SWP-062 | Asset Based Community Development |
| SWP-063 | Community Accountability and Grievance Mechanisms |
| SWP-064 | Inclusive Local Planning and Co Design |
| SWP-065 | Community Programme Implementation Practicum |

The source README maps retained domains to these additions. The internal eight-course final exam has 40 unbound MCQ slots, six short answers (30 marks) and two integrative essays (30 marks), totalling 100. Each course has five MCQ slots; written questions collectively cover all eight courses, and each essay integrates all eight. Actual original domains come from the retained catalogue. Duration 210 minutes, pass 70% and approximately 180 minutes of study per new course are proposals requiring academic and learner piloting.

Human criterion marks and rationales, independent moderation, rubric version, and amendment/appeal histories are required by the separate offline PCEI review contract. Provider assessment ID remains null and mixed-item support is unverified. A perfect offline result never authorises a certificate.

## Source provenance and review

The source checkpoint is published Phase 9 commit `3ea7bf212314148cd1c6ade754de177aca9a65e2`. Main was advanced through that build and the owner's publishing-policy commit `6ce75cf9b2afeb22264c163e6ff5438fb3051504` before completing this phase. Completed builds belong on main; preserve its policy and any newer remote work, and never force-push.

The existing cloud chat reported a frozen build at `bc98398ef243b2cabb523ada11d3ae8ab948f29c`, with 198 isolated tests passed. Its runtime later became unavailable. Text source was recovered through the first-party chat connection; no human-verification challenge was bypassed and no owner file upload is needed. A local re-audit found that 14 of 19 supplied file checksums match. The research file, two READMEs and final runbook/report packet do not match the supplied checksum strings. They must not be described as an authenticated byte-for-byte copy of the frozen archive. The research and README content was independently reviewed locally; this runbook and report builder are locally authored. Transport envelopes and comparisons remain ignored and private.

The locally recovered source before review corrections compiled to canonical package `85a91769efd74cdaa0f43975b29b4e6a5ea2c90325ce0a940bfa11024ef0be0c`. Local review corrected the R44 printed author byline to "Leton De-Great, Kasi Blessing" and replaced two backstage practicum paragraphs with learner reflection and implementation guidance. All 75 MCQs, options and rationales remain unchanged by those corrections. The reviewed package is `9fb5add7d7eb5b945232f8e7bbd34460cad3cd4c47c71914f1e5b25c90b5df1b`. Seven earlier packages and their 390 question stems are protected separately against the published checkpoint.

Research appraisal was performed on 16 November 2026; local wording/byline review occurred on 18 November and final layout/build verification on 19 November. Do not relabel the evidence as a fresh comprehensive appraisal on the report date. Per-source methods, dates, rights, context and limitations are in `research.py`. IACD 2018, OECD 2022 and World Bank ESS10 are practice comparators, not accreditation or universal Nigerian law. Recent studies have explicit transfer/causal limits. IJSDS surveys have possible dataset overlap and reporting inconsistencies; numerical causal effects are not taught. Registry bibliography S07/S04/R02 remains unresolved. No raw paper or protected source tool is redistributed.

## Materials and local verification

Twenty aligned resources comprise five learner-guide PDFs (7/7/6/7/8 pages), five three-page worksheet PDFs, five editable PPTX decks (15/16/15/16/16 slides) and matching PDFs converted from those actual decks with LibreOffice. All 128 final PDF pages, including all 78 slide pages, were inspected individually as Poppler PNGs on 19 November. No clipping or overlap was observed. Guide/worksheet body text is 12-point embedded Liberation Sans regular/bold. Hashes, accessible text, teaching-point coverage and fonts are independently checked. Native PowerPoint compatibility and expert accessibility/pilot approval remain pending. Videos have not been produced.

The full suite must pass locally using an explicitly isolated database, followed by the 645-file protected checkpoint comparison. The first local run reached all 198 tests but failed one inspection test because pdfplumber was absent; the dependency was then installed and pinned for CI. The successful local rerun passed all 198 tests in 209.410 seconds with the explicit in-memory database. All 645 checkpoint courseware files matched (text newline normalisation only; binary bytes identical). Migration drift check reported no changes. Detailed local proof remains ignored and private.

The desktop `.env` is LIVE Postgres. Never run tests with its defaults. In a fresh PowerShell process:

```powershell
$env:DATABASE_URL='sqlite:///:memory:'
$env:DEBUG='True'
.venv/Scripts/python.exe scripts/verify_pcei_local_build.py
```

The verifier runs the complete suite in a fresh child with explicit memory/debug environment. `--completed-test-summary PATH` may reuse only a genuinely observed successful isolated log for this exact unchanged build. Local proof requires actual final manifest hashes and a current visual review declaration; it never proves live staging or push.

Source reproduction uses `scripts/build_pcei_source.py`. Media reproduction uses `scripts/build_pcei_media.py` with explicit font, bundled runtime, Artifact Tool skill, LibreOffice and Poppler paths. Existing SWEEP builders/backgrounds remain unchanged. Use a fresh export or preserve only this phase's output before rebuilding, because the deck finalizer refuses overwrites. Revalidate and inspect every regenerated final page; binary hashes can differ across runtimes. The final local manifest is authoritative for staging. Required Python dependencies include project requirements plus ReportLab for authoring. Do not copy credentials to cloud.

## Private staging and publication

Before this phase the verified live baseline was 60 courses (34 active originals, 26 inactive drafts), 376 assets and 25 closed coded schools. The observed post-staging totals are 65 courses (34 active originals, 31 inactive drafts), 396 assets, eight PCEI courses (three originals/five drafts) and 25 closed schools. All new course CBT IDs remain blank. Existing teaching, modules, assets, original CBT mappings, earlier drafts, learners and credentials passed before/after fingerprint parity.

Use the existing authorised create-only `stage_authored_review` command with a new receipt path, followed by the phase-local persistent upload/reconciliation workflow. Uploads must verify private bucket status, TLS and all exact bytes before metadata registration; no blind replay or overwrite. All new courses stay inactive with blank CBT IDs; resources enter private `in_review` status. Existing school/course/module/asset/learner/credential fingerprints must match before and after. No schema, RLS, auth or original-course changes are part of this phase.

The final read-only live verification confirmed five source courses, 15 modules, 20 private resources, 20 fresh remote file hashes, retained-record parity, counts above and 35 public checks: catalogue 200, all 31 drafts 404 and the three original PCEI pages 200. Operational receipts stay under ignored `production_courseware/private/phase-ten/`. No learner records, tokens, signed URLs or staff assessment keys may be shared as handoff proof.

This batch is applied. Do not replay course staging or uploads. Preserve receipts and inspect actual outcomes before any recovery. Future read-only audits must preserve historical proof and use a new audit output path because the verifier refuses proof-file overwrites.

`scripts/pcei_build_proof.py` validates supplied proof; it performs no network checks itself. The owner report requires genuine local proof and an optional `--live-proof` export. Live exports need actual remote hash rows, all exact public path/status results, provenance and verification timestamp. Do not manufacture fields before checks occur. Staging proof never proves Git publication: independently fetch, commit and push main, then compare remote HEAD and confirm the worktree is clean.

`scripts/build_phase_ten_report.py` creates a one-page 12-point report and a reopened, hash-verified 21-entry review ZIP containing only the 20 learner resources and media README. Staff source, answer keys, exam rubrics, raw papers, QA images, operational receipts and secrets are excluded. The report remains explicit about outstanding academic release gates.

## Release gates and next phase

All new courses remain inactive and resources private/in review; school enrolment and certification remain closed. Academic, community/local-practice, safeguarding, accessibility/pilot and supervised-skills reviews are pending. Use fictional scenarios and invented aggregates, with an alternative fictional exercise; no personal histories, real complainant/child/survivor records or unsafe field recruitment. Grievance facilitation does not confer investigation/adjudication authority. The introductory practicum is simulated/supervised learning, not completed placement or independent professional competence.

Badges require approved courses and verified ParaLearn course passes. School certificates require all approved school courses, the final mixed exam, human written marking, independent moderation and authorised signatures from the Head of Learning and Founder Prof. Mina Ogbanga. Head of Learning details/signature remain pending.

Authored progress after PCEI: 31 of 150 planned additions; 119 remain. Next scope is CPS, retaining SWP-001-003 plus five additions toward eight courses. Finish this phase's verification and push before starting it.
