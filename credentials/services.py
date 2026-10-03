from django.db import transaction
from django.utils import timezone

from .models import Badge, Certificate


def _holder_name(user):
    return (user.get_full_name() or user.get_username()).strip()


def award_badge(user, course, *, verified_attempt):
    """
    Create (or fetch) a badge only for a verified ParaLearn result. Returns
    ``(badge, created)``.

    Note: this no longer renders or saves PNG/PDF files to disk. The
    artwork is generated on demand, at request time, by the badge_png /
    badge_pdf views (see credentials/views.py + generator.py) — this
    function's only job is to record that the badge was earned so it shows up
    on the user's "My badges & certificates" page. The explicit verified
    attempt guard makes it impossible for a local quiz score or arbitrary
    service caller to award a new badge.
    """
    if (
        verified_attempt.user_id != user.id
        or verified_attempt.course_id != course.id
        or not verified_attempt.passed
        or verified_attempt.result_verified_at is None
    ):
        raise ValueError("A badge requires a verified passing ParaLearn assessment attempt.")
    badge, created = Badge.objects.get_or_create(
        user=user,
        course=course,
        status="active",
        defaults={
            "issued_to_name": _holder_name(user),
            "credential_title": f"{course.title} completion badge",
        },
    )
    return badge, created


def award_certificate(user, school):
    """
    Create (or fetch) the certificate record for a user/school pair.
    Returns (certificate, created).

    As with award_badge, artwork is rendered on demand by the
    certificate_png / certificate_pdf views rather than saved to disk here.
    """
    certificate, created = Certificate.objects.get_or_create(
        user=user,
        school=school,
        status="active",
        defaults={
            "issued_to_name": _holder_name(user),
            "credential_title": f"{school.name} certificate of completion",
        },
    )
    return certificate, created


def revoke_credential(credential, *, reason: str):
    """Invalidate an issued credential while retaining its public audit trail."""
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("A revocation reason is required.")
    with transaction.atomic():
        credential.status = "revoked"
        credential.revoked_at = timezone.now()
        credential.revocation_reason = reason[:2000]
        credential.save(update_fields=["status", "revoked_at", "revocation_reason"])
    return credential


def reissue_credential(credential, *, reason: str):
    """Supersede a credential and create one active replacement atomically."""
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("A replacement reason is required.")
    model = type(credential)
    with transaction.atomic():
        credential = model.objects.select_for_update().get(pk=credential.pk)
        if credential.status == "active":
            credential.status = "superseded"
            credential.revoked_at = timezone.now()
            credential.revocation_reason = reason[:2000]
            credential.save(update_fields=["status", "revoked_at", "revocation_reason"])
        fields = {
            "user": credential.user,
            "issued_to_name": credential.issued_to_name or _holder_name(credential.user),
            "credential_title": credential.credential_title,
            "issuer_name": credential.issuer_name,
        }
        if isinstance(credential, Badge):
            fields["course"] = credential.course
        else:
            fields["school"] = credential.school
        replacement = model.objects.create(**fields)
        credential.replaced_by = replacement
        credential.save(update_fields=["replaced_by"])
    return replacement


def get_certificate_score(user, school):
    """Best passing exam score for a user/school pair, or None."""
    from learning.models import SchoolExamAttempt

    best_attempt = (
        SchoolExamAttempt.objects.filter(user=user, school=school, passed=True)
        .order_by("-score")
        .first()
    )
    return best_attempt.score if best_attempt else None
