# Academy phase three PDF and slide materials

Executed on 14 November 2026 after the owner requested aligned PDFs and properly designed slides while videos are developed, with a push after each completed phase.

## Scope delivered

The two FSW draft courses now have eight completed review resources. SWP-035 has a six-page learner-guide PDF, three-page practice-worksheet PDF, 16-slide editable PPTX and matching 16-page slide PDF. SWP-036 has a seven-page learner-guide PDF, three-page practice-worksheet PDF, 16-slide editable PPTX and matching 16-page slide PDF. The course content source and resource version remain 0.1.0.

The slides use the existing SWEEP Academy illustration and navy/green styling. All 15 teaching points per course appear in editable slide text. The PDFs contain selectable text, a 12-point reading font, clear headings and page numbers. Fuller teaching, fictional cases, activities, feedback, references and evidence limitations remain available in the learner guides and facilitator notes. The slides contain concise teaching and practice prompts rather than the course CBT answer keys.

The 51 final PDF pages, including all 32 final slide pages, were visually reviewed. A crowded reference link was replaced with a short linked label, cover text was reflowed and PDF reference paragraphs were kept together. The final PPTX packages passed structural, slide-count, geometry, font and Artifact Tool import checks. LibreOffice exported the actual final decks to PDF and Poppler rendered the final pages for QA. Native Microsoft PowerPoint was not used for validation.

## Platform and Storage execution

The resource manifest validates a new `pdf_slides` profile: one learner-guide PDF, one worksheet PDF, one editable PPTX and one slide PDF per course. The legacy eight-asset release profile remains supported. `production_courseware/FORMAT_STANDARD.md` records this standard for future batches and the requirement to push after each verified phase.

The new `stage_pdf_slide_resources` command verified inactive course identities and a private Storage bucket, uploaded all eight resources and downloaded each object to verify its SHA-256 hash. Only after every file succeeded did it add all eight metadata records in a short transaction. Every resource is **in review** with no academic approval or publication recorded. The command refuses active courses, learner-enrolled drafts and existing asset packages, so it cannot silently rewrite released materials.

All pre-existing rows in the schools, courses, learning and credentials apps passed before/after fingerprint comparison. The original 272 course assets remain unchanged; the eight new review assets bring the total to 280. The academy still has 34 retained active courses and two inactive drafts. The new courses' CBT IDs remain blank. Existing CBT mappings, attempts, learner progress and credentials were preserved. The 25 coded schools remain closed to new full-school enrolment.

Private staging and verification receipts are in `production_courseware/private/phase-three/`. `fsw-resources.json` reserves the operation, `fsw-resources.uploads.jsonl` journals uploaded object paths and hashes, and `fsw-resources.applied.json` records new asset IDs and parity evidence. Signed URLs and service credentials are not stored in the receipts or committed to Git. Use the latest phase-three verifier for ongoing checks; phase two's pre-asset audit represents its earlier execution boundary.

## Validation

The full isolated Django suite passed all **163 tests**. The five focused resource-staging tests also passed after the private-bucket safeguard was added. The tests cover package completeness, altered files, active-course refusal, review-only staging, repeat refusal and an upload-verification failure that creates no metadata. Tests used an in-memory SQLite database, never the live database.

`scripts/build_fsw_media_manifest.py` checks actual PDF text and page counts, module coverage, editable teaching-point coverage, checksums and package completeness. The post-upload verifier checks persisted metadata and hashes, the original-record fingerprints, inactive draft state and the public catalogue. Its private result is `post-upload-verification.json`.

## Git and delivery

The previous phase-one and phase-two commits, `c8428db` and `d9eed84`, were pushed together to `origin/main` at the beginning of this phase. Phase three is a separate commit and push after verification. Private QA images, build candidates, credentials and operational receipts remain excluded. The eight final learner resources, manifest, source builders, package standard and code/tests are versioned in Git.

The downloadable review bundle is `../output/academy_phase_three/SWEEP_FSW_Phase_3_Review_Materials.zip`. It contains only the eight learner media files and a short review notice. All eight bundled file hashes were checked against the upload manifest.

## Remaining programme work

This media phase covers the first two newly authored courses. It does not complete the remaining course-development programme. Continue creating research-backed courses for the approved 25 schools, using the same material standard for each new batch.

Independent academic and Nigerian practice review, accessibility/pilot review, approved ParaLearn course assessments and verified mixed school exams remain release conditions. Actual videos, captions and checked transcripts are later additions; no video resource or fabricated transcript was created here. School certification stays closed until all curriculum courses, a finalised moderated ParaLearn school exam and authorised signatories are ready.
