from .models import Badge, Certificate


def award_badge(user, course):
    """
    Create (or fetch) the badge record for a user/course pair. Returns
    (badge, created).

    Note: this no longer renders or saves PNG/PDF files to disk. The
    artwork is generated on demand, at request time, by the badge_png /
    badge_pdf views (see credentials/views.py + generator.py) — this
    function's only job is to record that the badge was earned so it
    shows up on the user's "My badges & certificates" page.
    """
    badge, created = Badge.objects.get_or_create(user=user, course=course)
    return badge, created


def award_certificate(user, school):
    """
    Create (or fetch) the certificate record for a user/school pair.
    Returns (certificate, created).

    As with award_badge, artwork is rendered on demand by the
    certificate_png / certificate_pdf views rather than saved to disk here.
    """
    certificate, created = Certificate.objects.get_or_create(user=user, school=school)
    return certificate, created


def get_certificate_score(user, school):
    """Best passing exam score for a user/school pair, or None."""
    from learning.models import SchoolExamAttempt

    best_attempt = (
        SchoolExamAttempt.objects.filter(user=user, school=school, passed=True)
        .order_by("-score")
        .first()
    )
    return best_attempt.score if best_attempt else None
