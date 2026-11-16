> Historical dispatch checkpoint. Phase 9 completion and verified private staging are recorded in SCHOOL_REFACTOR_PHASE_NINE.md.

# SWEEP Academy Phase 9 cloud continuation

Handoff prepared 16 November 2026 at the owner's request to continue through Codex Cloud from a phone. This checkpoint preserves unfinished MHP authoring; it is **not** a completed phase or a learner release. No Phase 9 production courses, modules, resources, exams or credentials have been created yet.

## Owner's authorised scope

Replace the old organisation with the 25 coded schools (already completed), retain and realign all original courses/CBTs, then develop research-backed additions to each school's approved 5–10-course target. Continue in phases and push each accurate verified build. Provide legible, consistently designed learner-guide PDFs, worksheets, editable slides and matching slide PDFs until actual video production follows. Course completion badges require an approved course and verified ParaLearn course-CBT pass. School certificates require every approved school course and a passed final ParaLearn exam testing all courses with MCQs, short answers and essays. Written answers require human marking and moderation. Head of Learning name/signature are pending; Founder, SWEEP Academy: Prof. Mina Ogbanga. Never fabricate signatures, academic approval, a provider assessment ID or live ParaLearn mixed-item capability.

Keep full-school enrolment/certification closed until curriculum, provider, marking, pilot/accessibility and signatory requirements are ready. New content remains inactive and resources private/in review. Preserve all original teaching, CBT IDs, learners, credentials, prior drafts/modules/assets. No emails or other messages to third parties are authorised. This is one cloud continuation, not permission to spawn additional agents or unrelated chats.

## Repository and completed baseline

- Repository: https://github.com/remikeks/project-sweep.git ; default branch `main`.
- Last completed/pushed build: `037abd7211b69c191c5aa68b1b7dc2329b40432a` (Phase 8). Read `SCHOOL_REFACTOR_PHASE_EIGHT.md` for workflow and baseline.
- Baseline verified live counts: 56 courses = 34 active originals + 22 inactive authored drafts; 360 assets; all 25 coded schools closed. FSW draft catalogue 10, ERT 8, GBV 8. Last isolated full suite: 185 passing tests.
- The current cloud checkpoint adds only source drafts, their compiled review package/validation, research-fetch code, an ignore rule and this handoff. No completed-build status is implied.
- Local `.env` points at LIVE Postgres. Do not run tests using the default database. Use a fresh process with `DATABASE_URL=sqlite:///:memory:` and `DEBUG=True`. In a Linux shell: `DATABASE_URL='sqlite:///:memory:' DEBUG=True python manage.py test --noinput` using the task's configured Python/venv. Never print secrets.

Use the exact checkpoint revision supplied in the cloud task prompt. Verify remote branch and HEAD, inspect existing edits, preserve them. This local desktop chat will not keep editing the phase after cloud dispatch. Do not force-push or overwrite unrelated work.

## Phase 9: MHP target ten

Retain these six original courses, modules, content, assets and CBT mappings unchanged:

| Code | Original title |
| --- | --- |
| SWP-004 | Biopsychosocial Assessment |
| SWP-005 | Cognitive Behavioral Therapy Foundations |
| SWP-006 | Crisis Stabilization & Safety Planning |
| SWP-007 | Screening & Brief Intervention (SBIRT) |
| SWP-008 | Motivational Interviewing |
| SWP-009 | Recovery-Oriented Systems of Care |

Their original catalogue/modules/outcomes/CBT domains are in `production_courseware/release-2026-10-03/course_catalogue.json`. Read these actual entries before mapping the full-school exam. Do not rewrite their clinical or addiction content or treat a school exam as permission to practise clinically.

Four original extension sources are already authored under `production_courseware/phase_nine/mhp_batch_01/`:

| Code | Title | Source |
| --- | --- | --- |
| SWP-057 | Trauma Informed and Culturally Responsive Psychosocial Care | `cultural_care.py` |
| SWP-058 | Community Mental Health Rights and Recovery | `rights_recovery.py` |
| SWP-059 | Child Adolescent and Family Psychosocial Support | `child_family.py` |
| SWP-060 | Mental Health Service Coordination and Safe Referral | `coordination.py` |

`authoring.py` supplies the school-specific helper, ten appraised references, evidence date and pending specialist/lived-experience reviews. `review_package.json` was compiled successfully: four courses, twelve modules, sixty original MCQs, each tied to a teaching point; checked against all 330 prior stems. Current package digest is in `validation.json`. This is structural source validation only. No Phase 9 full suite, designed media, full-school exam, live staging or access verification has yet run.

Each module has at least 250 teaching words, an outcome, original non-graphic fictional case, activity, feedback and matching reference IDs. Proposed study time is 180 minutes per addition, subject to piloting. Exercises prohibit personal trauma histories, real child interviews and health records; learners may pause/use an alternative fictional exercise. Diagnosis, therapy, prescribing, crisis-triage authority, legal capacity and independent child/clinical practice are outside the new introductory scope.

## Research already appraised

Evidence was checked 15 November 2026. Preserve that actual date unless independently updating the review; report/handoff date is 16 November. Full source methods/rights/access caveats are in `authoring.py`, copied deterministically into the review package. Do not erase qualifications to make a stronger claim.

- S1: retained IFSW ethical principles.
- S21: WHO community mental-health guidance 2021; actual official PDF 296 file pages. Selected rights, supported-decision, inclusion and action sections read, not every case. International benchmark, not local legal compliance or service availability.
- S22: WHO mental-health policy guidance 2025, **Module 1 only**, actual 44-page PDF. Selected introduction/reform/lived-experience/social-determinant sections; not all five modules.
- S23: WHO/UNICEF child/youth service guidance 2024; actual linked PDF **112 file pages** versus publication-page metadata 122. Selected rights, participation, family/community and integrated/transition sections. Discrepancy retained.
- R29: MacRae et al., online 22 May 2026, DOI `10.1177/15248380261451829`; conceptual integrative trauma-informed framework review, search December 2024, rapid single-reviewer stages with subset checks. Not a treatment-effect review. CC BY-NC 4.0; link/original factual commentary only.
- R30: **Croke** et al., February 2026, DOI `10.1136/bmjment-2025-302275`; actual eight-page BMJ publisher PDF, 29 digital outpatient peer-support studies, search January 2025. Varied bias, sparse long-term/safety evidence. Main text says five databases but names four; language-search/exclusion wording also differs. No numerical effect, universal safety or engagement claim taught. CC BY 4.0.
- R31: Desatnik et al., 18 March 2026, DOI `10.1007/s10826-026-03286-1`; narrative systematic review of voluntary adolescent-parent programmes with face-to-face components, 24 publications/20 interventions, search December 2023. Retrospective registration, mostly single screening, heterogeneous measures/no meta-analysis. Not all children, compulsory safeguarding or digital-only delivery. CC BY 4.0.
- R32: Isaacs and Duncan, 18 August 2025, DOI `10.1186/s13033-025-00679-5`; adult coordination scoping map, 18 papers mostly US/Australia, terminology/population exclusions. Search end date not established from inspected main methods. Not a proven universal model or clinical role rule. CC BY-NC-ND 4.0; link/original factual commentary only.
- R34: Linton, Oduola and Teague, **28 July 2026** (not the date of a related suggested article), DOI `10.1007/s10597-026-01676-9`; 20-study Western qualitative recovery synthesis, updated search November 2025. UK-informed illness definitions, limited within-group/lifespan resolution; July 31 caption correction. No Nigerian cultural rule, family/faith mandate or causal treatment effect. CC BY 4.0.
- R35: Ejekaru and Adebusuyi, IJSDS 2025, DOI `10.67007/ijsds-2025-0200036`; actual 19-file-page linked PDF includes issue front matter. Single-hospital purposive provider survey (41), not representative service-user outcomes. Methods/abstract/results and regression-table arithmetic/df reporting are inconsistent. Numerical results are not taught or treated as causal; independent methods review needed. Bounded Nigerian contextual questions only. **PDF says all rights reserved; no Crossref licence**, so source PDF/text/tables/data are not redistributed or adapted.

Raw downloads, Crossref metadata and retrieval receipts remain on the local machine under ignored `production_courseware/private/phase-nine/research/`; they are not transferred through Git. `scripts/fetch_mhp_research.py` can retrieve sources afresh into the cloud's private folder, preserving existing receipts. WHO official API PDF downloads and BMJ/IJSDS PDF downloads succeeded. Sage direct retrieval was restricted; Springer returned challenge pages. Publisher-indexed primary methods/limitations were read through web tools; no archived full text claimed for those papers, no access restrictions bypassed.

Q1/Q2 claims use SCImago's own indexed 2025 records: Trauma Violence and Abuse Q1 / Journal of Child and Family Studies Q2. Direct tables restricted; no independent JCR table. BMJ publisher metrics confirmed but no primary quartile table obtained, so no BMJ quartile asserted. No IJSDS or other unverified quartile claimed. Rank is not article validity. WHO sources are CC BY-NC-SA 3.0 IGO; only links and original factual commentary are used, with no copied/adapted framework/tool/exercise/logo. Do not bundle raw source PDFs.

## Complete the phase in cloud

1. Inspect the checkpoint and instructions. Verify the source compiler still matches the committed package. The compiler command uses all six prior packages: `phase_two/fsw_batch_01`, `phase_four/fsw_batch_02`, `phase_five/ert_batch_01`, `phase_six/ert_batch_02`, `phase_seven/gbv_batch_01`, `phase_eight/gbv_batch_02`. Each path is under `production_courseware/` and ends with `/review_package.json`.
2. Build a **new ten-course MHP internal exam blueprint**. Use `scripts/build_fsw_ten_course_exam.py`, `scripts/build_gbv_eight_course_exam.py` and `schools/exam_blueprints.py` as patterns/contracts. Required courses: 004–009 plus 057–060. Forty unbound MCQ slots/four per course; six short answers and two integrative essays, 100 marks. Written questions collectively cover all ten, with marking guidance, weighted rubrics, human marking/moderation/appeal history and no AI-only finalisation. Suggested short-answer pairs: 004+005, 006+007, 008+009, 057+058, 059, 060. Review original course domains; avoid newly invented treatment or triage protocols. All IDs remain unbound/provider assessment null/support unverified; proposed duration/pass mark need review/pilot. `draft_catalogue_complete=True` is distinct from approved curriculum; `curriculum_complete=False`, certificate authority false. A perfect offline result must not certify.
3. Create aligned sixteen media resources at `production_courseware/phase_nine/mhp_media_01/`: four guides, four three-page worksheets, four editable PPTX and matching slide PDFs. Use applicable PDF/Presentations skills and bundled workspace dependencies discovered **on the cloud host**, not Windows paths from local history. Run required artifact create markers before first media authoring. Reuse `scripts/build_fsw_media_pdfs.py`, `scripts/build_fsw_media_decks.mjs`, actual school labels and `static/img/courseware-deck-background.png`. Use Artifact Tool editable exports, not python-pptx. File workflow is established because the earlier live presentation service lacked MXC. Guides 12-point body, established navy/green/white style, no shrinking for long titles. Current source uses five/six references per course, expected sixteen slides each; verify actual outputs rather than assume counts.
4. Render **actual final PPTX** via isolated LibreOffice to matching PDF, then all PDFs via Poppler. Adapt `scripts/render_fsw_media.py` paths to the cloud host. Run `scripts/build_fsw_media_manifest.py` against package/release and `scripts/build_courseware_contact_sheets.py`. Visually inspect every final guide/worksheet/slide page plus full-page spot checks; fix clipping/overlap and reverify. Exclude answer keys/staff exam rubrics from learner media and review ZIP; no simulated video labelled actual video.
5. Add meaningful Phase 9 tests for deterministic source/330 prior stems, ten-course exam and course/written coverage, missing completion/marking/moderation and certificate rejection, actual/prior media identity/hashes and additive preservation of all six original MHP CBTs/previous drafts/other schools. Full isolated suite with in-memory SQLite. Do not use `.env` live DB for tests. Compile/whitespace checks.
6. Prepare a Phase 9 runbook/source/media READMEs, honest pending approvals and clear next-build plan. Stage only after tests and actual-media QA pass, using existing create-only commands, new **private** receipts and authorised connections. Never copy local `.env`, service-role keys, private operational records or signed URLs into Git, chat, shared attachments or the task prompt. If cloud lacks production/Git credentials, use configured connections/vault/settings; finish independent work and clearly identify the exact access needed. Do not claim live staging/push succeeded without proof.
7. Expected successful Phase 9 counts: **60 total courses, 34 active originals, 26 inactive drafts, 376 assets; MHP ten courses/six original active plus four inactive; all 25 coded schools closed**. Programme additions authored after completed phase: 26/150, 124 remain. Final generic verifier: `scripts/verify_authored_media_phase.py --package production_courseware/phase_nine/mhp_batch_01/review_package.json --release production_courseware/phase_nine/mhp_media_01 --private production_courseware/private/phase-nine --school MHP --expected-total 60 --expected-active 34 --expected-assets 376 --expected-school-count 10 --expected-target 10`. It should verify sixteen remote hashes, retained pre-phase fingerprints and **33 public checks** (catalogue + 26 draft 404s + six retained MHP course 200s). Derive/review actual results, never fabricate a proof receipt.
8. Resource staging uses private-bucket checks, signed upload/download hashes and a short metadata transaction. Local Phase 8's ignored persistent-HTTPS helper is not in Git; use existing commands first. If transport fails, preserve reservations/intents/completion journals, inspect outcome, and never blindly repeat an uncertain PUT or replay an applied create-only batch. Keep TLS verification enabled. Read relevant Supabase skills/current docs before storage/DB work. No schema/auth/RLS change is required.
9. Produce a legible one-page report to Prof. Mina and verified key-free seventeen-entry review ZIP after actual proof, using `scripts/build_phase_eight_report.py` as pattern and actual test/page counts/date. Render/inspect the report and reopen/hash-check ZIP. Deliver through the cloud's supported file paths/download links, not inaccessible local Windows paths. Push each completed verified build as authorised; preserve other remote changes and do not force-push. Confirm remote HEAD and clean worktree. This checkpoint branch may be used for continuation; do not label it a finished phase before required checks.

Next school after MHP is PCEI (target eight, three original courses). Do not skip unfinished MHP requirements merely because the owner said next phase. Finish this active phase first, then follow the owner's further steering in the cloud chat. Do not run parallel local/cloud production mutations.
