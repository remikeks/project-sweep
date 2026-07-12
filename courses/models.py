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
    content = models.TextField(
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
