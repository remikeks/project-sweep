# Foundational Social Work first development batch

Status: **draft for review, not approved for learner release**. Evidence checked on 14 November 2026.

This is the first two-course development increment after the 25-school realignment. It is not completion of the 150-course expansion. FSW retains its three existing health-application courses unchanged. These drafts would bring FSW to five released courses; the approved full FSW target remains ten. Five is a breadth milestone, not a claim of comprehensive professional qualification.

| Code | Draft course | Modules | Draft course MCQs |
| --- | --- | ---: | ---: |
| SWP-035 | Social Work Values and Ethical Decision Making | 3 | 15 |
| SWP-036 | Generalist Assessment and Case Management | 3 | 15 |

`authoring.py` contains original teaching, worked cases, activities, feedback, teaching points and assessment authoring material. `review_package.json` is the deterministic export. The package includes answer keys and must remain in staff review storage; `.vercelignore` excludes all `production_courseware` from application deployment. The staging command only copies learner lesson fields and references to inactive database records. It does not copy assessment keys into lessons or provision a remote exam.

Each module has an outcome, at least 250 words of teaching, a fictional worked case, an activity, feedback and cited sources. Each of its five teaching points maps to one MCQ. Source checksums make subsequent unreviewed changes detectable. These checks establish structure and traceability, not academic approval or psychometric validity.

## Evidence review

The six sources comprise two professional frameworks and four open-access research articles. Publisher full text and Crossref metadata were checked for R1, R2 and R3. R5 was checked against its publisher page, DOI metadata and its 17-page PDF, including its methods. Retrieval bytes and hashes are retained privately under `production_courseware/private/school-phase2-2026-11-14/research`.

- R1 is a qualitative systematic review of moral distress and injury. It informs the discussion of organisational constraints; it does not provide a Nigerian prevalence estimate or a proven SWEEP intervention.
- R2 is a qualitative comparison of ten German rehabilitation facilities. The title correction in DOI `10.3389/fresc.2024.1508335` was checked. Findings inform discussion of competing mandates with explicit limits on transfer to Nigeria.
- R3 is an umbrella review of care-navigation roles. It informs role clarification and coordination, while acknowledging varied definitions and review quality. It does not establish universal effectiveness of case management.
- R5 is an IJSDS Nigerian desk review, not new participant research. Its search and selection reporting are insufficiently detailed for independent replication. It provides contextual questions about governance, not a prevalence estimate, proof of a local allegation or an evaluated intervention.

The source records state the use and limitation of each article. Professional guidance is a practice benchmark rather than Nigerian legislation. Learner-facing text links the original works and contains original commentary; no publisher figures or article passages are reproduced.

The Frontiers impact table reports 2025 JIF/CiteScore quartiles in its 2026 release: Rehabilitation Sciences Q1/Q2 and Health Services Q2/Q1. These are **publisher-reported journal metrics**; the table does not identify the relevant subject categories and independent ranking verification remains outstanding. No Q1/Q2 status is claimed for IJSDS. Quartiles do not certify an individual article's quality.

Candidate R4 was not included: the direct publisher retrieval returned a JavaScript challenge rather than the article. An HTTP 200 alone is not evidence of a verified full text. No teaching claim in this batch relies on R4.

## Final school examination

`school_exam_blueprint.json` is an **internal authoring contract**, not a verified ParaLearn payload. Its proposed five-course FSW curriculum includes SWP-016, SWP-017, SWP-018, SWP-035 and SWP-036. It does not alter those existing courses or course CBTs.

The proposed exam has 40 MCQ slots at one mark each, six short answers at five marks each and two essays at fifteen marks each: 100 marks. Each required course has eight MCQ slots and is also represented in the written questions. All eight written questions have original prompts, model marking guidance and criterion-based rubrics. The 40 MCQ slots remain unbound pending approved item selection or authoring and review. The 70 percent pass mark and 150-minute duration are proposals requiring academic review and piloting.

Human marking and moderation are required. AI may assist a future workflow but cannot alone finalise a written result. A future result adapter must verify learner, attempt, school, curriculum version and provider result identity; authenticate and reconcile results; retain original responses and marks; support appeals and adjustments; and avoid duplicate completion or credential events. Written grading pending, a raw submission, a partial result or an MCQ-only score must not trigger certification.

The local contract validator and acceptance tests are preparatory work. They are not wired into the certificate service and cannot enable a certificate. The existing new-school certificate block stays in force.

## ParaLearn discovery and remaining dependencies

The current course integration remains untouched. A read-only attempt to discover school-exam support could not authenticate: Vercel exports sensitive integration values as placeholders. Public or local frontend types mentioning essays do not prove that the deployed external API supports written grading or finalisation. No provider assessment was created and no result contract is claimed verified.

Live integration must run with an authorised non-placeholder server credential. Verify the deployed API's exact question types, rubric representation, marking permissions, moderation states, final result semantics and signed delivery/reconciliation behavior before implementing the school launch/result adapter. Do not map assumed `SHORT_ESSAY` or `LONG_ESSAY` types into the production contract without verification.

The next content release work is independent subject-matter and Nigerian practice review, revisions, accessible learning resources, approved ParaLearn course exams and learner piloting. This draft is not a recorded video, published slide deck or an approved badge-bearing course. Enrolment and certification stay closed until all release conditions are met. Certificates require the Head of Learning name and authorised signatures of the Head of Learning and Founder Prof. Mina Ogbanga; no signature is fabricated.

## Reproduce and stage

Run `scripts/build_fsw_batch.py` to export and validate the package. Run `scripts/build_fsw_review_documents.py` with the bundled artifact Python to create the legible 12-point review guides and progress report. Render and inspect final Word documents before delivery.

`manage.py stage_authored_review --package production_courseware/phase_two/fsw_batch_01/review_package.json` is read-only validation. Add `--commit --receipt <new private receipt path>` only for authorised inactive staging. Staging is create-only, globally checks course code/title/slug collisions, requires closed school enrolment, makes all additions in one transaction, and proves pre-existing table values unchanged. A second run is refused; it cannot silently replace an earlier draft. The original realignment command has a strict 34-course baseline and should not be reused after additive course development.
