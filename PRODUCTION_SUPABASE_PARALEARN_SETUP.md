# SWEEP Production Supabase & ParaLearn Setup Curriculum

This document is the runbook for taking the completed SWEEP content portal,
ParaLearn CBT integration, and Phase 4 learning/credential features live.

## Outcome

At completion, SWEEP will have:

- Supabase Storage for approved course assets.
- Verified Supabase JWT access for content authors, reviewers, and publishers.
- A migrated production database.
- ParaLearn-hosted CBT assessments for every published course.
- A signed ParaLearn webhook that records results and awards credentials.
- A verified live learner journey: enroll, complete modules, pass CBT, receive a
  badge, pass the school exam, receive a certificate, and verify it publicly.

## 1. Collect the Required Access

Before configuration, have a project owner provide access through secure
channels. Never add any secret to Git, browser code, or this document.

- [ ] Supabase project owner or administrator access.
- [ ] Production deployment host access (Render or the chosen host).
- [ ] Production database access sufficient to run Django migrations.
- [ ] ParaLearn workspace administrator access.
- [ ] ParaLearn API key, workspace details, assessment identifiers, and webhook
      signing secret.
- [ ] Production domain names for SWEEP and the content portal.
- [ ] A GitHub account with write access to `remikeks/project-sweep`.

## 2. Supabase Project and Storage

### Create the storage bucket

- [ ] Create a private bucket named `sweep-course-assets`.
- [ ] Keep the bucket private; learner downloads are served through SWEEP's
      permission-aware download route or short-lived signed URLs.
- [ ] Do not expose the Supabase service-role key to the portal frontend.
- [ ] Configure allowed file sizes and use only the approved course-asset types:
      DOCX, PDF, PPTX, video, transcripts, worksheets, and supported references.

### Configure browser origins and storage access

- [ ] Add the production content-portal origin to Supabase Auth redirect URLs.
- [ ] Add the local development origin only where needed.
- [ ] Configure CORS to allow only the SWEEP portal origins and required HTTP
      methods/headers; do not use `*` with authenticated requests.
- [ ] Confirm direct browser uploads work only through a short-lived,
      server-created upload intent.

### Configure content roles

The portal expects verified Supabase JWTs. Roles must come from trusted
application metadata, not user-editable metadata.

- [ ] Define `author`, `reviewer`, and `publisher` roles in Supabase
      `app_metadata` or another server-controlled role source.
- [ ] Map those role values in `SUPABASE_JWT_ROLE_MAP`.
- [ ] Configure the JWT issuer, audience, JWKS URL, allowed signing algorithms,
      role claim, and/or permission claim in SWEEP.
- [ ] Test each role: author creates drafts; reviewer approves; publisher
      publishes/retires; unauthorised users receive no access.

## 3. Production SWEEP Configuration

Source-control quality gates run without production credentials. Keep the
deployment secrets below out of CI logs and pull-request environments; the
automated suite uses an isolated SQLite database instead.

Set these values only in the deployment host's protected environment-variable
manager:

```text
DEBUG=False
SECRET_KEY=<strong unique production value>
ALLOWED_HOSTS=<production domains>
CSRF_TRUSTED_ORIGINS=https://<production domains>
DATABASE_URL=<production PostgreSQL connection URL>

SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_STORAGE_BUCKET=sweep-course-assets
SUPABASE_SERVICE_ROLE_KEY=<server-only secret>
SUPABASE_JWT_ISSUER=https://<project-ref>.supabase.co/auth/v1
SUPABASE_JWT_AUDIENCE=authenticated
SUPABASE_JWKS_URL=https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json
SUPABASE_JWT_ALGORITHMS=<approved asymmetric algorithm list>
SUPABASE_JWT_ROLE_CLAIM=<trusted role claim>
SUPABASE_JWT_ROLE_MAP=<JSON role mapping>
```

- [ ] Set secure cookies and HTTPS redirect only after confirming the deployment
      proxy supplies the forwarded protocol safely.
- [ ] Confirm static assets collect successfully.
- [ ] Run `python manage.py check --deploy` with production settings.
- [ ] Confirm the **Django Quality Gate** workflow is green for the deployment
      revision before promotion.

## 4. Apply the SWEEP Database Changes

Deploy commit `87db731` or its pushed equivalent, then:

- [ ] Back up the production database.
- [ ] Run `python manage.py migrate` once as a release step.
- [ ] Verify migrations include:
  - Course assets and upload intents.
  - ParaLearn attempts, learner identities, and webhook events.
  - Frozen school curricula and sequential module progress.
  - Credential lifecycle fields and public verification support.
- [ ] Confirm old school enrolments received curriculum snapshots.
- [ ] Confirm no live credential data was lost and existing credentials remain
      publicly verifiable after the migration.

## 5. Configure ParaLearn CBT

### Configure the integration

Set the following server-side variables:

```text
PARALEARN_API_BASE_URL=<confirmed ParaLearn CBT API base URL>
PARALEARN_API_KEY=<server-only API key>
PARALEARN_API_KEY_HEADER=Authorization
PARALEARN_API_KEY_PREFIX=Bearer 
PARALEARN_CANDIDATE_PROVISION_PATH=/candidates
PARALEARN_RESULT_PATH_TEMPLATE=<confirmed result lookup path, if enabled>
PARALEARN_ALLOWED_LAUNCH_HOSTS=<comma-separated ParaLearn hosts>
PARALEARN_WEBHOOK_SIGNING_SECRET=<server-only webhook secret>
```

- [ ] Confirm every production setting against ParaLearn's current workspace
      documentation before saving it.
- [ ] Add each ParaLearn assessment identifier to its corresponding
      `Course.paralearn_assessment_id` in Django admin.
- [ ] Do not enable a course assessment until its ParaLearn assessment is
      published and mapped.

### Register the webhook

Register this HTTPS endpoint in ParaLearn:

```text
https://<sweep-domain>/courses/paralearn/webhook/
```

- [ ] Configure the `exam.attempt.completed` event.
- [ ] Configure the same HMAC signing secret in ParaLearn and SWEEP.
- [ ] Send a signed test payload.
- [ ] Confirm invalid signatures are rejected and create no learner result.

## 6. Live Acceptance Tests

Use a disposable test learner and a non-production assessment before opening
the service to learners.

### Content portal

- [ ] Author signs in and uploads an approved sample document.
- [ ] Reviewer moves it to approved.
- [ ] Publisher publishes it.
- [ ] Enrolled learner can download it; unenrolled learner cannot.

### CBT and credentials

- [ ] Enrol in a course with modules.
- [ ] Confirm later modules and CBT are locked until earlier modules are marked
      complete.
- [ ] Mark all modules complete in order.
- [ ] Launch ParaLearn CBT and complete a passing attempt.
- [ ] Confirm the signed webhook completes the course and creates one badge.
- [ ] Retry or redeliver the same webhook; confirm no duplicate badge is made.
- [ ] Enrol in a school, complete its frozen curriculum, and pass its SWEEP
      school exam.
- [ ] Confirm a certificate is issued once.
- [ ] Open `/credentials/verify/<credential-uuid>/` in a private browser
      session and confirm the active credential verifies correctly.
- [ ] Revoke and reissue a test credential through staff admin; confirm old and
      replacement verification states are accurate.

## 7. Operating Procedures

- [ ] Schedule `python manage.py reconcile_paralearn_results` for delayed CBT
      result recovery, only after configuring ParaLearn result reconciliation.
- [ ] Monitor webhook failures, failed launch attempts, upload errors, and
      expired upload intents.
- [ ] Rotate Supabase and ParaLearn secrets through the deployment host, never
      through Git.
- [ ] Back up Postgres and verify restore procedures.
- [ ] Require a review/approval/publish workflow for every future course asset.

## Completion Record

Record the production date, project reference, deployment revision, test
learner used, webhook verification result, and responsible administrator in a
secure operations system. Do not record secrets here.
