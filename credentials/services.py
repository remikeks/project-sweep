from django.core.files.base import ContentFile

from . import generator
from .models import Badge, Certificate


def award_badge(user, course):
    """
    Create (or fetch) the badge for a user/course pair and render its
    PNG + PDF artwork. Returns (badge, created).
    """
    badge, created = Badge.objects.get_or_create(user=user, course=course)

    if created or not badge.png_file or not badge.pdf_file:
        png_bytes, pdf_bytes = generator.generate_badge_files(user, course)
        base_name = f"badge_{user.pk}_{course.pk}"
        badge.png_file.save(f"{base_name}.png", ContentFile(png_bytes), save=False)
        badge.pdf_file.save(f"{base_name}.pdf", ContentFile(pdf_bytes), save=False)
        badge.save()

    return badge, created


def award_certificate(user, school):
    """
    Create (or fetch) the certificate for a user/school pair and render
    its PNG + PDF artwork. Returns (certificate, created).
    """
    from learning.models import SchoolExamAttempt

    certificate, created = Certificate.objects.get_or_create(user=user, school=school)

    if created or not certificate.png_file or not certificate.pdf_file:
        best_attempt = (
            SchoolExamAttempt.objects.filter(user=user, school=school, passed=True)
            .order_by("-score")
            .first()
        )
        score = best_attempt.score if best_attempt else None

        png_bytes, pdf_bytes = generator.generate_certificate_files(user, school, score=score)
        base_name = f"certificate_{user.pk}_{school.pk}"
        certificate.png_file.save(f"{base_name}.png", ContentFile(png_bytes), save=False)
        certificate.pdf_file.save(f"{base_name}.pdf", ContentFile(pdf_bytes), save=False)
        certificate.save()

    return certificate, created
