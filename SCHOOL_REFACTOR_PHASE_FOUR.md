# Academy phase four: complete the FSW draft catalogue

Executed on 14 November 2026 under the owner's phased-execution instruction. This phase adds the five remaining proposed FSW foundation courses, aligned PDF/slide resources and a ten-course school-exam authoring map. It does not approve the curriculum or open school certification.

## Delivery

| New code | Draft course | Modules | Course MCQs | Media files |
| --- | --- | ---: | ---: | ---: |
| SWP-037 | Person in Environment and Human Development | 3 | 15 | 4 |
| SWP-038 | Communication Interviewing and Helping Relationships | 3 | 15 | 4 |
| SWP-039 | Professional Recording Consent and Confidentiality | 3 | 15 | 4 |
| SWP-040 | Referral Networks and Interprofessional Practice | 3 | 15 | 4 |
| SWP-041 | Reflective Practice Boundaries and Supervision | 3 | 15 | 4 |

Every course has original teaching, fictional cases, practice activities, feedback and a source appraisal. Each module has at least 250 teaching words and five teaching points mapped to five MCQs. Across the phase there are fifteen modules and seventy-five draft course questions. All stems were checked against the earlier thirty-question batch and against one another.

FSW now has its proposed ten-course catalogue: unchanged SWP-016/017/018 plus inactive drafts SWP-035 through SWP-041. The ten-course coverage map and evidence notes are in `production_courseware/phase_four/fsw_batch_02/README.md`. Selected IFSW/IASSW educational domains guide the map. These short courses do not establish degree equivalence, placement completion, professional registration or external accreditation. Depth, hours and practice relevance still require independent academic review.

The new source evidence includes recent open-access communication, documentation and reflective-practice reviews, an IJSDS Port Harcourt contextual study, the OpenStax developmental-context chapter, official education standards and the NDPC's 2025 directive. Evidence records distinguish qualitative/scoping/contextual findings from intervention effectiveness, journal metrics from article quality, and official Nigerian guidance from overseas professional benchmarks. BJSW rank 11/99 supports an explicitly labelled Q1-consistent inference rather than an independently checked JCR quartile. No quartile is claimed for IJSDS or for Journal of Social Work in this batch. Repository copies and private retrieval receipts record legitimate full-text access; unsuccessful candidates do not support teaching claims.

## Materials and QA

Each course has a six-page learner-guide PDF, three-page worksheet PDF, sixteen-slide editable PPTX and matching sixteen-page slide PDF. Twenty resources provide eighty editable slides and 125 final PDF pages. The learner package follows `production_courseware/FORMAT_STANDARD.md`: 12-point PDF body text, clear headings, course/version footers, navy/green/white styling, the established cover illustration and large editable slide text. Full teaching and evidence notes remain in guides and facilitator notes.

All final PDF pages were rendered and visually reviewed, including all eighty slide pages exported from the actual final PPTX through isolated LibreOffice. No clipping or overlap was found. All five decks passed package, geometry, font and Artifact Tool import checks. Native Microsoft PowerPoint was not used. Automated checks confirmed every guide teaching paragraph, case, activity and feedback, every module title, and every teaching point in both editable decks and slide PDFs. The upload manifest binds final bytes with SHA-256 hashes. These are production checks; independent academic, accessibility and learner-pilot approvals remain pending.

Media builders now accept a package and release path while retaining previous defaults. The deck builder uses each course's cover title and supports source-specific display titles, links and evidence-limit labels. Reference-slide counts derive from the actual source list. Previously staged phase-three source packages and media were not regenerated or changed.

## Mixed final school exam

The new blueprint identifies all ten courses, with four MCQ slots per course and written coverage for every course. Forty one-mark MCQs, six five-mark short answers and two fifteen-mark essays total 100 marks. All eight written items have original prompts, model marking guidance and criterion rubrics. The proposed threshold is 70 percent and the proposed duration is 180 minutes, subject to review and accessible piloting.

Forty school MCQ slots remain unbound; approved item selection and actual provider provisioning are outstanding. The seventy-five course MCQs are separate draft banks. The blueprint is an internal authoring contract, not a ParaLearn API payload. Its provider assessment ID remains null and provider support is unverified. Human marking and moderation are mandatory for written answers; AI alone cannot finalise a result. The earlier five-course proposal remains as a historical file with a different curriculum version. Tests confirm that an earlier-version result cannot satisfy the new contract. The offline contract cannot authorise certification.

## Platform execution and safeguards

Create-only course staging added five inactive courses and fifteen modules. Every pre-existing schools, courses, learning and credentials row passed a before/after fingerprint comparison. New course CBT IDs remain blank, and no course assessment was created externally. Existing CBT mappings, learner progress, attempts and credentials remain unchanged.

Private Storage staging checked the bucket's private status, uploaded twenty files, downloaded each to compare its hash and then registered the complete metadata batch in a short transaction. All assets entered `in_review`. All prior database rows again passed parity checks. The platform totals are 41 courses, including 34 retained active courses and seven inactive drafts, and 300 assets. The 25 coded schools remain closed to full-school enrolment.

Private audit receipts are in `production_courseware/private/phase-four/`: `fsw-courses.applied.json`, `fsw-resources.applied.json`, the upload journal and `post-upload-verification.json`. The latest verifier reads back remote files, compares the five staged courses and fifteen modules to the exact source, excludes only this phase's additions when comparing the original fingerprint, and checks the retained public catalogue and hidden drafts. Use this latest boundary rather than earlier verifiers that intentionally assert earlier course/asset totals. Credentials, signed URLs, learner information and operational snapshots are excluded from Git.

## Validation and delivery

The full Django suite passed **166 tests** in isolated in-memory SQLite with `DEBUG=True`. Tests never used the live database. New tests cover deterministic batch export, prior-bank duplicate checking, ten-course mixed-exam coverage, rejection of an earlier curriculum result and staging all five additions while preserving the previous FSW courses and their CBT IDs. The material manifest checks passed against the actual final files. Python syntax and Git whitespace checks also passed.

The twenty-file learner-media bundle is `../output/academy_phase_four/SWEEP_FSW_Phase_4_Review_Materials.zip`; all bundled resource hashes match the upload manifest. It contains a review notice and no course CBT keys or private exam marking guide. A legible one-page progress report to Prof. Mina is `../output/academy_phase_four/SWEEP_Phase_4_Report_Prof_Mina.pdf`.

This phase is committed and pushed to `origin/main` after verification, as requested. No runtime feature release is needed for these inactive additions and authoring tools. A Git push is not content approval or evidence of provider integration.

## Next phase

Continue the remaining 143 of 150 proposed new courses in bounded research and PDF/slide batches, while independent review of the seven FSW drafts proceeds. A next ERT foundation batch can add four researched courses to its one retained course, reaching a five-course draft breadth milestone before completing its target of eight and progressing across the other schools. Check scope, evidence, learning depth and the school curriculum map before each batch; do not treat a numerical minimum as sufficient educational coverage.

ParaLearn course provisioning and mixed-exam integration require verified deployed API capabilities and authorised non-placeholder credentials. Keep course badges tied to verified approved course CBT passes. School certificates require every approved curriculum course, a passed final school exam after human marking/moderation, and authorised Head of Learning and Founder signatures. The Head of Learning's name/signature is still to be supplied; Founder is Prof. Mina Ogbanga. Do not fabricate signatures. Actual videos, accessible captions and checked transcripts are later additions, preserving course identity and existing completion history.
