# Owner-approved course material release - LIVE 19 November 2026

Completed and verified on 19 November 2026: 65 active courses, 396 published resources, all 124 newly released file hashes, 66 public pages and 124 unauthenticated download guards passed. The full 206-test isolated suite passed. Vercel production deployment `dpl_3p773gEKQw9FVHP91HHccfdn4vSV` is READY and serves sweepacademy.org and www.sweepacademy.org from source commit `ddb22009a321f7b75cb481eed9e18216f0348fbb`. Protected teaching/CBT/school/learner/credential fingerprints match. The non-sensitive verification summary is committed beside the approval record.

The owner explicitly approved all existing course materials for live release on 19 November 2026. This supersedes the material-publication hold recorded in the earlier phase reports. The exact instruction and interpretation are recorded in `production_courseware/releases/2026-11-19/owner_approval.json`.

Scope: activate the individual course pages for SWP-035 through SWP-065 and publish their 124 existing resources: 31 guides, 31 worksheets, 31 editable PPTX decks and 31 matching slide PDFs. The 272 resources already live remain unchanged. Source teaching, module content, original course CBT mappings, school enrolment settings and existing learner/credential data are preserved. Existing editions retain their original draft labels; the course page states their current approval date and distinguishes pending assessment availability.

## Release controls

`publish_approved_materials` loads all eight authored releases, checks exact course/module content and resource metadata, validates local file hashes and freshly downloads/checksums all 124 private storage objects before taking write locks. It records the explicit owner approval without impersonating a reviewer account. A short database transaction locks the affected schools/courses/assets, rechecks lifecycle/protected fingerprints, moves the resources through approved to published and activates the 31 courses. Only lifecycle status/timestamps change. Every other field and every other school/course/learning/credential record remains protected. A parity failure rolls back publication.

The private storage bucket stays private. Learners enrol in an individual course and use the existing authenticated, enrolment-checked download route to receive short-lived resource URLs. Publishing metadata does not open the storage bucket or expose staff assessment banks. School enrolment remains closed; missing ParaLearn IDs stay blank and school certificates stay unavailable until their existing requirements are met. Course material approval does not manufacture assessment-provider support, passes, badges or signatures.

The publication command refuses an existing intent or applied receipt. Do not replay it after an uncertain outcome: inspect the recorded before/after state first. Operational journals, file verification rows and learner checks stay under ignored `production_courseware/private/material-release-2026-11-19/`. A new read-only audit must use a distinct path and preserve prior evidence.

## Validation and deployment

Eight new tests cover the exact 31-course/124-file release, preservation of teaching/CBTs/schools, checksum rejection, concurrent lifecycle drift, protected teaching drift, transaction rollback, published course notices/enrolment-checked downloads, and replay refusal. The full isolated suite passed all 206 tests in 286.596 seconds, and the migration drift check reported no changes. Live preflight verified all 124 exact remote file hashes before publication. Tests always use an explicit in-memory SQLite database; local `.env` is live Postgres.

The existing Vercel project is `sweep-academy` in the already linked team. Inspection showed production had not advanced with the recent main pushes, so the verified release also requires an explicit deployment through that existing connection. The owner has authorised production publication and main pushes. No new Vercel project, storage bucket, schema, RLS rule or account is needed. Keep secrets out of deployment arguments and use the existing CLI session.

Observed after publication: 65 active courses, no inactive authored drafts, 396 published assets, 25 coded schools still closed. Actual database totals and protected parity passed, alongside the public catalogue/all 65 course pages, all 124 released resource titles and all 124 unauthenticated download guards. Positive enrolled-download behaviour was exercised in isolated tests; no learner or credential writes were made during live verification. The release does not claim that videos or ParaLearn assessments have been produced.

The GitHub Actions account is locked due to billing as observed on the Phase 10 push. Local validation is distinct from CI; do not describe a job that did not start as passing.

## Next phase

After verified publication and push, continue CPS: retain SWP-001-003 and develop five additions toward eight courses. Its staging baseline must reflect this live release: 65 active courses and 396 published resources. The next five authored additions should initially be inactive with private in-review resources while their build is verified. Preserve all existing live teaching and CBTs. Authored progress remains 31/150 additions; 119 remain.
