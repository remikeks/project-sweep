# School realignment phase one

Authorized by the owner on 14 November 2026. This phase changes the primary
school relationship of each of the 34 existing courses. It does not change
course identifiers, titles, URLs, modules, resources, CBT IDs/settings,
assessment results, progress or badges.

## Rollout

1. Run the application test suite using an isolated database. Never use the
   production database as the test database.
2. Save the private read-only production snapshot with
   `scripts/audit_school_refactor_baseline.py --output <private-path>`.
   The snapshot contains private learning records and must not be committed.
3. Apply additive migration `schools.0003_coded_school_catalogue`. No seed or
   catalogue-sync command should run during this rollout.
4. Deploy and verify the application before switching the catalogue. Existing
   public school pages continue to work with the additive schema.
5. Run `manage.py realign_schools` to validate the actual database without
   writing, then apply with `--commit --receipt <new-private-path>.json`.
6. Run `manage.py realign_schools --verify <new-private-path>.applied.json`
   immediately, before unrelated learner activity changes the snapshot hashes.
7. Verify 25 public schools, 34 course URLs and assessment IDs, former-school
   transition pages and existing learner access. Retain the snapshot and both
   receipts in private storage.

The command refuses unrecognized courses/schools, title drift or missing legacy
curriculum snapshots. Its transaction updates only course school references,
creates coded school records and marks former schools historical. It hashes
all course, module, resource, quiz, school-exam, learning and credential records
before and after, excluding only the intended course school reference. A repeat
run does not recreate schools or overwrite the first receipt.

## Rollback

Validate with `manage.py realign_schools --rollback <receipt>.applied.json`.
Apply with the additional `--commit` flag. Original assignments and school
states are restored; newly created school rows remain inactive. No school row
is deleted. Automatic rollback refuses any changed protected record or a new
school enrolment/certificate; review new learner activity rather than erase it.
The additive schema can remain during an application rollback.

## Phase boundary

All coded schools start with full-school enrolment closed. Individual current
courses continue to work. New-school local-MCQ examination and certificate
issuance paths are blocked until the separate integrated ParaLearn school-exam
workflow is implemented and verified. Historical learners keep the original
school exam route. Legacy seed/sync commands are blocked after realignment
because they overwrite existing content and examinations.

Phase two develops the new course evidence dossiers and resources, immutable
curriculum versions, and mixed-question ParaLearn school assessments. No new
courses or new exams are created by the phase-one realignment command.

## Execution receipt 14 November 2026

- Production deployment `dpl_A8QQ57CPwCT1B8Suw2xshT1FSZ41` is Ready and promoted
  to `https://sweepacademy.org`.
- Applied additive migration `schools.0003_coded_school_catalogue`.
- Created 25 coded current schools and retained 10 former schools as historical
  records excluded from public browsing and new enrolment.
- Realigned all 34 existing courses once. Their course fields, CBT identities,
  modules, assets, learning records and credential records passed exact hash parity.
- Counts retained: 34 courses, 102 modules and 272 assets. All 34 existing course
  CBT identifiers were present before execution and are unchanged afterward.
- All 145 application tests passed locally. No hosted CI pass is claimed.
- All 71 live HTTP checks passed: school and course lists, 25 current school
  pages, 10 former-school transition pages and 34 direct course URLs.
- A repeat run found zero assignments to change and made no writes.
- Private pre-change snapshot, prepared/applied receipts and HTTP verification
  evidence are under `production_courseware/private/school-refactor-2026-11-14/`.
  Those files are excluded from Git and Vercel uploads.
- No new course content, course CBTs or school examinations were created in this
  phase. New school enrolment/certification remains closed until phase two and
  the integrated ParaLearn examination checks are complete.

Next phase: develop and review the first foundational course batch from the
approved working curriculum, with individual evidence dossiers. Prepare new
curriculum versions and the ParaLearn mixed-question marking and final-result
contract alongside content production. Pending signatory details do not block
research or draft course development.
