# Phase 15 BLU

The School of Climate Change and Blue Economy Social Work (BLU) had no courses before this phase. The academy baseline was 90 active courses, 496 published resources and 25 closed school enrolments. The BLU target is six courses. The authoring package adds SWP-091 through SWP-096, with 18 modules and 90 review MCQs checked against 840 earlier stems.

The courses cover blue economy foundations, fisheries livelihoods and social protection, coastal climate adaptation, equitable marine conservation, blue finance and community benefit, and a coastal livelihoods planning practicum. Each uses worked examples and fictional coastal cases. The curriculum map compares the course activities with Duke's Ocean Justice course and selected CSWE social work competencies. Its evidence register records access and reuse terms and distinguishes official guidance, regional synthesis, original open research and contextual IJSDS discussion.

Each course has a learner-guide PDF with 12-point body text, a three-page worksheet PDF, an editable PowerPoint and the matching slide PDF. The 24 files include 144 PDF pages, of which 93 are slides. The rendered PDFs passed visual and automated page checks. The decks passed structural checks and were rendered through LibreOffice. Native PowerPoint review and learner piloting are pending. Video is planned for a later phase.

The ParaLearn school exam blueprint covers all six courses. Its draft contains 40 MCQ slots, six short answers and two integrative essays that each draw on every course. The three sections total 100 marks. Timing and pass thresholds await piloting. Written responses require human marking and independent moderation. Graded delivery requires a private question bank and verified provider bindings. The Head of Learning name and signature are pending. Founder Prof. Mina Ogbanga is the other signatory.

Build with `scripts/build_blu_source.py`, `scripts/build_blu_six_course_exam.py` and `scripts/build_blu_media.py`. Use an isolated SQLite database when testing because the default application connection is live. The 229-test suite passed in 237.901 seconds and the migration check found no changes. All 870 earlier courseware files at `7b23151cf62719540a4b995040c93af5375b8c61` passed source parity. The scoped publication workflow verifies the production baseline, staged resource hashes and prior records. The academy applies its download controls to LMS copies. The committed learner files and review examples are public.

Phase 15 brings the programme to 62 of the 150 planned course additions. Phase 16 is EIL. Verify the live inventory and SW-EMHEC scope before finalising the eight-course curriculum map.

## Production verification

Staging added six inactive courses and 18 modules. The 24 private uploads matched the source file hashes, and their metadata was registered for review. The scoped release then activated SWP-091 through SWP-096 and published all 24 resources. Live verification passed for 96 active courses, 520 published resources, 97 public pages and 24 guest download guards. The 24 published files passed a fresh remote hash check. Earlier course, CBT, learner and credential records passed production parity checks. All 25 school enrolments remain closed pending verified school exams and certification readiness.

Vercel built commit `67baac72055451121d4e2d688d5ebbee267b422c` in deployment `dpl_AqKWFRci7ZJnnzFmoy9ssnAM3WBM` and assigned both academy domains. The catalogue, six BLU pages and 24 download guards passed after deployment. GitHub Actions run 46080873727 never started its job because of an account billing lock. [GitHub Actions run](https://github.com/remikeks/project-sweep/actions/runs/46080873727)

The [one-page report for Prof. Mina](production_courseware/phase_fifteen/SWEEP_Phase_15_Report_Prof_Mina.pdf) was visually verified at 130 DPI. The learner archive passed a ZIP integrity check and matched all 24 approved file hashes.
