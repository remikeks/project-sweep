# SWEEP Academy course material standard

Owner instruction recorded 14 November 2026: keep course formats aligned, use properly designed PDFs and slides while videos are being developed, and push after each completed phase.

## Required package for new course batches

Every new course uses the `pdf_slides` resource profile until video production is complete. The four course-level resources share the same course code, source version, language and review status.

| Resource | Delivery format | Purpose |
| --- | --- | --- |
| Learner guide | PDF | Full lessons, outcomes, cases, activities, feedback and evidence notes |
| Practice worksheet | PDF | Printable application tasks with space for learners' responses |
| Course slides | Editable PPTX | Concise teaching points, cases, feedback and facilitator notes |
| Course slides | PDF | Portable copy matching the final editable deck slide for slide |

Word documents may remain authoring sources. Learners receive PDF reading materials and slides. Course CBT answer keys, private assessment blueprints, credentials, signatures and internal validation logs never enter the learner resource package.

## Design and readability

Use the existing SWEEP Academy illustration on deck covers and the established navy, green and white palette. Preserve the proportions of existing artwork. Use a consistent 16:9 slide canvas, clear subject headings, aligned text and stable course/version footers. Keep teaching text editable. Each slide should have a clear teaching purpose rather than repeat the full guide as a dense paragraph.

PDF guides and worksheets use a 12-point body font, clear heading levels, generous margins and page numbers. Slides use large, readable teaching text, typically 20 to 23 points, with larger titles. Source labels and footers may be smaller. Revise layout or divide content before shrinking teaching text to fit.

Include the course code and resource version on each resource. State draft status visibly until approval. Keep case examples and assessment thresholds consistent across the guide, slides and platform. Show concise source citations on relevant reference slides, link the original source and retain fuller research limitations in the guide and facilitator notes.

## Build and verify

Build resources from the approved version of a single authored source. Check that every module and teaching point has a corresponding place in the guide and slides. Inspect every rendered PDF page and final slide for clipping, overlap, awkward page breaks, legibility and missing text. Confirm that final slide PDF pages match the editable deck in count, sequence and content. Record checksums after the final changes.

Register completed new packages with `stage_pdf_slide_resources`. It validates the `pdf_slides` profile, requires inactive draft courses, verifies the Storage bucket is private, uploads and downloads each file to check its hash, and then adds a complete batch of metadata in one short transaction. Resources enter `in_review`; this operation cannot approve or publish them. It preserves pre-existing course and learner records.

## Video addition

Videos are a later addition to the same curriculum and resource version lineage. Existing facilitator notes can support script development, but they are not recorded videos or verified transcripts. A completed video package must include the actual recording and accessible captions or a checked transcript. Record review, consent and rights where applicable. Add the verified video through the existing content workflow without changing course CBT mappings or learner completion history merely because a new media format exists.

## Phase delivery and Git

Each completed phase has a scope statement, reproducible source, reviewed learner files, tests appropriate to code changes and an execution receipt. Commit and push the phase to the existing repository after verification. Confirm the remote branch contains the commit. Private credentials, signed URLs, learner information and operational snapshots remain excluded from Git. A Git push is not evidence that content passed academic review or became learner-visible.

The legacy eight-asset package stays supported for existing releases. This new delivery profile does not remove or rewrite the original 34 courses, their course CBTs or their previously released resources.
