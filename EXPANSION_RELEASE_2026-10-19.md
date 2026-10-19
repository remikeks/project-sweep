# Expansion publication and integration verification

## Published curriculum

On 2026-10-18 at 17:10:22 UTC the verified publication transaction activated
SWP-031–034 and published their 32 existing resources. Totals after publication:
10 schools, 34 active courses, 102 modules and 272 published resources (240
baseline v1.0.0; 32 expansion v1.1.0). No duplicate catalogue rows were imported.
A repeat publication returned unchanged. All 32 remote files were downloaded
and checked against the reviewed manifest before the transaction.

| Course | Genuine ParaLearn exam ID |
| --- | --- |
| SWP-031 Digital Social Work Practice | exam_1792326226918_zcmk7 |
| SWP-032 Climate Justice & Resilient Communities | exam_1792327109114_9pkcv |
| SWP-033 Leadership Supervision and Programme Management | exam_1792327123620_zu6i3 |
| SWP-034 Participatory Research and Practice Innovation | exam_1792327137939_l90mh |

All four exams are published, roster-restricted, 15 questions/15 marks and 60
minutes. All 60 question texts, options, keys and rationales matched the reviewed
source through the official provider API. Questions and options are shuffled.

## Actual integration evidence

Each exam had an actual synthetic zero-score submission, with a signed provider
event processed by SWEEP. No passing result or learner credential was fabricated.

| Course | Original QA provider attempt | Signed event |
| --- | --- | --- |
| SWP-031 | att_ef9ed76c834d647a717db485 | evt_14fb390ea226d2f8c0ca |
| SWP-032 | att_49d8cd7efde1728c50b342e7 | evt_e4264f90942ef3f12c62 |
| SWP-033 | att_26fcfe63b3d6c816d7059211 | evt_fad671221877f11ac1ad |
| SWP-034 | att_bff11e33cf40fa19c188c920 | evt_494dbcf8c76084c27d3c |

The existing provider key and webhook secret were configured for the production
API at `https://cbt.pln.ng/api/cbt`. The webhook destination is
`https://sweepacademy.org/courses/paralearn/webhook/`. No secrets belong in this
receipt. Private import, checksum, publication and QA journals are excluded
from Git and Vercel uploads.

Result recovery was tested against genuine provider slips: the provider requires
its internal attempt ID, not SWEEP's external UUID. Recovery now resolves that
ID using the authenticated exam monitor and exact candidate/student/exam/attempt
correlation; it never matches by display name.

Live retake testing found that ParaLearn deduplicates candidates by exam and
student ID. Additive migration `learning.0006_per_attempt_provider_identity`
preserves old attempts while new attempts receive separate opaque candidate
UUIDs. A real hosted retake then started and submitted successfully. Its signed
result revealed that the provider normalizes `metadata.sweepLearnerId` to the
candidate UUID. The compatibility fix accepts only the stored learner UUID or
that exact attempt's candidate UUID, with independent owner/exam checks.

## Deployment and quality gate

Commit `eeb5398` was pushed and deployed as
`dpl_5KPZnxQGmhWNdWxncmy4D8GVPJ32`, confirmed Ready with production aliases
`sweepacademy.org`, `www.sweepacademy.org` and `sweep-academy.vercel.app`.
The subsequent metadata compatibility fix is commit `d054e7b` and passed all
127 tests locally. Final deployment and post-fix live-delivery verification are
recorded below when complete; the earlier retake event remains an honest failed
processing record, not rewritten as success.

GitHub workflow runs `39148249154` (8375d54) and `39174288858` (eeb5398) failed
before any steps ran. Their failure annotation says the account is locked due
to a billing issue. This is NOT a passing hosted quality gate and is NOT evidence
of failed application tests. The owner must resolve GitHub billing before a
hosted rerun can establish CI status. Do not disable or weaken the gate to hide it.

## Scope and governance

Owner authorization permits an introductory research-informed release.
Independent subject-matter approval and professional accreditation are not
claimed. Historical Render learner records and duplicate local material remain
excluded. The old 32 storage objects are retained intentionally for rollback,
not imported as additional resource records.

Optional research enrichment of six original online courses is documented in
`RESEARCH_ENRICHMENT_2026-10-19.md`; the remaining 24 and all 240 baseline
downloadable files are not represented as enriched.

## Final verification — 2026-10-19 Africa/Lagos

- Application commit `57d180f` includes the provider metadata fix `d054e7b`.
- Production deployment `dpl_HVAXCUYwrwd6iZxkgmghEtXKEqPn` confirmed Ready,
  https://sweep-academy-gvvht7ri1-evanders-projects-83d1e543.vercel.app,
  with the live alias https://sweepacademy.org.
- All **132 tests passed** locally; migration consistency check reported no
  changes. GitHub-hosted CI remains blocked by the account billing lock.
- Final browser retake: local attempt `b137e9e0-03f6-4664-a4ff-333c58ec0235`,
  provider attempt `att_168dea2094563c0f4c383be7`, signed event
  `evt_cb2b1a9923c2664c28e0`. The event processed without error and verified the
  actual zero-score result at 2026-10-18 23:14:03 UTC. Candidate and provider
  attempt IDs differ from the previous submission.
- The earlier metadata-rejected test was recovered through the live Check
  result button using its genuine provider result; the original event's error
  remains in the audit trail.
- Browser verification showed the optional Motivational Interviewing reading,
  its evidence limitations, learning activity and Crossref/OpenAlex/DOAJ links.
- Final database audit confirmed 10 schools, 34 active/mapped courses, 102
  modules, 272 published assets, no duplicate course codes or logical resource
  identities, and zero QA badges/certificates.
- The clearly labelled synthetic QA account was deactivated after verification;
  its audit history was retained. A public browser page then showed Log in / Sign
  up and the live count of 34 courses across 10 schools.
