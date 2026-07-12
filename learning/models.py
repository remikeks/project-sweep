from django.conf import settings
from django.db import models

from courses.models import Course
from schools.models import School

User = settings.AUTH_USER_MODEL


class SchoolEnrollment(models.Model):
    """
    Records that a user enrolled in an entire school. Creating this
    automatically enrolls the user in every active course the school
    offers (see learning.services.enroll_in_school).
    """

    user = models.ForeignKey(User, related_name="school_enrollments", on_delete=models.CASCADE)
    school = models.ForeignKey(School, related_name="enrollments", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "school")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user} -> {self.school} (school enrollment)"


class CourseEnrollment(models.Model):
    """Records that a user enrolled in an individual course."""

    user = models.ForeignKey(User, related_name="course_enrollments", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    via_school_enrollment = models.ForeignKey(
        SchoolEnrollment,
        related_name="course_enrollments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Set if this enrollment came from enrolling in the whole school.",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user} -> {self.course}"


class CourseProgress(models.Model):
    """Tracks a user's progress through a single course."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(User, related_name="course_progress", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="progress_records", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    best_score = models.PositiveSmallIntegerField(default=0)
    attempts_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "course")
        verbose_name_plural = "Course progress records"

    def __str__(self):
        return f"{self.user} / {self.course} [{self.status}]"


class QuizAttempt(models.Model):
    """A single attempt at a course's multiple-choice assessment."""

    user = models.ForeignKey(User, related_name="quiz_attempts", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="quiz_attempts", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(help_text="Percentage score, 0-100.")
    passed = models.BooleanField(default=False)
    correct_count = models.PositiveSmallIntegerField(default=0)
    question_count = models.PositiveSmallIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user} / {self.course}: {self.score}% ({'pass' if self.passed else 'fail'})"


class SchoolExamAttempt(models.Model):
    """A single attempt at a school's certification exam."""

    user = models.ForeignKey(User, related_name="school_exam_attempts", on_delete=models.CASCADE)
    school = models.ForeignKey(School, related_name="exam_attempts", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(help_text="Percentage score, 0-100.")
    passed = models.BooleanField(default=False)
    correct_count = models.PositiveSmallIntegerField(default=0)
    question_count = models.PositiveSmallIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user} / {self.school}: {self.score}% ({'pass' if self.passed else 'fail'})"
