from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from . import generator
from .models import Badge, Certificate
from .services import get_certificate_score


@login_required
def my_credentials(request):
    """Where a user views and downloads all their badges and certificates."""
    badges = Badge.objects.filter(user=request.user).select_related("course", "course__school")
    certificates = Certificate.objects.filter(user=request.user).select_related("school")

    context = {
        "badges": badges,
        "certificates": certificates,
    }
    return render(request, "credentials/credentials_list.html", context)


# --------------------------------------------------------------------------
# On-demand artwork serving.
#
# These views render the PNG/PDF directly into the HTTP response instead of
# reading a file that was saved to disk when the badge/certificate was
# awarded. That sidesteps two problems on Render (and any host with an
# ephemeral or per-instance filesystem):
#   1. A file written by one gunicorn worker/instance may not exist on the
#      instance that later handles the download request.
#   2. Anything written to local disk is wiped on every redeploy.
# Rendering is deterministic (same user + course/school always produces the
# same image) and cheap, so generating it fresh per request is simpler and
# more reliable than trying to keep a persisted copy in sync.
# --------------------------------------------------------------------------

@login_required
def badge_png(request, uid):
    badge = get_object_or_404(
        Badge.objects.select_related("course", "course__school"), uid=uid, user=request.user
    )
    data = generator.render_badge_png_bytes(badge.user, badge.course)
    return HttpResponse(data, content_type="image/png")


@login_required
def badge_pdf(request, uid):
    badge = get_object_or_404(
        Badge.objects.select_related("course", "course__school"), uid=uid, user=request.user
    )
    data = generator.render_badge_pdf_bytes(badge.user, badge.course)
    response = HttpResponse(data, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{badge.course.slug}-badge.pdf"'
    return response


@login_required
def certificate_png(request, uid):
    certificate = get_object_or_404(Certificate.objects.select_related("school"), uid=uid, user=request.user)
    score = get_certificate_score(certificate.user, certificate.school)
    data = generator.render_certificate_png_bytes(certificate.user, certificate.school, score=score, awarded_at=certificate.awarded_at, issued_to_name=certificate.issued_to_name, credential_id=certificate.uid)
    return HttpResponse(data, content_type="image/png")


@login_required
def certificate_pdf(request, uid):
    certificate = get_object_or_404(Certificate.objects.select_related("school"), uid=uid, user=request.user)
    score = get_certificate_score(certificate.user, certificate.school)
    data = generator.render_certificate_pdf_bytes(certificate.user, certificate.school, score=score, awarded_at=certificate.awarded_at, issued_to_name=certificate.issued_to_name, credential_id=certificate.uid)
    response = HttpResponse(data, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{certificate.school.slug}-certificate.pdf"'
    return response


def verify_credential(request, uid):
    """Public verification by high-entropy credential ID; never exposes accounts."""
    badge = Badge.objects.filter(uid=uid).select_related("course", "course__school").first()
    certificate = Certificate.objects.filter(uid=uid).select_related("school").first()
    credential = badge or certificate
    if credential is None:
        return render(request, "credentials/verify.html", {"verified": False}, status=404)
    if badge:
        title = credential.credential_title or f"{credential.course.title} completion badge"
        issuer = credential.issuer_name or credential.course.school.name
    else:
        title = credential.credential_title or f"{credential.school.name} certificate of completion"
        issuer = credential.issuer_name or credential.school.name
    return render(request, "credentials/verify.html", {
        "verified": credential.status == "active", "credential": credential,
        "title": title, "issuer": issuer,
        "holder": credential.issued_to_name or credential.user.get_full_name() or credential.user.get_username(),
    })
