import uuid

from django.conf import settings
from django.db import models

from courses.models import Course
from schools.models import School

User = settings.AUTH_USER_MODEL


class Badge(models.Model):
    """Awarded automatically when a user passes a course's assessment."""

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="badges", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="badges", on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    png_file = models.ImageField(upload_to="badges/png/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="badges/pdf/", blank=True, null=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"Badge: {self.user} / {self.course}"


class Certificate(models.Model):
    """Awarded automatically when a user passes a school's certification exam."""

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, related_name="certificates", on_delete=models.CASCADE)
    school = models.ForeignKey(School, related_name="certificates", on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    png_file = models.ImageField(upload_to="certificates/png/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="certificates/pdf/", blank=True, null=True)

    class Meta:
        unique_together = ("user", "school")
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"Certificate: {self.user} / {self.school}"
