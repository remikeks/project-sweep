import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from courses.models import Course
from schools.models import School

User = settings.AUTH_USER_MODEL


class Badge(models.Model):
    """Awarded automatically after a verified passing ParaLearn assessment."""

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="badges", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="badges", on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    issued_to_name = models.CharField(max_length=200, blank=True)
    credential_title = models.CharField(max_length=250, blank=True)
    issuer_name = models.CharField(max_length=120, default="SWEEP")
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("revoked", "Revoked"), ("superseded", "Superseded")], default="active")
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)
    replaced_by = models.ForeignKey("self", related_name="replaces", on_delete=models.SET_NULL, null=True, blank=True)
    # Legacy: no longer written to. Artwork is now rendered on demand by
    # credentials/views.py (badge_png/badge_pdf) instead of being saved to
    # disk at award time — see credentials/services.py. Left in place
    # rather than migrated away, since a schema change wasn't needed to
    # fix this and any already-saved files/rows should keep working.
    png_file = models.ImageField(upload_to="badges/png/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="badges/pdf/", blank=True, null=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "course"), condition=Q(status="active"), name="unique_active_badge")]
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"Badge: {self.user} / {self.course}"


class Certificate(models.Model):
    """Awarded automatically when a user passes a school's certification exam."""

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="certificates", on_delete=models.CASCADE)
    school = models.ForeignKey(School, related_name="certificates", on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    issued_to_name = models.CharField(max_length=200, blank=True)
    credential_title = models.CharField(max_length=250, blank=True)
    issuer_name = models.CharField(max_length=120, default="SWEEP")
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("revoked", "Revoked"), ("superseded", "Superseded")], default="active")
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)
    replaced_by = models.ForeignKey("self", related_name="replaces", on_delete=models.SET_NULL, null=True, blank=True)
    # Legacy: no longer written to — see the note on Badge.png_file above.
    png_file = models.ImageField(upload_to="certificates/png/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="certificates/pdf/", blank=True, null=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "school"), condition=Q(status="active"), name="unique_active_certificate")]
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"Certificate: {self.user} / {self.school}"
