# Foundational Social Work PDF and slide review materials

This phase packages the two inactive teaching drafts, SWP-035 Social Work Values and Ethical Decision Making and SWP-036 Generalist Assessment and Case Management. It does not activate them or complete the wider 150-course expansion.

Each course contains a full learner-guide PDF, a three-page practice-worksheet PDF, a 16-slide editable PPTX and the matching 16-page slide PDF. All resources use version 0.1.0 and remain for academic review. There are no video placeholders, fabricated transcripts or assessment answer keys in these learner files.

The lessons, cases, activities and feedback come from the unchanged `phase_two/fsw_batch_01/review_package.json`. All 15 teaching points per course appear in its native editable slide text. Fuller teaching and source limitations are present in the guide and facilitator notes. Slides use the existing academy cover illustration and navy/green palette. PDF body text is 12 points.

## Review boundaries

The source appraisal and pending academic, Nigerian practice, accessibility and learner-pilot reviews from phase two still apply. PDF/slide production and structural checks do not constitute academic approval. The new course CBTs and mixed school exam remain to be configured and verified. School enrolment and certificates stay closed until the agreed readiness conditions are met.

## Reproduction

Use the bundled artifact Python and Node runtimes described in the project tooling. Run `scripts/build_fsw_media_pdfs.py` to create the guide and worksheet PDFs. Run `scripts/build_fsw_media_decks.mjs <new-output-directory>` to create the editable decks with Artifact Tool and its structural finalizer. Use a new build directory for revisions, then copy the validated final PPTX files unchanged into this package.

Run `scripts/render_fsw_media.py` with the isolated LibreOffice executable and bundled Poppler executable. LibreOffice exports matching slide PDFs from the final PPTX files; Poppler renders each final PDF page for inspection. The packaged Artifact Tool's local rendering path encountered a missing standard-font module, so final visual QA uses these independent rendered outputs rather than claiming that rendering succeeded through that path.

After final visual inspection, run `scripts/build_fsw_media_manifest.py`. It checks PDF text, module coverage, editable-slide teaching-point coverage, slide/page counts, file hashes and the four-resource package profile. It writes `upload_manifest.json` and `package_validation.json`.

For database/Storage staging, first run `manage.py stage_pdf_slide_resources --release production_courseware/phase_three/fsw_media_01 --manifest production_courseware/phase_three/fsw_media_01/upload_manifest.json`. The default is read-only. Authorised staging adds `--commit --receipt <new-private-receipt-path>`. Verification uses the same release and manifest with `--verify <applied-receipt-path>`.

The command uploads only into a verified private bucket and verifies the remote bytes. Metadata is registered in review only after every file succeeds. Any interrupted upload is journalled privately; no partial metadata batch is committed. A repeat operation refuses courses that already have assets, avoiding silent replacements. Further revisions need a separately reviewed version workflow.

## Future batches

Follow `production_courseware/FORMAT_STANDARD.md` for subsequent schools and courses. Add actual video resources later, with captions or checked transcripts, while preserving the curriculum and assessment lineage.
