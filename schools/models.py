from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# A rotating set of emblem glyphs + accent tones used on school cards.
# Cycled by `order`, so this scales automatically to any number of schools
# (not just the current 10) without needing an uploaded icon per school.
SCHOOL_EMBLEMS = ["\U0001F91D", "\U0001F9E0", "\U0001F33F", "\U0001F333", "\U0001F3DB",
                   "\U0001F3E5", "\U0001F392", "\u2696\uFE0F", "\U0001F32A\uFE0F", "\U0001F4DC"]
SCHOOL_ACCENTS = ["leaf", "moss", "fern", "sage", "pine"]


class School(models.Model):
    """
    One of the 10 'schools' offered on SWEEP (e.g. School of Child &
    Family Welfare, School of Mental Health Practice, etc). A school is a
    themed collection of courses. Enrolling in a school enrolls the user
    in every active course it offers, and finishing every course unlocks
    a certification exam for the school itself.
    """

    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to="school_icons/", blank=True, null=True)

    # Certification exam configuration
    passing_score = models.PositiveSmallIntegerField(
        default=70,
        help_text="Minimum percentage score required to pass the school's "
        "certification exam.",
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("school_detail", kwargs={"slug": self.slug})

    @property
    def active_courses(self):
        return self.courses.filter(is_active=True).order_by("order")

    @property
    def course_count(self):
        return self.active_courses.count()

    @property
    def total_estimated_minutes(self):
        return sum(self.active_courses.values_list("estimated_minutes", flat=True))

    @property
    def exam_question_count(self):
        return self.exam_questions.count()

    @property
    def emblem(self):
        """A glyph for this school's card, cycling through a fixed set."""
        return SCHOOL_EMBLEMS[self.order % len(SCHOOL_EMBLEMS)]

    @property
    def accent(self):
        """A CSS accent-tone name for this school's card, cycling through a fixed set."""
        return SCHOOL_ACCENTS[self.order % len(SCHOOL_ACCENTS)]


class SchoolExamQuestion(models.Model):
    """A multiple-choice question in a school's certification exam."""

    school = models.ForeignKey(School, related_name="exam_questions", on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]


class SchoolExamChoice(models.Model):
    """An answer option for a SchoolExamQuestion."""

    question = models.ForeignKey(
        SchoolExamQuestion, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text
