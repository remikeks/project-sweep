# SWEEP Academy Curriculum Governance

## Authoritative catalogue

The live Vercel catalogue of ten schools is the authoritative curriculum.
The older Render export is an archive and reference source only. It must not
be bulk-imported into production.

New curriculum is added to an existing school unless a documented governance
decision establishes a new school. This protects learners from near-duplicate
paths, separate certificates for the same capability, and conflicting course
resources.

## Current baseline

- 10 schools
- 30 courses
- 90 modules
- 240 published course assets (eight per course)

The baseline is a release snapshot, not a permanent course-count limit. An
approved additional course within one of the ten schools increases the course
and asset totals while retaining the ten-school structure.

## Required review before a course is built

For every proposed course, record:

1. the host school and rationale;
2. one measurable course outcome and three module outcomes;
3. the current course(s) reviewed for possible overlap;
4. what is genuinely new rather than renamed or repeated material;
5. subject-matter, safeguarding, and jurisdictional review requirements;
6. ownership of the learner guide, deck, transcripts, worksheet, and ParaLearn assessment; and
7. the replacement, redirect, or learner-record policy if it supersedes old content.

The current planned placements are:

| Capability | Host school | Delivery form |
| --- | --- | --- |
| Social-work foundations | Shared orientation, not a school | Short pre-catalogue orientation |
| Digital social work | Community & Macro Practice | New course |
| Climate justice and resilient communities | Disaster Response and Community & Macro Practice | Targeted modules or course |
| Leadership, supervision, and programme management | Community & Macro Practice | New course or extension |
| Research methods and innovation | Community & Macro Practice and Social Policy & Advocacy | Targeted modules or course |
| Broad professional practice | Shared material across applicable schools | Reusable modules, not a duplicate school |

Digital Social Work Practice is assigned to Community & Macro Practice. It is
an in-review course until subject-matter, privacy, accessibility, and local
legal review are complete.

Climate Justice & Resilient Communities is assigned to Disaster Response &
Crisis Intervention. It is an in-review course until climate-justice,
accessibility, safeguarding, and local legal review are complete. It must not
duplicate Disaster Preparedness & Response Planning or Long-Term Disaster
Recovery Support.

Leadership Supervision & Programme Management is assigned to Community & Macro
Practice. It is an in-review course until leadership, professional-practice,
safeguarding, and local legal review are complete. It must not duplicate
Program Development & Evaluation or Community Organizing & Coalition Building.

Participatory Research & Practice Innovation is assigned to Community & Macro
Practice. It is an in-review course until participatory-research,
research-ethics, accessibility, data-protection, and local legal review are
complete. It must not duplicate Community Needs Assessment, Program Development
& Evaluation, or Using Data to Drive Policy Change.

Broad professional practice is covered through Foundation Orientation and the
reusable boundary, supervision, referral, and escalation instructions that are
included in every course package. It will not be added as an eleventh school or
an additional certificate path.

## Publication gate

Run this read-only check for every release before upload and publication:

```powershell
.\.venv\Scripts\python.exe manage.py audit_curriculum_release `
  --catalogue production_courseware\release-2026-10-03\course_catalogue.json `
  --manifest production_courseware\release-2026-10-03\upload_manifest.json `
  --release production_courseware\release-2026-10-03
```

It verifies unique school/course/module identities, a unique course code and
slug, a complete eight-resource package per course, unique storage identities
and checksums, and the bytes of every supplied release file. It makes no
database, Storage, or learner-record changes.

## Learner record rule

Do not automatically transfer Render completions, assessment attempts, badges,
or certificates to new Vercel courses. The learning content, module sequence,
assessment items, and resources changed. Preserve historical records as an
archive and review any migration case by case.
