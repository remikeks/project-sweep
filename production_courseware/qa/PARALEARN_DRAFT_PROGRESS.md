# Historic ParaLearn draft-bank progress — 2026-10-04

> **Superseded status (2026-10-09):** All 30 assessment banks are approved for content use. This file is retained as a historical creation log only; its draft and publication notes are not the current assessment-approval status. See [PARALEARN_REVIEW_INDEX.md](PARALEARN_REVIEW_INDEX.md).

Target: 30 course banks, 15 questions each (450 total), left unpublished for expert review.

## Verified progress

- SWP-001–003: 15 questions each were verified saved in earlier work. Sources were course outlines; expert review should compare them against the full learner guides.
- SWP-004: 15 questions generated from the learner guide. A fresh editor connection showed `Synced with CBT microservice`, 15 questions and 21 marks. It unexpectedly showed `Published · students can join`. The Unpublish action returned `Draft · students can't join yet`. The resulting editor header changed to `Examination Assessment`, while retaining SWP-004; check the title on the next server connection.
- SWP-005: on continuation, the editor showed `Synced with CBT microservice`, 15 questions and 21.5 marks. It unexpectedly showed published status, and Unpublish returned draft status with a success notification. This bank is now confirmed synchronized. Its header also changed to `Examination Assessment` after Unpublish, while retaining SWP-005; check the title on a subsequent server connection.
- SWP-006: AI generation recovered on the next retry. Fifteen questions were imported and saved; a fresh server load confirms 15 questions, 21.5 marks, and `Synced with CBT microservice`. However, Save resulted in published status. Two Unpublish attempts produced a room-closed success notification but the editor continued to show published status, including after reload. Treat this room as potentially learner-accessible pending a ParaLearn fix. No Publish action was requested or clicked in this work.
- SWP-007: 15 questions generated successfully and preserved in `paralearn-swp-007-generation-preview.txt`. The live preview is preserved. These were deliberately not imported after the SWP-006 publication-control failure.
- SWP-008–030: 23 banks remain empty, 345 questions still to generate.
- The dashboard contains 31 rooms, including the previously identified duplicate SWP-017. Nothing was deleted.

## Preserved evidence

- `paralearn-swp-005-generation-preview.txt`: full UI preview with 15 questions, options, and rationales.
- `paralearn-swp-005-offline-state.txt`: editor state after Save.
- `paralearn-swp-005-offline.png`: screenshot of that state.
- The SWP-005 editor tab is preserved for continuation. Avoid clearing browser site data while the draft is only local.
- `../release-2026-10-03/paralearn_source_text.json`: extracted text of all 30 release learner guides, prepared for ParaLearn's text-source input. Direct file upload was blocked by the Chrome extension's file-access setting.

## Next actions

**Current blocker:** saving and unpublishing SWP-006 do not preserve the authorized draft status. Evidence: `paralearn-swp-006-unpublish-inconsistent.txt` and `.png`. The initial AI 503 is no longer the immediate blocker. Resolve the live publication-control issue before importing more question banks. Totals: 90 questions verified synchronized (SWP-001–006), plus 15 preview questions preserved (SWP-007). This is not 90 verified draft questions: SWP-006 still displays published.

1. Restore reliable ParaLearn service access. SWP-006–008 AI generation requests each returned HTTP 503 from ParaLearn's Gemini provider, citing high demand. SWP-006–008 editors also showed offline draft mode. One bounded retry of SWP-006 after waiting also returned 503. Error evidence is saved in `paralearn-generation-failures-2026-10-04.json`. No questions were returned for these three courses.
2. Generate and save 15 questions per remaining course from each full learner guide.
3. Verify each canonical room's title, question count, and unpublished state after server load. Do not interpret the dashboard's generic `Always Live` label as publication verification.
4. Expert review: source grounding, answer keys, plausible distractors, meaningful practice questions rather than document-structure questions, local policy/clinical scope, and consistent scoring.
5. Publish and map assessments only after review. No new SWEEP mappings or learner results were created in this work.

Canonical SWP-004 ID: `cmusrsyoj000bof8cv9qbwi1b`.
Canonical SWP-005 ID: `cmusrt2b6000dof8c25q28dq6`.
