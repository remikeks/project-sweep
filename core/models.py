from django.db import models

# Cycled through by order, same pattern as schools.models.SCHOOL_ACCENTS —
# used for the initials-avatar gradient when no photo has been uploaded yet.
TEAM_ACCENTS = ["leaf", "moss", "fern", "sage", "pine"]


class TeamMember(models.Model):
    """A person shown on the public 'Our Team' page."""

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, blank=True, help_text='Job title or role, e.g. "Executive Director".')
    bio = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to="team_photos/",
        blank=True,
        null=True,
        help_text="Shown on the Our Team page. A square photo (roughly 600\u00d7600px) "
        "works best \u2014 it gets cropped to fit. Until a photo is uploaded, this "
        "person's initials are shown instead.",
    )
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this person from the public Our Team page without deleting their record.",
    )

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        letters = "".join(part[0] for part in self.name.split()[:2] if part)
        return letters.upper() or "?"

    @property
    def accent(self):
        """A CSS accent-tone name for this person's fallback avatar, cycling through a fixed set."""
        return TEAM_ACCENTS[self.order % len(TEAM_ACCENTS)]

    @property
    def photo_available(self):
        """
        Whether a photo is both set AND actually present in storage — see
        schools.models.School.poster_available for why this checks
        existence rather than just whether the field is non-empty.
        """
        return bool(self.photo) and self.photo.storage.exists(self.photo.name)


class Resource(models.Model):
    """A downloadable file shown on the public 'Resources' page (guides, toolkits, etc.)."""

    title = models.CharField(max_length=200)
    caption = models.CharField(
        max_length=300,
        blank=True,
        help_text="Short line shown under the title on the Resources page, e.g. a call to action.",
    )
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="resources/")
    cover_image = models.ImageField(upload_to="resource_covers/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this resource from the public Resources page without deleting it.",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-uploaded_at"]

    def __str__(self):
        return self.title

    @property
    def file_available(self):
        return bool(self.file) and self.file.storage.exists(self.file.name)

    @property
    def cover_available(self):
        return bool(self.cover_image) and self.cover_image.storage.exists(self.cover_image.name)
