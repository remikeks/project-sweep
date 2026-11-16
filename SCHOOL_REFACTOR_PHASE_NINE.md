# Phase 9 MHP: verified private staging

16 November 2026. The ten-title MHP draft catalogue is complete: six unchanged original courses SWP-004–009 and four inactive additions SWP-057–060. This completes the authoring/private-staging phase, not academic approval, learner release or a live ParaLearn integration.

## Build and publishing provenance

The real cloud chat "MHP Phase Nine Continuation" built from dispatch checkpoint `8f7dee621f11ee098fb4c221d6116a2439aefdc5`; its source build was `5fc317c4a15f7b2be0a3964bd8e024a51050e447`. It lacked GitHub write and production credentials. The existing desktop publishing connection completed the authorised phase. Credentials, raw papers and operational receipts stayed local/private.

Reviewed source travelled through the first-party chat connector in two checksum-verified compressed text handoffs. The checkpoint teaching/package hashes and deterministic exam JSON matched. PDFs/PPTX were regenerated locally, not accepted on the cloud's binary hashes. Local adjustments make font paths portable, normalise Windows text newlines for Git comparisons, and gate the owner report on actual live proof. Cloud browser download stopped at human verification; no challenge was bypassed.

The completed build was first pushed to `codex/mhp-phase-nine-cloud`. The owner's subsequent instruction on 16 November 2026 to push all builds brings `main` forward to this verified Phase 9 build as well. Future completed, verified phases should reach `main` before development moves to another school. Preserve other remote work and never force-push. This supersedes the historical cloud-dispatch restriction that kept main at Phase 8.

## Verified work

- Four courses, twelve modules, sixty original MCQs checked against all 330 earlier stems. Canonical package digest `7f54a6fbb3501817671dbdb5e6451dd5cd87146fee6744330f235593308e887d`; evidence appraisal remains dated 15 November.
- Ten-course internal exam: forty unbound MCQ slots/four per course, six short answers collectively covering all ten, two integrative essays covering all ten, 100 marks. Retained catalogue outcomes/modules/CBT domains are mapped without changing them. Written marking, independent moderation and amendment/appeal history require humans. Proposed 210 minutes and 70% pass need approval/piloting. Provider assessment ID null/support unverified; perfect offline results cannot certify.
- Sixteen resources: four guides (8/7/7/7 pages), four three-page worksheets, four editable sixteen-slide Artifact Tool decks and matching actual LibreOffice slide PDFs. Guides use 12-point embedded Liberation Sans and the established design. All 105 PDF pages were rendered with Poppler and visually checked on 28 contact sheets, with full-page guide spot checks. Guides/worksheets were rechecked after embedded-font/reference-intro regeneration. No clipping/overlap observed; native PowerPoint and accessibility/specialist approval are not claimed. Local artifact create markers ran for PDF/PPTX authoring.
- 191 isolated tests passed locally in 247.343 seconds, fresh process `DATABASE_URL=sqlite:///:memory:`, `DEBUG=True`. Six new tests cover deterministic dated sources/330 stems, ten-course exam coverage, incomplete/unmarked/unmoderated results and certificate rejection, current/prior media identity, embedded fonts/safety notes, create-only staging preservation and replay rejection.
- All 623 protected checkpoint courseware files match Git; Windows text CRLF/LF differences are normalised on both sides, while binary resources are byte-identical. Actual-file teaching/text/hash verification, Python compilation and whitespace checks passed.
- LIVE create-only staging created four inactive courses and twelve modules, then sixteen private `in_review` assets. Before/after fingerprints preserve all existing schools, teaching/modules/assets, original CBT mappings, earlier drafts, learners and credentials. New course CBT IDs remain blank.
- LIVE verification passed sixteen private remote hashes and 33 public checks: catalogue, all 26 inactive-draft 404s, and six original MHP course 200s. Observed totals: **60 courses = 34 active originals + 26 inactive drafts; 376 assets; MHP ten courses/six active plus four inactive; all 25 coded schools closed**.

## Rebuild and verification

Read `CLOUD_CONTINUATION_PHASE_NINE.md` as the historical dispatch record. Use the source/media READMEs for evidence and boundaries. Original source appraisals retain rights, methods, metadata discrepancies and access limitations; no new full-text appraisal is inferred from cloud downloads.

Use the existing scripts with verified host-local runtime/font/LibreOffice/Poppler paths:

1. `scripts/build_mhp_ten_course_exam.py` reproduces exam digest `0b553f8b31620b184a0bf1d5c8e4a17e615376013923e9075e24a3c3508aa718` after text-newline normalisation.
2. `scripts/build_fsw_media_pdfs.py` accepts `--package`, `--release`, `--font-regular`, `--font-bold` and the MHP-specific `--reference-intro`. Guidance is a benchmark, not Nigerian legal authority or proof of service availability; the local survey is contextual research, not a regulatory standard.
3. `scripts/build_fsw_media_decks.mjs` uses the unchanged background and editable Artifact Tool exports. Its finalizer refuses overwrites: rebuild in a fresh release, inspect before replacing Phase 9 outputs.
4. `scripts/render_fsw_media.py`, `scripts/build_fsw_media_manifest.py` and `scripts/build_courseware_contact_sheets.py` render/verify actual final files. Refresh `visual_qa.json` only after actual visual inspection.
5. In a fresh PowerShell process set `$env:DATABASE_URL='sqlite:///:memory:'`, `$env:DEBUG='True'` before `.venv/Scripts/python.exe manage.py test --noinput`. Default `.env` points at LIVE Postgres; never use it for tests.
6. `scripts/verify_mhp_local_build.py` checks source/media/visual proof; `--completed-test-summary` can reuse an already observed successful isolated suite when no tested code changed. Local proof is distinct from live proof.
7. `scripts/build_phase_nine_report.py --font-regular PATH --font-bold PATH` requires both actual local and post-upload verification receipts. It produces a one-page 12-point owner report and a reopened/hash-checked seventeen-entry review ZIP: sixteen learner resources and README, no staff keys/rubrics/raw papers/private receipts.

## Private operational evidence and recovery

Ignored receipts at `production_courseware/private/phase-nine/`: courses.applied.json, resources.applied.json, upload intents/completion journal, isolated test summary, local-build-verification.json and post-upload-verification.json. Do not copy credentials, signed URLs, raw records or these operational files into Git/shared attachments. The verified-TLS persistent transport writes upload intent before PUT, checks uncertain outcomes by exact authorised read/hash, and registers metadata in a short transaction only after every upload verifies. No schema/auth/RLS changes were required.

This batch is applied. **Do not replay staging or uploads.** Any later read-only recheck must use existing receipts; the create-only verifier's proof file also refuses overwrite, so preserve historical proof and use an explicitly new audit destination for any future verification. Review outcome/journals before recovery; do not blindly retry uncertain writes.

## Remaining approvals and next build

Keep additions inactive/resources private and all coded schools closed to full-school enrolment/certification. Academic, clinical/child-safeguarding, Nigerian legal/practice, lived-experience, supervised-skills and accessibility/pilot reviews remain pending. Exercises use fictional cases/invented aggregates, never personal trauma histories, real child interviews or health records; an alternative fictional exercise is allowed. Introductory coursework grants no diagnosis, therapy, prescribing, crisis-triage, capacity or independent child/clinical authority.

Badges require approved courses and verified ParaLearn course-CBT passes. Certificates require every approved school course and a passed full-curriculum mixed ParaLearn exam after human written marking/moderation, plus approved signatories. Head of Learning name/signature pending; Founder, SWEEP Academy: Prof. Mina Ogbanga. No provider capability, signature or approval is fabricated.

Next school is **PCEI**, target eight: retain its three original courses, research five additions, create aligned guides/worksheets/editable slides/slide PDFs and a full-school mixed exam, verify preservation/private access and push the accurate build. Authored progress: **26/150 additions; 124 remain**. Actual videos with checked captions/transcripts follow later. Continue in the existing cloud chat from the pushed branch when the owner next instructs; no further chat/agent or new phase was started here.
