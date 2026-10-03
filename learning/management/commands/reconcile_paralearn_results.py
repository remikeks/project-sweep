"""Recover delayed ParaLearn CBT results through the configured provider API."""

from django.core.management.base import BaseCommand, CommandError

from learning.assessment_services import AssessmentResultError, reconcile_assessment_attempt
from learning.models import CourseAssessmentAttempt
from learning.paralearn import ParaLearnError, result_reconciliation_is_configured


class Command(BaseCommand):
    help = "Reconcile pending ParaLearn CBT course-assessment results."

    def add_arguments(self, parser):
        parser.add_argument("--attempt-id", help="Reconcile one SWEEP course-assessment UUID.")
        parser.add_argument("--limit", type=int, default=100, help="Maximum pending attempts to request (default: 100).")

    def handle(self, *args, **options):
        if not result_reconciliation_is_configured():
            raise CommandError(
                "ParaLearn result reconciliation is disabled until workspace credentials are configured."
            )
        if options["limit"] < 1:
            raise CommandError("--limit must be at least 1.")

        attempts = CourseAssessmentAttempt.objects.select_related("course", "user").filter(
            provider=CourseAssessmentAttempt.Provider.PARALEARN,
            status__in=(
                CourseAssessmentAttempt.Status.LAUNCHED,
                CourseAssessmentAttempt.Status.RESULT_PENDING,
                CourseAssessmentAttempt.Status.RECONCILIATION_FAILED,
            ),
        )
        if options["attempt_id"]:
            attempts = attempts.filter(pk=options["attempt_id"])
        attempts = attempts.order_by("created_at")[: options["limit"]]

        processed = applied = failures = 0
        for attempt in attempts:
            processed += 1
            try:
                _, result_is_new, _ = reconcile_assessment_attempt(attempt=attempt)
            except (ParaLearnError, AssessmentResultError) as exc:
                failures += 1
                self.stderr.write(f"{attempt.pk}: {exc}")
            else:
                if result_is_new:
                    applied += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"ParaLearn reconciliation complete: {processed} checked, {applied} result(s) applied, {failures} failure(s)."
            )
        )
