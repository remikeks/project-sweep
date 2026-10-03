from django.conf import settings
import uuid

from django.db import models
from django.db.models import Q

from courses.models import Course, CourseModule
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


class SchoolCurriculumRequirement(models.Model):
    """An immutable course requirement for one learner's school cohort."""

    school_enrollment = models.ForeignKey(
        SchoolEnrollment, related_name="curriculum_requirements", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="school_curriculum_requirements", on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=("school_enrollment", "course"), name="unique_school_curriculum_course"),
        ]
        indexes = [models.Index(fields=("school_enrollment", "order"))]

    def __str__(self):
        return f"{self.school_enrollment} / {self.course}"


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


class ModuleProgress(models.Model):
    """One learner's completed step in a sequential course."""

    user = models.ForeignKey(User, related_name="module_progress", on_delete=models.CASCADE)
    module = models.ForeignKey(CourseModule, related_name="progress_records", on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "module"), name="unique_module_progress")]
        indexes = [models.Index(fields=("user", "module"))]

    def __str__(self):
        return f"{self.user} / {self.module}"


class QuizAttempt(models.Model):
    """A legacy, non-authoritative built-in quiz submission.

    Existing records are retained for historical reporting. ParaLearn CBT
    attempts, rather than this model, are the only records that may complete a
    course or award a badge.
    """

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


class CourseAssessmentAttempt(models.Model):
    """A learner's auditable attempt at a provider-authoritative assessment.

    ``id`` is passed to ParaLearn as SWEEP's opaque attempt reference. The
    provider's own identifiers are stored separately, so retries and signed
    outcomes can be tied back to the exact local learner/course pair.
    """

    class Provider(models.TextChoices):
        PARALEARN = "paralearn", "ParaLearn CBT"

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        LAUNCHED = "launched", "Launched"
        RESULT_PENDING = "result_pending", "Result pending"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        DISQUALIFIED = "disqualified", "Disqualified — examiner review required"
        LAUNCH_FAILED = "launch_failed", "Launch failed"
        RECONCILIATION_FAILED = "reconciliation_failed", "Reconciliation failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="course_assessment_attempts", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="assessment_attempts", on_delete=models.CASCADE)
    provider = models.CharField(max_length=30, choices=Provider.choices, default=Provider.PARALEARN)
    # Retained as a local audit/correlation key. ParaLearn receives ``id`` as
    # ``externalAttemptId`` and uses that stable UUID for relaunch correlation.
    launch_idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    provider_candidate_id = models.CharField(max_length=200, blank=True, null=True)
    provider_attempt_id = models.CharField(max_length=200, blank=True, null=True)
    provider_result_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.CREATED)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)
    launch_count = models.PositiveIntegerField(default=0)
    reconciliation_count = models.PositiveIntegerField(default=0)
    launched_at = models.DateTimeField(null=True, blank=True)
    result_received_at = models.DateTimeField(null=True, blank=True)
    result_verified_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_reconciled_at = models.DateTimeField(null=True, blank=True)
    last_launch_error = models.TextField(blank=True)
    last_reconciliation_error = models.TextField(blank=True)
    result_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("provider", "provider_attempt_id"),
                condition=Q(provider_attempt_id__isnull=False),
                name="unique_provider_assessment_attempt",
            ),
            models.UniqueConstraint(
                fields=("provider", "provider_result_id"),
                condition=Q(provider_result_id__isnull=False),
                name="unique_provider_assessment_result",
            ),
            models.CheckConstraint(
                condition=Q(score__isnull=True) | Q(score__gte=0, score__lte=100),
                name="assessment_attempt_score_in_range",
            ),
        ]

    def __str__(self):
        return f"{self.user} / {self.course} / {self.provider} [{self.status}]"


class ParaLearnLearnerIdentity(models.Model):
    """An opaque, stable UUID exposed to ParaLearn instead of a Django PK."""

    user = models.OneToOneField(
        User,
        related_name="paralearn_identity",
        on_delete=models.CASCADE,
    )
    external_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ParaLearn identity for {self.user}"


class ParaLearnWebhookEvent(models.Model):
    """A verified ParaLearn result event, retained for replay protection/audit."""

    event_id = models.CharField(max_length=200, unique=True)
    attempt = models.ForeignKey(
        CourseAssessmentAttempt,
        related_name="paralearn_events",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    payload_sha256 = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    received_at = models.DateTimeField(auto_now_add=True)
    signature_verified_at = models.DateTimeField()
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self):
        return f"ParaLearn event {self.event_id}"


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
