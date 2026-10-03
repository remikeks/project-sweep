"""Verified ParaLearn CBT assessment lifecycle and completion rules."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import (
    CourseAssessmentAttempt,
    CourseProgress,
    ParaLearnLearnerIdentity,
    ParaLearnWebhookEvent,
)
from .services import course_modules_complete
from .paralearn import (
    ParaLearnClient,
    ParaLearnError,
    ParaLearnResultNotFoundError,
    payload_sha256,
    result_reconciliation_is_configured,
)


PARALEARN_COMPLETION_EVENT = "exam.attempt.completed"


class AssessmentResultError(ValueError):
    """A signed message was authentic but not a valid ParaLearn final result."""


@dataclass(frozen=True)
class AuthoritativeResult:
    attempt_reference: uuid.UUID
    provider_attempt_id: str
    provider_result_id: str | None
    exam_id: str
    student_id: uuid.UUID
    percentage: Decimal
    score: int
    completed_at: Any


@dataclass(frozen=True)
class ResultSlip:
    """The provider-authenticated state returned by ``/attempts/:id/slip``."""

    status: str
    attempt_reference: uuid.UUID
    provider_attempt_id: str
    exam_id: str
    student_id: uuid.UUID
    final_result: AuthoritativeResult | None


def _text(payload: dict[str, Any], field: str, *, required: bool = True, max_length: int = 200) -> str | None:
    value = payload.get(field)
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > max_length:
        raise AssessmentResultError(f"Result field '{field}' must be a non-empty string.")
    return value.strip()


def _parse_datetime(value: Any, field: str):
    if not isinstance(value, str):
        raise AssessmentResultError(f"Result field '{field}' must be an ISO-8601 timestamp.")
    parsed = parse_datetime(value)
    if parsed is None:
        raise AssessmentResultError(f"Result field '{field}' must be an ISO-8601 timestamp.")
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _parse_uuid(value: str, field: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except (TypeError, ValueError, AttributeError) as exc:
        raise AssessmentResultError(f"Result field '{field}' is not a valid UUID.") from exc


def _parse_percentage(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise AssessmentResultError("Result field 'percentage' must be a number from 0 through 100.")
    try:
        percentage = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AssessmentResultError("Result field 'percentage' must be a number from 0 through 100.") from exc
    if not percentage.is_finite() or not Decimal("0") <= percentage <= Decimal("100"):
        raise AssessmentResultError("Result field 'percentage' must be a number from 0 through 100.")
    return percentage


def _stored_score(percentage: Decimal) -> int:
    return int(percentage.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep result audit facts while never persisting PINs or contact details."""
    secret_fields = {"candidatePin", "candidateName", "email"}
    return {key: value for key, value in payload.items() if key not in secret_fields}


def _parse_correlation(
    payload: dict[str, Any],
    *,
    expected_attempt_id: uuid.UUID | None = None,
) -> tuple[uuid.UUID, uuid.UUID]:
    """Validate the immutable SWEEP-to-ParaLearn identifier mapping."""
    attempt_reference = _parse_uuid(_text(payload, "externalAttemptId"), "externalAttemptId")
    if expected_attempt_id and attempt_reference != expected_attempt_id:
        raise AssessmentResultError("Result belongs to a different SWEEP assessment attempt.")
    student_id_text = _text(payload, "studentId")
    student_id = _parse_uuid(student_id_text, "studentId")

    metadata = payload.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            raise AssessmentResultError("Result field 'metadata' must be a JSON object.")
        mapped_attempt = metadata.get("sweepAttemptId")
        if mapped_attempt is not None and mapped_attempt != str(attempt_reference):
            raise AssessmentResultError("Result metadata does not match its external attempt ID.")
        mapped_learner = metadata.get("sweepLearnerId")
        if mapped_learner is not None and mapped_learner != student_id_text:
            raise AssessmentResultError("Result metadata does not match its learner ID.")
    return attempt_reference, student_id


def parse_authoritative_result(
    payload: dict[str, Any],
    *,
    event_id: str,
    expected_attempt_id: uuid.UUID | None = None,
) -> AuthoritativeResult:
    """Validate ParaLearn's documented ``exam.attempt.completed`` envelope."""
    if not isinstance(payload, dict):
        raise AssessmentResultError("Result body must be a JSON object.")
    if _text(payload, "event") != PARALEARN_COMPLETION_EVENT:
        raise AssessmentResultError("Webhook payload is not a ParaLearn completion event.")
    if _text(payload, "eventId") != event_id:
        raise AssessmentResultError("Webhook event ID does not match its signed payload.")
    _parse_datetime(payload.get("timestamp"), "timestamp")
    if _text(payload, "status") != "SUBMITTED":
        raise AssessmentResultError("Webhook result status must be SUBMITTED.")

    attempt_reference, student_id = _parse_correlation(
        payload, expected_attempt_id=expected_attempt_id
    )

    return AuthoritativeResult(
        attempt_reference=attempt_reference,
        provider_attempt_id=_text(payload, "attemptId"),
        # ParaLearn sends one immutable event ID per completion. It is the
        # stable result identifier in the absence of a separate result ID.
        provider_result_id=event_id,
        exam_id=_text(payload, "examId"),
        student_id=student_id,
        percentage=_parse_percentage(payload.get("percentage")),
        score=_stored_score(_parse_percentage(payload.get("percentage"))),
        completed_at=_parse_datetime(payload.get("submittedAt"), "submittedAt"),
    )


def parse_result_slip(
    payload: dict[str, Any], *, expected_attempt_id: uuid.UUID
) -> ResultSlip:
    """Validate ParaLearn's documented authenticated result-slip response."""
    if not isinstance(payload, dict):
        raise AssessmentResultError("Result slip must be a JSON object.")
    status = _text(payload, "status")
    if status not in {"IN_PROGRESS", "SUBMITTED", "DISQUALIFIED"}:
        raise AssessmentResultError("Result slip has an unsupported status.")
    attempt_reference, student_id = _parse_correlation(
        payload, expected_attempt_id=expected_attempt_id
    )
    provider_attempt_id = _text(payload, "attemptId")
    exam_id = _text(payload, "examId")

    if status == "IN_PROGRESS":
        return ResultSlip(
            status=status,
            attempt_reference=attempt_reference,
            provider_attempt_id=provider_attempt_id,
            exam_id=exam_id,
            student_id=student_id,
            final_result=None,
        )

    if not isinstance(payload.get("isPassed"), bool):
        raise AssessmentResultError("Final result slip field 'isPassed' must be a boolean.")
    if status == "DISQUALIFIED" and payload["isPassed"]:
        raise AssessmentResultError("A disqualified result slip cannot be marked passed.")
    completion_value = payload.get("submittedAt") or payload.get("completedAt")
    completion_field = "submittedAt" if payload.get("submittedAt") else "completedAt"
    percentage = _parse_percentage(payload.get("percentage"))
    return ResultSlip(
        status=status,
        attempt_reference=attempt_reference,
        provider_attempt_id=provider_attempt_id,
        exam_id=exam_id,
        student_id=student_id,
        # Result slips have no event ID. Provider attempt IDs are unique and
        # the local result stays event-ID-free so a later signed webhook can
        # be recorded without manufacturing a provider identifier.
        final_result=AuthoritativeResult(
            attempt_reference=attempt_reference,
            provider_attempt_id=provider_attempt_id,
            provider_result_id=None,
            exam_id=exam_id,
            student_id=student_id,
            percentage=percentage,
            score=_stored_score(percentage),
            completed_at=_parse_datetime(completion_value, completion_field),
        ),
    )


def create_assessment_attempt(*, user, course) -> CourseAssessmentAttempt:
    """Create the local attempt and its opaque, stable ParaLearn learner ID."""
    with transaction.atomic():
        ParaLearnLearnerIdentity.objects.get_or_create(user=user)
        return CourseAssessmentAttempt.objects.create(user=user, course=course)


def _set_launch_failure(attempt_id, message: str) -> CourseAssessmentAttempt:
    with transaction.atomic():
        attempt = CourseAssessmentAttempt.objects.select_for_update().get(pk=attempt_id)
        if attempt.status not in {
            CourseAssessmentAttempt.Status.PASSED,
            CourseAssessmentAttempt.Status.FAILED,
            CourseAssessmentAttempt.Status.DISQUALIFIED,
        }:
            attempt.status = CourseAssessmentAttempt.Status.LAUNCH_FAILED
            attempt.last_launch_error = message[:2000]
            attempt.launch_count += 1
            attempt.save(update_fields=["status", "last_launch_error", "launch_count", "updated_at"])
        return attempt


def launch_assessment_attempt(*, attempt: CourseAssessmentAttempt, client=None):
    """Provision a ParaLearn candidate and redirect to its hosted launch URL."""
    identity, _ = ParaLearnLearnerIdentity.objects.get_or_create(user=attempt.user)
    client = client or ParaLearnClient()
    try:
        launch = client.create_launch(attempt=attempt, learner_identity=identity)
    except ParaLearnError as exc:
        _set_launch_failure(attempt.pk, str(exc))
        raise

    with transaction.atomic():
        locked = CourseAssessmentAttempt.objects.select_for_update().select_related("course").get(pk=attempt.pk)
        if locked.provider_candidate_id and locked.provider_candidate_id != launch.provider_candidate_id:
            locked.status = CourseAssessmentAttempt.Status.LAUNCH_FAILED
            locked.last_launch_error = "ParaLearn returned a different candidate for the same SWEEP attempt."
            locked.launch_count += 1
            locked.save(update_fields=["status", "last_launch_error", "launch_count", "updated_at"])
            raise AssessmentResultError(locked.last_launch_error)

        first_successful_launch = locked.launched_at is None
        locked.provider_candidate_id = launch.provider_candidate_id
        locked.status = CourseAssessmentAttempt.Status.LAUNCHED
        locked.launched_at = locked.launched_at or timezone.now()
        locked.last_launch_error = ""
        locked.launch_count += 1
        locked.save(
            update_fields=[
                "provider_candidate_id", "status", "launched_at", "last_launch_error", "launch_count", "updated_at"
            ]
        )
        if first_successful_launch:
            progress, _ = CourseProgress.objects.select_for_update().get_or_create(user=locked.user, course=locked.course)
            progress.attempts_count += 1
            if progress.status == CourseProgress.Status.NOT_STARTED:
                progress.status = CourseProgress.Status.IN_PROGRESS
                progress.save(update_fields=["attempts_count", "status"])
            else:
                progress.save(update_fields=["attempts_count"])
        return locked, launch.launch_url


def _apply_result(
    *,
    result: AuthoritativeResult,
    payload: dict[str, Any],
    forced_status: str | None = None,
) -> tuple[CourseAssessmentAttempt, bool, bool]:
    """Persist one verified provider result and award a badge exactly once."""
    with transaction.atomic():
        try:
            attempt = (
                CourseAssessmentAttempt.objects.select_for_update()
                .select_related("course", "user")
                .get(pk=result.attempt_reference, provider=CourseAssessmentAttempt.Provider.PARALEARN)
            )
        except CourseAssessmentAttempt.DoesNotExist as exc:
            raise AssessmentResultError("No SWEEP ParaLearn attempt matches this result.") from exc
        if result.exam_id != attempt.course.paralearn_assessment_id:
            raise AssessmentResultError("Result exam identifier does not match the course configuration.")
        try:
            identity = ParaLearnLearnerIdentity.objects.get(user=attempt.user)
        except ParaLearnLearnerIdentity.DoesNotExist as exc:
            raise AssessmentResultError("Result has no mapped SWEEP learner identity.") from exc
        if result.student_id != identity.external_id:
            raise AssessmentResultError("Result learner identifier does not match the assessment owner.")
        if attempt.provider_attempt_id and attempt.provider_attempt_id != result.provider_attempt_id:
            raise AssessmentResultError("Result provider attempt identifier does not match the launched attempt.")
        if CourseAssessmentAttempt.objects.filter(
            provider=CourseAssessmentAttempt.Provider.PARALEARN,
            provider_attempt_id=result.provider_attempt_id,
        ).exclude(pk=attempt.pk).exists():
            raise AssessmentResultError("This ParaLearn provider attempt belongs to another SWEEP attempt.")
        # ParaLearn calculates and signs the percentage. SWEEP applies the
        # course's published pass policy to that verified provider result.
        passed = (
            False
            if forced_status == CourseAssessmentAttempt.Status.DISQUALIFIED
            else result.percentage >= Decimal(str(attempt.course.passing_score))
        )
        final_status = forced_status or (
            CourseAssessmentAttempt.Status.PASSED if passed else CourseAssessmentAttempt.Status.FAILED
        )
        terminal_statuses = {
            CourseAssessmentAttempt.Status.PASSED,
            CourseAssessmentAttempt.Status.FAILED,
            CourseAssessmentAttempt.Status.DISQUALIFIED,
        }
        if attempt.status in terminal_statuses:
            if (
                attempt.provider_attempt_id == result.provider_attempt_id
                and attempt.status == final_status
                and attempt.score == result.score
                and attempt.passed == passed
            ):
                # A result slip can be observed before its eventual signed
                # webhook. Record that webhook's unique event ID, but do not
                # repeat completion or badge work.
                if result.provider_result_id and not attempt.provider_result_id:
                    attempt.provider_result_id = result.provider_result_id
                    attempt.save(update_fields=["provider_result_id", "updated_at"])
                return attempt, False, False
            raise AssessmentResultError("This assessment attempt already has a different authoritative result.")

        if result.provider_result_id and CourseAssessmentAttempt.objects.filter(
            provider=CourseAssessmentAttempt.Provider.PARALEARN,
            provider_result_id=result.provider_result_id,
        ).exclude(pk=attempt.pk).exists():
            raise AssessmentResultError("This ParaLearn result was already applied to another attempt.")

        first_confirmed_provider_attempt = attempt.launched_at is None
        attempt.provider_attempt_id = result.provider_attempt_id
        attempt.provider_result_id = result.provider_result_id
        attempt.status = final_status
        attempt.score = result.score
        attempt.passed = passed
        attempt.launched_at = attempt.launched_at or timezone.now()
        attempt.launch_count = max(attempt.launch_count, 1)
        attempt.result_received_at = timezone.now()
        attempt.result_verified_at = timezone.now()
        attempt.completed_at = result.completed_at
        attempt.result_payload = _redact_payload(payload)
        attempt.last_reconciliation_error = ""
        attempt.save(
            update_fields=[
                "provider_attempt_id", "provider_result_id", "status", "score", "passed", "launched_at", "launch_count",
                "result_received_at", "result_verified_at", "completed_at", "result_payload",
                "last_reconciliation_error", "updated_at",
            ]
        )
        progress, _ = CourseProgress.objects.select_for_update().get_or_create(user=attempt.user, course=attempt.course)
        update_fields = []
        if first_confirmed_provider_attempt:
            progress.attempts_count += 1
            update_fields.append("attempts_count")
        if result.score > progress.best_score:
            progress.best_score = result.score
            update_fields.append("best_score")
        if passed and course_modules_complete(attempt.user, attempt.course) and progress.status != CourseProgress.Status.COMPLETED:
            progress.status = CourseProgress.Status.COMPLETED
            progress.completed_at = result.completed_at
            update_fields.extend(["status", "completed_at"])
        elif not passed and progress.status == CourseProgress.Status.NOT_STARTED:
            progress.status = CourseProgress.Status.IN_PROGRESS
            update_fields.append("status")
        if update_fields:
            progress.save(update_fields=update_fields)

        badge_awarded = False
        if passed and course_modules_complete(attempt.user, attempt.course):
            from credentials.services import award_badge

            _, badge_awarded = award_badge(attempt.user, attempt.course, verified_attempt=attempt)
        return attempt, True, badge_awarded


def process_signed_webhook(
    *,
    payload: dict[str, Any],
    raw_payload: bytes,
    event_id: str,
) -> tuple[ParaLearnWebhookEvent, bool, bool]:
    """Store a verified ParaLearn event exactly once, then apply its result."""
    if not event_id or len(event_id) > 200:
        raise AssessmentResultError("Webhook event ID header is invalid.")
    digest = payload_sha256(raw_payload)
    redacted_payload = _redact_payload(payload)
    try:
        with transaction.atomic():
            event, created = ParaLearnWebhookEvent.objects.get_or_create(
                event_id=event_id,
                defaults={
                    "payload_sha256": digest,
                    "payload": redacted_payload,
                    "signature_verified_at": timezone.now(),
                },
            )
    except IntegrityError:
        event = ParaLearnWebhookEvent.objects.get(event_id=event_id)
        created = False
    if not created:
        if event.payload_sha256 != digest:
            raise AssessmentResultError("Webhook event ID was reused with a different payload.")
        if event.processing_error:
            raise AssessmentResultError(event.processing_error)
        return event, False, False

    try:
        result = parse_authoritative_result(payload, event_id=event_id)
        attempt, result_is_new, badge_awarded = _apply_result(result=result, payload=payload)
    except AssessmentResultError as exc:
        event.processing_error = str(exc)
        event.processed_at = timezone.now()
        event.save(update_fields=["processing_error", "processed_at"])
        raise
    event.attempt = attempt
    event.processed_at = timezone.now()
    event.save(update_fields=["attempt", "processed_at"])
    return event, result_is_new, badge_awarded


def _record_pending_result(
    *,
    attempt: CourseAssessmentAttempt,
    provider_attempt_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> tuple[CourseAssessmentAttempt, bool, bool]:
    """Record a non-final lookup without treating it as a failed assessment."""
    with transaction.atomic():
        locked = CourseAssessmentAttempt.objects.select_for_update().get(pk=attempt.pk)
        terminal_statuses = {
            CourseAssessmentAttempt.Status.PASSED,
            CourseAssessmentAttempt.Status.FAILED,
            CourseAssessmentAttempt.Status.DISQUALIFIED,
        }
        if locked.status in terminal_statuses:
            return locked, False, False
        if provider_attempt_id:
            if locked.provider_attempt_id and locked.provider_attempt_id != provider_attempt_id:
                raise AssessmentResultError("Result provider attempt identifier does not match the launched attempt.")
            if CourseAssessmentAttempt.objects.filter(
                provider=CourseAssessmentAttempt.Provider.PARALEARN,
                provider_attempt_id=provider_attempt_id,
            ).exclude(pk=locked.pk).exists():
                raise AssessmentResultError("This ParaLearn provider attempt belongs to another SWEEP attempt.")
            locked.provider_attempt_id = provider_attempt_id
        locked.status = CourseAssessmentAttempt.Status.RESULT_PENDING
        locked.last_reconciliation_error = ""
        fields = ["provider_attempt_id", "status", "last_reconciliation_error", "updated_at"]
        if payload is not None:
            locked.result_payload = _redact_payload(payload)
            fields.append("result_payload")
        locked.save(update_fields=fields)
        return locked, False, False


def _mark_reconciliation_failure(attempt: CourseAssessmentAttempt, message: str) -> None:
    with transaction.atomic():
        locked = CourseAssessmentAttempt.objects.select_for_update().get(pk=attempt.pk)
        if locked.status not in {
            CourseAssessmentAttempt.Status.PASSED,
            CourseAssessmentAttempt.Status.FAILED,
            CourseAssessmentAttempt.Status.DISQUALIFIED,
        }:
            locked.status = CourseAssessmentAttempt.Status.RECONCILIATION_FAILED
            locked.last_reconciliation_error = message[:2000]
            locked.save(update_fields=["status", "last_reconciliation_error", "updated_at"])


def reconcile_assessment_attempt(*, attempt: CourseAssessmentAttempt, client=None) -> tuple[CourseAssessmentAttempt, bool, bool]:
    """Recover the documented ParaLearn result-slip state for one attempt."""
    if not result_reconciliation_is_configured():
        raise AssessmentResultError("ParaLearn result reconciliation is not configured.")
    if attempt.status in {
        CourseAssessmentAttempt.Status.PASSED,
        CourseAssessmentAttempt.Status.FAILED,
        CourseAssessmentAttempt.Status.DISQUALIFIED,
    }:
        return attempt, False, False
    with transaction.atomic():
        locked = CourseAssessmentAttempt.objects.select_for_update().get(pk=attempt.pk)
        locked.reconciliation_count += 1
        locked.last_reconciled_at = timezone.now()
        locked.last_reconciliation_error = ""
        locked.save(update_fields=["reconciliation_count", "last_reconciled_at", "last_reconciliation_error", "updated_at"])

    client = client or ParaLearnClient()
    try:
        # ParaLearn accepts its internal ID or SWEEP's external attempt UUID.
        # The latter lets SWEEP reconcile a candidate that has launched but has
        # not yet reached the provider's assessment-start endpoint.
        payload = client.fetch_result(
            attempt_reference=attempt.provider_attempt_id or str(attempt.pk)
        )
    except ParaLearnResultNotFoundError:
        return _record_pending_result(attempt=attempt)
    except ParaLearnError as exc:
        _mark_reconciliation_failure(attempt, str(exc))
        raise

    try:
        slip = parse_result_slip(payload, expected_attempt_id=attempt.pk)
        if slip.status == "IN_PROGRESS":
            return _record_pending_result(
                attempt=attempt,
                provider_attempt_id=slip.provider_attempt_id,
                payload=payload,
            )
        if slip.status == "DISQUALIFIED":
            return _apply_result(
                result=slip.final_result,
                payload=payload,
                forced_status=CourseAssessmentAttempt.Status.DISQUALIFIED,
            )
        return _apply_result(result=slip.final_result, payload=payload)
    except (ParaLearnError, AssessmentResultError) as exc:
        _mark_reconciliation_failure(attempt, str(exc))
        raise


def serialise_result_for_log(payload: dict[str, Any]) -> str:
    """Small, safe diagnostic representation for management-command output."""
    return json.dumps({key: payload.get(key) for key in ("eventId", "externalAttemptId", "attemptId", "status")})
