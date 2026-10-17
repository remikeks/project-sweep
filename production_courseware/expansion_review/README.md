# Curriculum expansion: assessment and teaching review

Status: **draft for review, not publication approval**. Created 2026-10-17.

This folder is separate from the 30 approved course banks. It contains original
teaching scenarios and assessment drafts for SWP-031–034. They are not ParaLearn
exports and have no server assessment IDs. No existing question bank, learner
record, or published resource is replaced by these files.

Each course has 15 single-answer questions: five per module, one mark each.
The proposed pass mark is 70%, meaning at least 11 of 15 whole-mark answers.
This is a proposal, not an approved assessment standard or an imposed timer.
Question positions and options are fixed in the review export so reviewers can
cite stable IDs. The JSON records keys explicitly; never derive keys from order.

`assessment_source.json` is the editable authoring source. `build_expansion_review.py`
produces the readable review packs and JSON exports. Every item references an
authored teaching point, its module, and the checksum of the matching course
catalogue. Source fingerprints use canonical JSON so line endings and whitespace
do not change them; exported bank checksums use UTF-8 with LF line endings.
These links establish traceability, not expert approval or proof that
the existing eight-file package teaches the point adequately.

## Content gap found

The existing learner-guide generator repeats a generic learning sequence with
module focus words substituted. Its output is an outline-based draft, not enough
to demonstrate complete instruction for all the new assessment decisions.
The teaching notes in this review pack make the assessed reasoning explicit,
but must still be expanded and integrated into the learner guides, slides,
worksheets, and transcripts before learners are assessed. Do not publish a bank
just because its structure passes validation.

## Reference framework

These references were checked on 2026-10-17. Scenarios and teaching examples are
original SWEEP review drafts, not quotations or endorsed material. NASW standards
are a practice reference, not a statement of Nigerian or other local law.

- [NASW/ASWB technology standards](https://www.socialworkers.org/Practice/NASW-Practice-Standards-Guidelines/Standards-for-Technology-in-Social-Work-Practice): consider access, consent, confidentiality, professional boundaries, and suitability when choosing digital channels.
- [NASW/ASWB supervision standards](https://www.socialworkers.org/Practice/NASW-Practice-Standards-Guidelines/Best-Practice-Standards-in-Social-Work-Supervision): supervision combines administrative, educational, and supportive functions; local regulatory requirements still apply.
- [IPCC AR6 synthesis, Summary for Policymakers](https://www.ipcc.ch/report/ar6/syr/summary-for-policymakers/): inclusive decision-making, equity, resources, and monitoring support climate-resilient development; adaptation can have unequal effects.
- [IFSW ethical principles](https://www.ifsw.org/global-social-work-statement-of-ethical-principles/): dignity, participation, confidentiality, competence, and accountable decisions apply to practice and research, including digital settings.

## Publication checklist — all still open

1. Curriculum owner: approve scope boundaries, learning outcomes, and integrated teaching coverage.
2. Relevant subject-matter reviewers: verify each stem, key, rationale, distractor, and scenario; record named approval of an exact file checksum/version.
3. Local safeguarding, privacy, legal, and accessibility reviewers: adapt procedures and review accessible alternatives. No universal consent, reporting, retention, or supervision rule is asserted by this draft.
4. Materials owner: integrate approved teaching content into all eight assets per course; render and inspect all document formats, including the five DOCX files; rebuild checksums.
5. ParaLearn owner: import approved banks into the SWEEP account as unpublished assessments, verify answer keys and settings after import, assign actual assessment IDs, and test access and result delivery.
6. Release owner: reconcile the full 10-school, 34-course, 102-module, 272-asset candidate; verify no duplicate identities or content, then approve publication and activation together.

The last recorded production staging (2026-10-16) has four inactive course records
and 32 resources marked `in_review`. This review work does not change that state.
The four new assessments are local drafts only. Historical Render learner
completions and credentials remain excluded.

## Reproducible local checks

Run `python scripts/build_expansion_review.py --check` to validate the existing
review exports against the authoring source without changing files. Run
`python scripts/audit_expansion_candidate.py` to reconcile the original release
and four staged packages in memory, verify all 272 asset files, and check
cross-package identities and file checksums without copying or importing them.

The 2026-10-17 checks passed for 10 schools, 34 courses, 102 modules and 272
assets. The 60 draft stems are distinct from one another and from the 360
questions in the 24 available baseline exports. SWP-001–006 have no local
exports for comparison. These checks detect exact normalised stem duplicates,
not paraphrases or semantic overlap. A person must review that distinction.

Review packs:

- [Digital Social Work Practice](swp-031-assessment-review.md)
- [Climate Justice and Resilient Communities](swp-032-assessment-review.md)
- [Leadership Supervision and Programme Management](swp-033-assessment-review.md)
- [Participatory Research and Practice Innovation](swp-034-assessment-review.md)
