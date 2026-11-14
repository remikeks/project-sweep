# Academy phase two first development increment

Executed on 14 November 2026 following the owner's instruction to proceed in phases.

## Delivered in this increment

Two original research-informed FSW teaching drafts were created and staged in the live database as **inactive** courses: SWP-035 Social Work Values and Ethical Decision Making and SWP-036 Generalist Assessment and Case Management. Six new modules contain teaching, worked cases, activities, feedback and linked evidence notes. Thirty course MCQs have answer keys, rationales and teaching-point mappings in staff review files, not in learner lesson fields.

The live database now holds 36 course records: the same 34 active courses and two inactive drafts. FSW still displays its three existing active courses; it would reach five after the new drafts pass release checks. Its approved full target remains ten. The wider 150-course development programme remains in progress; two drafts are not 150 published courses.

The mixed school-exam authoring contract requires coverage of every course in the proposed first FSW curriculum. It contains 40 unbound MCQ slots, six short-answer prompts and two essay prompts, totalling 100 marks. The written questions have model guidance and criterion-based rubrics. The proposed pass mark is 70 percent and duration is 150 minutes, pending academic review and piloting. Human marking and moderation are mandatory in the draft contract.

## Verification evidence

- All **158 Django tests passed** using an isolated in-memory SQLite database; no test ran against the live database. Thirteen new tests cover authored staging and the mixed-exam authoring contract.
- Staging compared before/after fingerprints for every pre-existing row in the schools, courses, learning and credentials apps. Every fingerprint matched, including original course text, modules, assets, course CBT IDs, attempts, progress and credential records.
- A separate read-only post-staging verification repeated parity checks and checked exact authored draft fields, references, school assignment, inactive status and blank provider assessment IDs.
- Four live HTTP checks passed: the public catalogue still shows 34 courses and excludes draft titles; both draft course URLs return 404; an existing FSW course remains accessible.
- The 25 coded schools remain closed to new full-school enrolment. No new course assessment, candidate, attempt, badge or certificate was provisioned by this increment.

Private receipts are under `production_courseware/private/school-phase2-2026-11-14/`: `fsw-staging.json`, `fsw-staging.applied.json` and `staging-verification.json`. These contain integrity evidence and remain excluded from Git and deployment.

## Files and operation

`production_courseware/phase_two/fsw_batch_01/README.md` records the evidence appraisal, rights, journal ranking limitations, remaining reviews and release dependencies. `authoring.py` is the original source; `review_package.json` and `school_exam_blueprint.json` are validated deterministic exports. They are staff review material and include assessment keys. The existing `.vercelignore` excludes the entire production courseware tree.

`stage_authored_review` is additive and create-only. It requires closed school enrolment, a new private receipt path and globally collision-free identities. It cannot update an active or existing inactive course. A repeat run refuses the existing identities. If a draft needs revision, implement a separately reviewed version-update operation with provenance; do not bypass the guard or reuse the old 34-course realignment command.

The database additions are compatible with the current deployed academy. This increment does not deploy a new runtime feature. The new Python authoring validators and offline result-contract tests are local implementation work, not a live ParaLearn school-exam adapter or a certificate authorisation path.

## Live integration and release dependencies

A read-only provider discovery attempt could not authenticate using the exported environment: Vercel redacts the sensitive integration credential. The probe now refuses placeholder credentials. No claim is made that course CBTs are unavailable or that the current live integration has stopped working. Local/frontend references to essay types are not proof of the deployed external API contract.

Verify mixed question types, rubric fields, marking/moderation permissions, final-state semantics and authenticated result reconciliation using an authorised server-side credential. Then implement and test curriculum-bound school launch/results with immutable attempt identity, idempotent finalisation, appeals and audit history. Do not accept a submitted, partly marked or AI-only result as final.

Content still requires independent subject-matter and Nigerian practice review, accessible release resources, approved ParaLearn course CBTs and learner piloting. The 40 school MCQ slots need approved bindings. Opening full-school enrolment also requires the agreed curriculum version and readiness checks. School certification additionally requires all curriculum courses, a finalised and moderated ParaLearn school exam, and authorised signatories. The Head of Learning name and authorised signature images remain outstanding. Founder name: Prof. Mina Ogbanga. No signature was invented and the deployed certificate block remains in force.

Readable Word review guides and a one-page progress report for Prof. Mina are under `../output/academy_phase_two/`, with a 12-point body font. They are drafts for review; they are not public learner release assets.
