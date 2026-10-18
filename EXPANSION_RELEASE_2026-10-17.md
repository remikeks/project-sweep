# Curriculum expansion revision — 2026-10-17

> Status update: the assessment import and publication gates below were completed
> on 2026-10-18. The original dated receipt is retained as history. See
> `EXPANSION_RELEASE_2026-10-19.md` for the current release and CI limitation.

## Completed and verified

- Four version 1.1.0 packages: Digital Social Work Practice; Climate Justice and
  Resilient Communities; Leadership Supervision and Programme Management;
  Participatory Research and Practice Innovation.
- Twelve developed lessons with worked examples, activities, feedback and all
  60 assessment decision points. Research provenance and claim limits are recorded
  in `production_courseware/expansion_review/teaching_source.json`.
- Thirty-two files: 20 DOCX, eight PDF and four PPTX. Visual review covered all
  56 Word pages, 32 PDF pages and 35 slides. Word title borders were corrected.
- Combined baseline/revised-candidate audit: 10 schools, 34 courses, 102 modules,
  272 resources; every local file checksum verified, no duplicate identities or
  identical file checksums. This is not a claim of no semantic overlap.
- Full Django test suite: 105 tests passed, including nine migration tests
  covering guards, rollback, interrupted upload recovery and repeat-run safety.
- Production revision completed: 32 existing asset records and 12 existing
  module records updated. All uploaded bytes were downloaded and checksum-checked
  before the database transaction. No new catalogue rows or learner changes.
- Repeat production execution returned unchanged, with no uploads or new rows.
- Read-only PostgreSQL verification: ten schools, 30 active courses, four inactive
  courses, 102 modules, 240 published version 1.0.0 resources and 32 in-review
  version 1.1.0 resources.
- Foundation Orientation has three optional non-credit lessons and reflection
  activities. Its local browser preview rendered the text and thumbnail correctly.
  It creates no enrolment, completion or credential.

## Rollback and duplication controls

The private migration journal is
`production_courseware/private/expansion-2026-10-17.json`, excluded from Git and
Vercel uploads. It retains the original row snapshots and old object paths.
The 32 old objects were deliberately retained, not imported as additional asset
records. Do not delete them or rerun the original four package imports.

The replacement import source is exclusively
`production_courseware/drafts/expansion-evidence-2026-10-17/upload_manifest.json`,
SHA-256 `ec850f7d192dbb50f9f57fda54a922647e8c0b48932784eb5fd84b1239c72f45`.
The original 240-file release remains unchanged. Historical Render learner
records and duplicate local media remain excluded.

## Still required before the four courses go live

1. Sign into the SWEEP ParaLearn examiner account.
2. Import/verify the four 15-question banks, answer keys and settings; record
   genuine assessment IDs and test learner access and result delivery.
3. Reconcile the production candidate, publish its 32 resources and activate
   the four courses together only after those assessment checks pass.

Owner authorization to generate and deploy is recorded in
`CURRICULUM_GOVERNANCE.md`. No independent subject-matter review or professional
accreditation is claimed. Further research enrichment of the original 30 courses
has not started; it follows completion of these release phases.

## Deployment receipt

Production deployment `dpl_3BtHx1yALydx9SaTFPHthKMhPWBP` was confirmed **Ready**
on 2026-10-17. Deployed application commit: `7a3671c` (including curriculum
implementation `0ddd087`).

- Deployment: https://sweep-academy-ovo2zqnqu-evanders-projects-83d1e543.vercel.app
- Production alias: https://sweepacademy.org
- Browser verification: https://sweepacademy.org/orientation/ displayed all three
  completed lessons, reflection activities, scope limits and ethical reference.
- Git copies of the manifest, teaching source and assessment source were
  checked against the review receipt: all three SHA-256 checks passed.

This confirms application deployment and staged content migration, not activation
of the four courses. The ParaLearn sign-in dependency above remains unresolved.
