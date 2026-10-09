# ParaLearn CBT integration boundary

SWEEP uses ParaLearn CBT as the authoritative source of assessment results.
The built-in course quiz remains available only as a historical, non-authoritative
record. It cannot complete a course or award a badge.

## Deliberate deployment guardrails

No live ParaLearn URL, workspace API key, or webhook secret is configured in
source control. Empty defaults disable candidate provisioning, reconciliation,
and result processing. A deployment must supply its workspace credentials from
the secret manager before it can make an outbound request.

```text
PARALEARN_API_BASE_URL=https://pln.ng/api/cbt
PARALEARN_API_KEY=<workspace API key>
PARALEARN_API_KEY_HEADER=Authorization
PARALEARN_API_KEY_PREFIX=Bearer 
PARALEARN_CANDIDATE_PROVISION_PATH=/candidates
PARALEARN_RESULT_PATH_TEMPLATE=/attempts/{attempt_reference}/slip
PARALEARN_ALLOWED_LAUNCH_HOSTS=pln.ng
PARALEARN_WEBHOOK_SIGNING_SECRET=<workspace webhook secret>
```

The base URL must be supplied by deployment configuration, rather than added as
a source-code default. Never expose either secret to the browser. The documented
HMAC defaults are `x-cbt-signature`, `sha256=`, and `hmac-sha256`.

## Stable SWEEP-to-ParaLearn identifiers

`CourseAssessmentAttempt.id` is a SWEEP UUID. It is sent as both
`externalAttemptId` and `metadata.sweepAttemptId`. Each learner receives one
persisted, opaque `ParaLearnLearnerIdentity.external_id` UUID; it is sent as
`studentId` and `metadata.sweepLearnerId`. This avoids exposing a Django user
primary key and makes relaunches and signed results deterministic.

`Course.paralearn_assessment_id` must contain the ParaLearn `examId` for that
course. ParaLearn's own candidate ID (`cand_…`) and submitted-attempt ID
(`att_…`) are retained separately for audit and reconciliation.

## Candidate provisioning and hosted launch

On the learner's launch action, SWEEP creates a local attempt, then performs an
authenticated request only when the settings above are present:

```http
POST https://pln.ng/api/cbt/candidates
Authorization: Bearer <workspace API key>
Content-Type: application/json
```

```json
{
  "examId": "<Course.paralearn_assessment_id>",
  "candidateName": "<learner display name>",
  "studentId": "<stable SWEEP learner UUID>",
  "externalAttemptId": "<SWEEP assessment-attempt UUID>",
  "email": "<learner email>",
  "metadata": {
    "sweepLearnerId": "<stable SWEEP learner UUID>",
    "sweepAttemptId": "<SWEEP assessment-attempt UUID>"
  }
}
```

SWEEP deliberately omits `candidatePin`; ParaLearn generates it. The provider
returns candidate `id` and `launchUrl`. SWEEP validates that the URL is HTTPS
and hosted by an allow-listed ParaLearn host, records only the candidate ID,
then redirects the learner to the returned hosted URL. It never constructs an
SSO URL or persists the candidate PIN.

Launch retry keeps the same local attempt UUID, so ParaLearn can resume or
deduplicate the candidate session using `externalAttemptId`. A failed launch
can be retried without creating another course attempt.

SWEEP never falls back to a manually constructed or raw `/take/<exam-code>`
URL when provisioning is unavailable or fails. Such a launch would omit the
persisted `externalAttemptId` and cannot safely be matched to a signed result,
so it must not complete a course or award a credential. The learner instead
receives a retry action for the saved local attempt.

## Signed final results

Register this endpoint in the ParaLearn workspace:

```text
POST https://<SWEEP host>/courses/paralearn/webhook/
```

SWEEP requires these headers for a completed result:

```http
x-cbt-event: exam.attempt.completed
x-cbt-event-id: evt_…
x-cbt-timestamp: 2026-10-03T07:15:00.000Z
x-cbt-signature: sha256=<HMAC-SHA256 of the exact raw JSON bytes>
```

The signature is checked in constant time against the raw request bytes before
JSON parsing. The signed payload must also contain `event`, `eventId`,
`examId`, `attemptId`, `externalAttemptId`, `studentId`, `status: "SUBMITTED"`,
`percentage`, and `submittedAt`. `eventId` must exactly match the
`x-cbt-event-id` header. `examId`, learner UUID, attempt UUID, and provider
attempt ID are verified against the local attempt before any completion change.

The `x-cbt-event-id` becomes SWEEP's unique event and provider-result key:
identical redeliveries are harmless, while reuse with different raw bytes is
rejected. Candidate PIN, candidate name, and email are removed before the
payload is stored in SWEEP's audit records.

ParaLearn's signed `percentage` is the assessment result. SWEEP applies the
course's published `passing_score` to that verified value, then atomically
updates `CourseProgress` and awards the badge. A local quiz result can never
reach this path.

## Result reconciliation

ParaLearn exposes result slips at:

```text
GET /api/cbt/attempts/{attemptId}/slip
```

The endpoint accepts either ParaLearn's internal `attemptId` or SWEEP's
`externalAttemptId`. SWEEP uses the internal ID when it already knows it and
otherwise uses its local attempt UUID. The documented template is enabled when
workspace credentials are present:

```text
PARALEARN_RESULT_PATH_TEMPLATE=/attempts/{attempt_reference}/slip
```

Result slips are authenticated with the workspace API key and are validated
against the same exam, learner UUID, external attempt UUID, and metadata as a
webhook before they can change a local attempt. They follow these transitions:

| Provider status | SWEEP action |
| --- | --- |
| `IN_PROGRESS` or a `404` slip | Keep the attempt pending; never award completion or a badge. |
| `SUBMITTED` | Verify the provider percentage, then apply the course's published passing score and award only if it passes. |
| `DISQUALIFIED` | Store an immutable terminal `Disqualified` state for examiner review; never award completion or a badge. |

Result-slip payloads receive the same candidate PIN, name, and email redaction
as webhooks. A later signed webhook for an already reconciled identical result
is retained for audit without repeating completion or badge work.

## Operational checklist

1. Create or select each ParaLearn exam and put its `examId` in the matching
   SWEEP course's `paralearn_assessment_id`.
2. Put the workspace key and webhook secret in the deployment secret manager.
3. Configure the exact base URL, launch-host allow list, and webhook URL above.
4. Send a non-production, correctly signed completion payload and confirm one
   completion and one badge are recorded.
5. Keep the integration disabled whenever workspace credentials or signing
   details are unavailable.
