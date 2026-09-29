from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from schools.models import School


class Course(models.Model):
    """
    A single course within a school. Each course has a difficulty level,
    an estimated time to complete, learning content, and a multiple-choice
    assessment. Passing the assessment marks the course complete and
    awards a badge.
    """

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    school = models.ForeignKey(School, related_name="courses", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField(
        blank=True,
        help_text="A longer descriptive overview of the course shown before enrollment.",
    )
    course_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional alphanumeric course code displayed on the course page.",
    )
    learning_objectives = models.TextField(
        blank=True,
        help_text="What learners will understand or be able to do after completing this course.",
    )
    content = models.TextField(
        blank=True,
        help_text="The main learning material for the course. Supports plain "
        "text/markdown-style paragraphs."
    )
    video_url = models.URLField(blank=True, help_text="Optional supplementary video link.")

    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER
    )
    estimated_minutes = models.PositiveIntegerField(
        default=30, help_text="Estimated time to complete, in minutes."
    )

    passing_score = models.PositiveSmallIntegerField(
        default=70, help_text="Minimum percentage score required to pass the assessment."
    )

    order = models.PositiveSmallIntegerField(
        default=0, help_text="Position of this course within its school."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["school__order", "order", "title"]

    def __str__(self):
        return f"{self.title} ({self.school.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            i = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def is_last_in_school(self):
        last = self.school.active_courses.order_by("-order", "-id").first()
        return last is not None and last.pk == self.pk


class CourseModule(models.Model):
    """A structured learning module belonging to a course."""

    class ModuleType(models.TextChoices):
        VIDEO = "video", "Video"
        ARTICLE = "article", "Article"
        MIXED = "mixed", "Mixed"

    class LearningMode(models.TextChoices):
        SELF_PACED = "self_paced", "Self-paced"
        LIVE = "live", "Live"
        BLENDED = "blended", "Blended"

    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    duration = models.CharField(max_length=50, blank=True, help_text="Example: 15 min")
    module_type = models.CharField(max_length=20, choices=ModuleType.choices, default=ModuleType.ARTICLE)
    learning_mode = models.CharField(
        max_length=20, choices=LearningMode.choices, default=LearningMode.SELF_PACED
    )
    overview = models.TextField(blank=True, help_text="A short summary of the module.")
    content = models.TextField(blank=True, help_text="The full content for this module.")
    module_summary = models.TextField(blank=True, help_text="A recap shown at the end of the module.")
    knowledge_check = models.TextField(blank=True, help_text="Questions or prompts for reflection.")
    practical_activity = models.TextField(blank=True, help_text="A practical exercise for the learner.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} / {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            i = 1
            while CourseModule.objects.filter(course=self.course, slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)


class CourseAsset(models.Model):
    """A versioned learner resource attached to a course or one of its modules.

    Files use Django's configured storage backend. This keeps the domain model
    independent of a storage provider, so Supabase Storage can be introduced
    without changing learner URLs or publishing rules.
    """

    class AssetType(models.TextChoices):
        LEARNER_GUIDE = "learner_guide", "Learner guide"
        SLIDES = "slides", "Slide deck"
        VIDEO = "video", "Video"
        TRANSCRIPT = "transcript", "Transcript"
        WORKSHEET = "worksheet", "Worksheet"
        REFERENCE = "reference", "Reference"

    class PublicationStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In review"
        APPROVED = "approved", "Approved"
        PUBLISHED = "published", "Published"
        RETIRED = "retired", "Retired"

    course = models.ForeignKey(Course, related_name="assets", on_delete=models.CASCADE)
    module = models.ForeignKey(
        CourseModule, related_name="assets", on_delete=models.CASCADE, null=True, blank=True,
        help_text="Leave blank when the resource applies to the whole course.",
    )
    title = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    file = models.FileField(upload_to="course_assets/%Y/%m/", blank=True)
    external_url = models.URLField(blank=True)
    version = models.CharField(max_length=40, default="1.0")
    language = models.CharField(max_length=20, default="en")
    status = models.CharField(max_length=20, choices=PublicationStatus.choices, default=PublicationStatus.DRAFT)
    order = models.PositiveSmallIntegerField(default=0)
    is_downloadable = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="created_course_assets", on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="reviewed_course_assets", on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="published_course_assets", on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        permissions = [
            ("review_courseasset", "Can approve course assets for publication"),
            ("publish_courseasset", "Can publish and retire course assets"),
            ("bulk_import_courseasset", "Can bulk import course asset metadata"),
        ]

    def __str__(self):
        return f"{self.course.title} / {self.title} (v{self.version})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if bool(self.file) == bool(self.external_url):
            raise ValidationError("Provide exactly one of a file or an external URL.")
        if self.module_id and self.module.course_id != self.course_id:
            raise ValidationError("The selected module must belong to this asset's course.")


class Question(models.Model):
    """A single multiple-choice question in a course's assessment."""

    course = models.ForeignKey(Course, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]


class Choice(models.Model):
    """An answer option for a course assessment Question."""

    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text
