import hashlib
import hmac
import json
from urllib.error import HTTPError

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.test import override_settings
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import timedelta

from courses.models import Choice, ContentUploadIntent, Course, CourseAsset, CourseModule, Question
from learning.assessment_services import create_assessment_attempt
from learning.models import (
    CourseAssessmentAttempt,
    CourseEnrollment,
    CourseProgress,
    ParaLearnLearnerIdentity,
    ParaLearnWebhookEvent,
    QuizAttempt,
)
from learning.paralearn import (
    LaunchResponse,
    ParaLearnClient,
    ParaLearnRequestError,
    ParaLearnResultNotFoundError,
)
from learning.services import enroll_in_course, grade_course_quiz
from credentials.models import Badge
from credentials.services import award_badge
from schools.models import School


class CourseDetailAccessTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Test School", slug="test-school")
        self.course = Course.objects.create(
            school=self.school,
            title="Intro to SWEEP",
            slug="intro-to-sweep",
            summary="A short summary for the course.",
            description="This is a longer course description intended to be visible before enrollment.",
            course_code="CS-101",
            learning_objectives="Learn the basics\nUnderstand the workflow",
            content="This is the full course content that should stay hidden until enrollment.",
        )

    def test_anonymous_user_sees_public_overview_but_not_learning_material(self):
        response = self.client.get(reverse("course_detail", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course Overview")
        self.assertContains(response, "This is a longer course description intended to be visible before enrollment.")
        self.assertContains(response, "CS-101")
        self.assertContains(response, "Learning objectives")
        self.assertNotContains(response, "This is the full course content that should stay hidden until enrollment.")

    def test_course_list_shows_enrolled_status_for_enrolled_courses(self):
        user = get_user_model().objects.create_user(username="student", password="secret123")
        CourseEnrollment.objects.create(user=user, course=self.course)

        self.client.force_login(user)
        response = self.client.get(reverse("course_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enrolled")

    def test_enrollment_redirects_to_the_first_module(self):
        user = get_user_model().objects.create_user(username="student2", password="secret123")
        CourseModule.objects.create(
            course=self.course,
            title="Welcome",
            order=1,
            duration="15 min",
            module_type="video",
            learning_mode="self_paced",
            overview="Intro overview",
            content="Intro content",
            module_summary="Intro summary",
            knowledge_check="What did you learn?",
            practical_activity="Reflect on your learning.",
        )

        self.client.force_login(user)
        response = self.client.post(reverse("enroll_in_course", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("course_module_detail", kwargs={"slug": self.course.slug, "module_order": 1}))

    def test_authenticated_user_can_enroll_and_start_course(self):
        user = get_user_model().objects.create_user(username="student3", password="secret123")
        CourseModule.objects.create(
            course=self.course,
            title="Welcome",
            order=1,
            duration="15 min",
            module_type="article",
            learning_mode="self_paced",
            overview="Intro overview",
            content="Intro content",
            module_summary="Intro summary",
            knowledge_check="What did you learn?",
            practical_activity="Reflect on your learning.",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("course_detail", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enroll and start course")
        self.assertNotContains(response, "Continue course")

    def test_module_content_is_sanitized_before_rendering(self):
        user = get_user_model().objects.create_user(username="student4", password="secret123")
        module = CourseModule.objects.create(
            course=self.course,
            title="Safe lesson",
            order=1,
            content="# Lesson\n<script>alert('unsafe')</script>\nSafe paragraph.",
        )
        enroll_in_course(user, self.course)
        self.client.force_login(user)

        response = self.client.get(
            reverse("course_module_detail", kwargs={"slug": self.course.slug, "module_order": module.order})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Safe paragraph.")
        self.assertNotIn("<script", str(response.context["module_content_html"]))


class ContentWorkflowApiTests(TestCase):
    def setUp(self):
        school = School.objects.create(name="Content School", slug="content-school")
        self.course = Course.objects.create(school=school, title="Content Course", slug="content-course")
        self.module = CourseModule.objects.create(course=self.course, title="Content lesson", order=1)
        self.user = get_user_model().objects.create_superuser(
            username="content-admin", password="secret123", email="admin@example.com"
        )
        self.client.force_login(self.user)

    def test_staff_can_create_and_publish_an_external_asset(self):
        payload = {
            "course_slug": self.course.slug,
            "module_order": self.module.order,
            "title": "Learner guide",
            "asset_type": "learner_guide",
            "external_url": "https://assets.example.test/guide.pdf",
        }
        response = self.client.post(reverse("create_course_asset"), data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        asset = CourseAsset.objects.get(title="Learner guide")
        self.assertEqual(asset.status, CourseAsset.PublicationStatus.DRAFT)

        for action in ("submit", "approve", "publish"):
            response = self.client.post(reverse("transition_course_asset", kwargs={"asset_id": asset.id, "action": action}))
            self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, CourseAsset.PublicationStatus.PUBLISHED)
        self.assertEqual(asset.published_by, self.user)

    def test_non_staff_cannot_register_content(self):
        learner = get_user_model().objects.create_user(username="learner", password="secret123")
        self.client.force_login(learner)
        response = self.client.post(reverse("create_course_asset"), data={}, content_type="application/json")
        self.assertEqual(response.status_code, 403)


class ContentPortalApiTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Portal School", slug="portal-school")
        self.course = Course.objects.create(school=self.school, title="Portal course", slug="portal-course")
        self.module = CourseModule.objects.create(course=self.course, title="Portal lesson", order=1)
        self.author = get_user_model().objects.create_user(username="author", password="secret123")
        self.reviewer = get_user_model().objects.create_user(username="reviewer", password="secret123")
        self.publisher = get_user_model().objects.create_user(username="publisher", password="secret123")
        self._grant(self.author, "add_courseasset", "change_courseasset", "view_courseasset")
        self._grant(self.reviewer, "view_courseasset", "review_courseasset")
        self._grant(self.publisher, "view_courseasset", "publish_courseasset", "bulk_import_courseasset")

    @staticmethod
    def _grant(user, *codenames):
        user.user_permissions.add(*Permission.objects.filter(content_type__app_label="courses", codename__in=codenames))

    def _external_payload(self, **overrides):
        payload = {
            "course_slug": self.course.slug,
            "module_order": self.module.order,
            "title": "Approved guide",
            "asset_type": "learner_guide",
            "external_url": "https://assets.example.test/approved-guide.pdf",
            "version": "1.0",
            "language": "en",
            "order": 0,
            "is_downloadable": True,
        }
        payload.update(overrides)
        return payload

    def test_author_can_submit_only_their_own_draft_and_reviewer_approves(self):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("create_course_asset"), data=self._external_payload(), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        asset = CourseAsset.objects.get(title="Approved guide")
        response = self.client.post(reverse("transition_course_asset", kwargs={"asset_id": asset.id, "action": "submit"}))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.reviewer)
        response = self.client.post(reverse("transition_course_asset", kwargs={"asset_id": asset.id, "action": "approve"}))
        self.assertEqual(response.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, CourseAsset.PublicationStatus.APPROVED)
        self.assertEqual(asset.reviewed_by, self.reviewer)

    def test_bulk_import_is_atomic_when_one_row_is_invalid(self):
        self.client.force_login(self.publisher)
        response = self.client.post(
            reverse("import_course_assets"),
            data={"assets": [self._external_payload(title="valid"), self._external_payload(title="invalid", course_slug="missing-course")]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CourseAsset.objects.count(), 0)

    def test_content_workspace_is_available_to_users_with_catalog_access(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse("content_portal"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course asset workspace")
        self.assertContains(response, self.course.title)

    def test_learner_download_requires_enrollment_and_published_status(self):
        asset = CourseAsset.objects.create(
            course=self.course,
            module=self.module,
            title="Published guide",
            asset_type="learner_guide",
            external_url="https://assets.example.test/published-guide.pdf",
            status=CourseAsset.PublicationStatus.PUBLISHED,
        )
        learner = get_user_model().objects.create_user(username="portal-learner", password="secret123")
        self.client.force_login(learner)
        response = self.client.get(reverse("course_asset_download", kwargs={"asset_id": asset.id}))
        self.assertRedirects(response, reverse("course_detail", kwargs={"slug": self.course.slug}))
        CourseEnrollment.objects.create(user=learner, course=self.course)
        response = self.client.get(reverse("course_asset_download", kwargs={"asset_id": asset.id}))
        self.assertRedirects(response, asset.external_url, fetch_redirect_response=False)

    @override_settings(
        SUPABASE_URL="https://project.supabase.co",
        SUPABASE_STORAGE_BUCKET="sweep-course-assets",
        SUPABASE_SERVICE_ROLE_KEY="server-only-test-key",
    )
    @patch("courses.content_api.SupabaseStorageClient")
    def test_signed_upload_is_bound_to_one_author_and_consumed_on_registration(self, storage_client):
        storage_client.return_value.create_signed_upload_url.return_value = SimpleNamespace(
            url="https://project.supabase.co/storage/v1/object/upload/sign/sweep-course-assets/path?token=one-use",
            storage_path="courses/portal-course/module-1/a-guide.pdf",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("create_content_upload_intent"),
            data={
                "course_slug": self.course.slug,
                "module_order": self.module.order,
                "asset_type": "learner_guide",
                "filename": "guide.pdf",
                "content_type": "application/pdf",
                "size_bytes": 1024,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        intent = ContentUploadIntent.objects.get()
        self.assertIsNone(intent.consumed_at)
        response = self.client.post(
            reverse("create_course_asset"),
            data=self._external_payload(upload_intent_id=str(intent.id)),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        intent.refresh_from_db()
        self.assertIsNotNone(intent.consumed_at)
        asset = CourseAsset.objects.get()
        self.assertEqual(asset.storage_path, intent.storage_path)
        self.assertEqual(asset.original_filename, "guide.pdf")

    @override_settings(
        SUPABASE_JWT_ISSUER="https://project.supabase.co/auth/v1",
        SUPABASE_JWT_AUDIENCE="authenticated",
        SUPABASE_JWKS_URL="https://project.supabase.co/auth/v1/.well-known/jwks.json",
        SUPABASE_JWT_ALGORITHMS=("RS256",),
        SUPABASE_JWT_PERMISSION_CLAIM="app_metadata.sweep_permissions",
        SUPABASE_JWT_ROLE_CLAIM="",
        SUPABASE_JWT_ROLE_MAP={},
    )
    @patch("courses.content_auth.SupabaseJWTVerifier.verify")
    def test_verified_supabase_claims_map_to_sweep_permissions(self, verify):
        verify.return_value = {
            "sub": "9bc2d075-2d28-4e80-9108-c30bde0cf57f",
            "email": "author@example.test",
            "role": "authenticated",
            "app_metadata": {"sweep_permissions": ["courses.add_courseasset"]},
        }
        response = self.client.post(
            reverse("create_course_asset"),
            data=self._external_payload(),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer header.payload.signature",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CourseAsset.objects.filter(created_by__username__startswith="supabase-").exists())


@override_settings(
    PARALEARN_API_BASE_URL="https://pln.ng/api/cbt",
    PARALEARN_API_KEY="test-key",
    PARALEARN_API_KEY_HEADER="Authorization",
    PARALEARN_API_KEY_PREFIX="Bearer ",
    PARALEARN_CANDIDATE_PROVISION_PATH="/candidates",
    PARALEARN_RESULT_PATH_TEMPLATE="/attempts/{attempt_reference}/slip",
    PARALEARN_ALLOWED_LAUNCH_HOSTS=("pln.ng",),
    PARALEARN_WEBHOOK_SIGNING_SECRET="test-webhook-secret",
    PARALEARN_WEBHOOK_SIGNATURE_HEADER="x-cbt-signature",
    PARALEARN_WEBHOOK_SIGNATURE_ALGORITHM="hmac-sha256",
    PARALEARN_WEBHOOK_EVENT_HEADER="x-cbt-event",
    PARALEARN_WEBHOOK_EVENT_ID_HEADER="x-cbt-event-id",
    PARALEARN_WEBHOOK_TIMESTAMP_HEADER="x-cbt-timestamp",
)
class ParaLearnAssessmentTests(TestCase):
    """The provider is mocked: no test contacts a real ParaLearn endpoint."""

    def setUp(self):
        self.school = School.objects.create(name="Assessment School", slug="assessment-school")
        self.course = Course.objects.create(
            school=self.school,
            title="Authoritative assessment course",
            slug="authoritative-assessment-course",
            paralearn_assessment_id="pl-course-101",
            # The signed provider percentage is authoritative; this is SWEEP's
            # published completion policy for that verified result.
            passing_score=90,
        )
        self.user = get_user_model().objects.create_user(
            username="assessment-learner", email="learner@example.test", password="secret123"
        )
        enroll_in_course(self.user, self.course)
        self.client.force_login(self.user)

    def _result_payload(self, attempt, **overrides):
        identity = ParaLearnLearnerIdentity.objects.get(user=self.user)
        payload = {
            "event": "exam.attempt.completed",
            "eventId": "evt-001",
            "timestamp": "2026-10-03T07:15:00.000Z",
            "workspaceId": "ws-sweep-test",
            "examId": self.course.paralearn_assessment_id,
            "examCode": "SWEEP-101",
            "attemptId": "provider-attempt-001",
            "externalAttemptId": str(attempt.pk),
            "studentId": str(identity.external_id),
            "candidateName": "Assessment Learner",
            "candidatePin": "849201",
            "email": self.user.email,
            "status": "SUBMITTED",
            "score": 38.0,
            "totalMarks": 40.0,
            "percentage": 95.0,
            "grade": "A1",
            "startedAt": "2026-10-03T06:35:00.000Z",
            "submittedAt": "2026-10-03T07:15:00.000Z",
            "resultSlip": {
                "durationMins": 40,
                "violations": 0,
                "breakdown": {
                    "totalQuestions": 40,
                    "correctCount": 38,
                    "wrongCount": 2,
                    "mcqScore": 38.0,
                    "essayScore": 0.0,
                },
            },
            "metadata": {
                "sweepLearnerId": str(identity.external_id),
                "sweepAttemptId": str(attempt.pk),
            },
        }
        payload.update(overrides)
        return payload

    def _result_slip(self, attempt, **overrides):
        identity = ParaLearnLearnerIdentity.objects.get(user=self.user)
        payload = {
            "attemptId": "provider-attempt-001",
            "externalAttemptId": str(attempt.pk),
            "studentId": str(identity.external_id),
            "examId": self.course.paralearn_assessment_id,
            "examCode": "SWEEP-101",
            "examTitle": "SWEEP assessment",
            "candidateName": "Assessment Learner",
            "candidatePin": "849201",
            "email": self.user.email,
            "status": "SUBMITTED",
            "score": 38.0,
            "totalMarks": 40.0,
            "percentage": 95.0,
            "grade": "A1",
            "isPassed": True,
            "durationMins": 40,
            "timeSpentMins": 38,
            "violations": 0,
            "startedAt": "2026-10-03T06:35:00.000Z",
            "submittedAt": "2026-10-03T07:13:00.000Z",
            "completedAt": "2026-10-03T07:13:00.000Z",
            "resultSlip": {
                "durationMins": 40,
                "violations": 0,
                "breakdown": {
                    "totalQuestions": 40,
                    "correctCount": 38,
                    "wrongCount": 2,
                    "mcqScore": 38.0,
                    "essayScore": 0.0,
                },
            },
            "metadata": {
                "sweepLearnerId": str(identity.external_id),
                "sweepAttemptId": str(attempt.pk),
            },
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def _signature(raw_payload):
        digest = hmac.new(b"test-webhook-secret", raw_payload, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def _post_signed_webhook(self, payload):
        raw_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return self.client.post(
            reverse("paralearn_result_webhook"),
            data=raw_payload,
            content_type="application/json",
            HTTP_X_CBT_SIGNATURE=self._signature(raw_payload),
            HTTP_X_CBT_EVENT="exam.attempt.completed",
            HTTP_X_CBT_EVENT_ID=payload["eventId"],
            HTTP_X_CBT_TIMESTAMP=payload["timestamp"],
        )

    @patch("learning.assessment_services.ParaLearnClient.create_launch")
    def test_launch_provisions_candidate_and_starts_progress_once(self, create_launch):
        create_launch.return_value = LaunchResponse(
            provider_candidate_id="cand-001",
            launch_url="https://pln.ng/take/SWEEP-101?pin=849201",
        )

        response = self.client.post(reverse("paralearn_launch", kwargs={"slug": self.course.slug}))

        self.assertRedirects(response, "https://pln.ng/take/SWEEP-101?pin=849201", fetch_redirect_response=False)
        attempt = CourseAssessmentAttempt.objects.get()
        self.assertEqual(attempt.status, CourseAssessmentAttempt.Status.LAUNCHED)
        self.assertEqual(attempt.provider_candidate_id, "cand-001")
        self.assertIsNone(attempt.provider_attempt_id)
        self.assertEqual(attempt.launch_count, 1)
        progress = CourseProgress.objects.get(user=self.user, course=self.course)
        self.assertEqual(progress.status, CourseProgress.Status.IN_PROGRESS)
        self.assertEqual(progress.attempts_count, 1)

    @patch("learning.assessment_services.ParaLearnClient.create_launch")
    def test_retry_reuses_local_attempt_and_idempotency_key(self, create_launch):
        create_launch.side_effect = ParaLearnRequestError("temporary provider outage")
        response = self.client.post(reverse("paralearn_launch", kwargs={"slug": self.course.slug}))
        self.assertEqual(response.status_code, 503)
        attempt = CourseAssessmentAttempt.objects.get()
        original_key = attempt.launch_idempotency_key
        self.assertEqual(attempt.status, CourseAssessmentAttempt.Status.LAUNCH_FAILED)

        create_launch.side_effect = None
        create_launch.return_value = LaunchResponse(
            provider_candidate_id="cand-001",
            launch_url="https://pln.ng/take/SWEEP-101?pin=849201",
        )
        response = self.client.post(reverse("paralearn_retry_launch", kwargs={"attempt_id": attempt.pk}))

        self.assertRedirects(response, "https://pln.ng/take/SWEEP-101?pin=849201", fetch_redirect_response=False)
        attempt.refresh_from_db()
        self.assertEqual(attempt.launch_idempotency_key, original_key)
        self.assertEqual(attempt.launch_count, 2)
        self.assertEqual(CourseAssessmentAttempt.objects.count(), 1)

    def test_valid_signed_pass_completes_course_and_awards_badge_once(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        response = self._post_signed_webhook(self._result_payload(attempt))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "event_id": "evt-001", "duplicate": False, "result_applied": True, "badge_awarded": True,
        })
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, CourseAssessmentAttempt.Status.PASSED)
        self.assertTrue(attempt.passed)
        self.assertIsNotNone(attempt.result_verified_at)
        self.assertEqual(attempt.score, 95)
        self.assertEqual(attempt.provider_attempt_id, "provider-attempt-001")
        self.assertNotIn("candidatePin", attempt.result_payload)
        self.assertNotIn("candidateName", attempt.result_payload)
        self.assertNotIn("email", attempt.result_payload)
        event = ParaLearnWebhookEvent.objects.get(event_id="evt-001")
        self.assertNotIn("candidatePin", event.payload)
        self.assertNotIn("candidateName", event.payload)
        self.assertNotIn("email", event.payload)
        progress = CourseProgress.objects.get(user=self.user, course=self.course)
        self.assertEqual(progress.status, CourseProgress.Status.COMPLETED)
        self.assertEqual(progress.best_score, 95)
        self.assertEqual(progress.attempts_count, 1)
        self.assertEqual(Badge.objects.filter(user=self.user, course=self.course).count(), 1)
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 1)

    def test_event_id_reuse_with_a_different_signed_body_is_rejected(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        self.assertEqual(self._post_signed_webhook(self._result_payload(attempt)).status_code, 200)

        response = self._post_signed_webhook(self._result_payload(attempt, percentage=94.0))

        self.assertEqual(response.status_code, 422)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 95)
        self.assertEqual(Badge.objects.filter(user=self.user, course=self.course).count(), 1)
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 1)

        duplicate = self._post_signed_webhook(self._result_payload(attempt))
        self.assertEqual(duplicate.status_code, 200)
        self.assertJSONEqual(duplicate.content, {
            "event_id": "evt-001", "duplicate": True, "result_applied": False, "badge_awarded": False,
        })
        self.assertEqual(Badge.objects.filter(user=self.user, course=self.course).count(), 1)
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 1)

    def test_invalid_signature_does_not_record_event_or_complete_course(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        payload = self._result_payload(attempt)
        response = self.client.post(
            reverse("paralearn_result_webhook"),
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CBT_SIGNATURE="not-a-valid-signature",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 0)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())
        self.assertEqual(CourseProgress.objects.get(user=self.user, course=self.course).status, CourseProgress.Status.NOT_STARTED)

    def test_signed_event_with_mismatched_header_timestamp_is_rejected_before_audit(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        payload = self._result_payload(attempt)
        raw_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")

        response = self.client.post(
            reverse("paralearn_result_webhook"),
            data=raw_payload,
            content_type="application/json",
            HTTP_X_CBT_SIGNATURE=self._signature(raw_payload),
            HTTP_X_CBT_EVENT="exam.attempt.completed",
            HTTP_X_CBT_EVENT_ID=payload["eventId"],
            HTTP_X_CBT_TIMESTAMP="2026-10-03T07:16:00.000Z",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 0)

    def test_invalid_signed_event_remains_rejected_on_an_identical_redelivery(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        invalid_payload = self._result_payload(attempt, examId="wrong-ParaLearn-course")

        first = self._post_signed_webhook(invalid_payload)
        repeated = self._post_signed_webhook(invalid_payload)

        self.assertEqual(first.status_code, 422)
        self.assertEqual(repeated.status_code, 422)
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 1)

    @override_settings(PARALEARN_WEBHOOK_SIGNING_SECRET="")
    def test_webhook_is_fail_closed_without_the_workspace_signing_secret(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        response = self._post_signed_webhook(self._result_payload(attempt))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 0)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())

    def test_signed_mismatched_result_is_audited_but_never_awards(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        response = self._post_signed_webhook(
            self._result_payload(attempt, examId="wrong-ParaLearn-course")
        )

        self.assertEqual(response.status_code, 422)
        event = ParaLearnWebhookEvent.objects.get(event_id="evt-001")
        self.assertIn("does not match", event.processing_error)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())
        self.assertEqual(CourseProgress.objects.get(user=self.user, course=self.course).status, CourseProgress.Status.NOT_STARTED)

    def test_signed_result_with_an_invalid_percentage_is_audited_but_never_awards(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        response = self._post_signed_webhook(self._result_payload(attempt, percentage="NaN"))

        self.assertEqual(response.status_code, 422)
        event = ParaLearnWebhookEvent.objects.get(event_id="evt-001")
        self.assertIn("percentage", event.processing_error)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())

    def test_signed_result_with_inconsistent_learner_metadata_is_audited_but_never_awards(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        response = self._post_signed_webhook(
            self._result_payload(attempt, studentId="b85e9ef4-93fc-430a-a8bd-565f56f3d6bc")
        )

        self.assertEqual(response.status_code, 422)
        event = ParaLearnWebhookEvent.objects.get(event_id="evt-001")
        self.assertIn("learner ID", event.processing_error)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())

    def test_signed_result_for_a_different_learner_is_audited_but_never_awards(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        other_learner_id = "b85e9ef4-93fc-430a-a8bd-565f56f3d6bc"
        response = self._post_signed_webhook(
            self._result_payload(
                attempt,
                studentId=other_learner_id,
                metadata={
                    "sweepLearnerId": other_learner_id,
                    "sweepAttemptId": str(attempt.pk),
                },
            )
        )

        self.assertEqual(response.status_code, 422)
        event = ParaLearnWebhookEvent.objects.get(event_id="evt-001")
        self.assertIn("learner identifier", event.processing_error)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())

    @patch("learning.assessment_services.ParaLearnClient.fetch_result")
    def test_reconciliation_uses_authenticated_provider_result_and_awards_badge(self, fetch_result):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        attempt.provider_attempt_id = "provider-attempt-001"
        attempt.status = CourseAssessmentAttempt.Status.LAUNCHED
        attempt.save(update_fields=["provider_attempt_id", "status"])
        fetch_result.return_value = self._result_slip(attempt)

        response = self.client.post(reverse("paralearn_reconcile_result", kwargs={"attempt_id": attempt.pk}))

        self.assertRedirects(response, reverse("course_detail", kwargs={"slug": self.course.slug}))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, CourseAssessmentAttempt.Status.PASSED)
        self.assertEqual(attempt.reconciliation_count, 1)
        self.assertTrue(Badge.objects.filter(user=self.user, course=self.course).exists())
        self.assertEqual(ParaLearnWebhookEvent.objects.count(), 0)
        fetch_result.assert_called_once_with(attempt_reference="provider-attempt-001")

        webhook = self._post_signed_webhook(self._result_payload(attempt))
        self.assertEqual(webhook.status_code, 200)
        self.assertJSONEqual(webhook.content, {
            "event_id": "evt-001", "duplicate": True, "result_applied": False, "badge_awarded": False,
        })
        attempt.refresh_from_db()
        self.assertEqual(attempt.provider_result_id, "evt-001")
        self.assertEqual(Badge.objects.filter(user=self.user, course=self.course).count(), 1)

    @patch("learning.assessment_services.ParaLearnClient.fetch_result")
    def test_in_progress_slip_uses_external_attempt_id_and_stays_pending(self, fetch_result):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        fetch_result.return_value = self._result_slip(
            attempt,
            status="IN_PROGRESS",
            submittedAt=None,
            completedAt=None,
        )

        response = self.client.post(reverse("paralearn_reconcile_result", kwargs={"attempt_id": attempt.pk}))

        self.assertRedirects(response, reverse("course_detail", kwargs={"slug": self.course.slug}))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, CourseAssessmentAttempt.Status.RESULT_PENDING)
        self.assertEqual(attempt.provider_attempt_id, "provider-attempt-001")
        self.assertIsNone(attempt.result_verified_at)
        self.assertNotIn("candidatePin", attempt.result_payload)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())
        fetch_result.assert_called_once_with(attempt_reference=str(attempt.pk))

    @patch("learning.assessment_services.ParaLearnClient.fetch_result")
    def test_missing_result_slip_remains_pending_without_a_failure_state(self, fetch_result):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        fetch_result.side_effect = ParaLearnResultNotFoundError("not found")

        response = self.client.post(reverse("paralearn_reconcile_result", kwargs={"attempt_id": attempt.pk}))

        self.assertRedirects(response, reverse("course_detail", kwargs={"slug": self.course.slug}))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, CourseAssessmentAttempt.Status.RESULT_PENDING)
        self.assertEqual(attempt.reconciliation_count, 1)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())

    @patch("learning.assessment_services.ParaLearnClient.fetch_result")
    def test_disqualified_result_slip_is_terminal_and_never_awards_badge(self, fetch_result):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        fetch_result.return_value = self._result_slip(
            attempt,
            status="DISQUALIFIED",
            isPassed=False,
            percentage=95.0,
            violations=4,
        )

        response = self.client.post(reverse("paralearn_reconcile_result", kwargs={"attempt_id": attempt.pk}))

        self.assertRedirects(response, reverse("course_detail", kwargs={"slug": self.course.slug}))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, CourseAssessmentAttempt.Status.DISQUALIFIED)
        self.assertFalse(attempt.passed)
        self.assertIsNotNone(attempt.result_verified_at)
        self.assertNotIn("candidatePin", attempt.result_payload)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())
        detail = self.client.get(reverse("course_detail", kwargs={"slug": self.course.slug}))
        self.assertContains(detail, "Disqualified")
        self.assertNotContains(detail, "Check result")

    @override_settings(
        PARALEARN_API_BASE_URL="",
        PARALEARN_API_KEY="",
        PARALEARN_API_KEY_HEADER="",
    )
    def test_launch_is_fail_closed_when_vendor_contract_is_not_configured(self):
        response = self.client.post(reverse("paralearn_launch", kwargs={"slug": self.course.slug}))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(CourseAssessmentAttempt.objects.count(), 0)

    def test_legacy_quiz_cannot_complete_or_award_after_phase_three(self):
        question = Question.objects.create(course=self.course, text="Legacy question")
        choice = Choice.objects.create(question=question, text="Correct", is_correct=True)

        result = grade_course_quiz(
            user=self.user,
            course=self.course,
            post_data={f"question_{question.id}": str(choice.id)},
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["authoritative"])
        self.assertEqual(QuizAttempt.objects.count(), 1)
        self.assertEqual(CourseProgress.objects.get(user=self.user, course=self.course).status, CourseProgress.Status.NOT_STARTED)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())

        legacy_route = self.client.post(reverse("course_quiz", kwargs={"slug": self.course.slug}))
        self.assertRedirects(legacy_route, reverse("course_detail", kwargs={"slug": self.course.slug}))
        self.assertEqual(QuizAttempt.objects.count(), 1)

    def test_badge_service_rejects_an_unverified_attempt(self):
        attempt = create_assessment_attempt(user=self.user, course=self.course)

        with self.assertRaisesMessage(ValueError, "verified passing ParaLearn"):
            award_badge(self.user, self.course, verified_attempt=attempt)
        self.assertFalse(Badge.objects.filter(user=self.user, course=self.course).exists())

    @patch("learning.paralearn.urlopen")
    def test_client_provisions_candidate_using_the_confirmed_contract(self, urlopen):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        identity = ParaLearnLearnerIdentity.objects.get(user=self.user)
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {
                "id": "cand-001",
                "launchUrl": "https://pln.ng/take/SWEEP-101?pin=849201&attemptId=" + str(attempt.pk),
            }
        ).encode("utf-8")
        urlopen.return_value = response

        launch = ParaLearnClient().create_launch(attempt=attempt, learner_identity=identity)

        self.assertEqual(launch.provider_candidate_id, "cand-001")
        self.assertEqual(launch.launch_url, "https://pln.ng/take/SWEEP-101?pin=849201&attemptId=" + str(attempt.pk))
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_full_url(), "https://pln.ng/api/cbt/candidates")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(
            body,
            {
                "examId": "pl-course-101",
                "candidateName": "assessment-learner",
                "studentId": str(identity.external_id),
                "externalAttemptId": str(attempt.pk),
                "email": "learner@example.test",
                "metadata": {
                    "sweepLearnerId": str(identity.external_id),
                    "sweepAttemptId": str(attempt.pk),
                },
            },
        )
        self.assertNotIn("candidatePin", body)

    @patch("learning.paralearn.urlopen")
    def test_client_fetches_the_documented_result_slip_by_external_attempt_id(self, urlopen):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {"attemptId": "provider-attempt-001", "status": "IN_PROGRESS"}
        ).encode("utf-8")
        urlopen.return_value = response

        slip = ParaLearnClient().fetch_result(attempt_reference=str(attempt.pk))

        self.assertEqual(slip["attemptId"], "provider-attempt-001")
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.get_full_url(),
            f"https://pln.ng/api/cbt/attempts/{attempt.pk}/slip",
        )
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")

    @patch("learning.paralearn.urlopen")
    def test_client_maps_a_missing_result_slip_to_a_pending_signal(self, urlopen):
        attempt = create_assessment_attempt(user=self.user, course=self.course)
        urlopen.side_effect = HTTPError(
            "https://pln.ng/api/cbt/attempts/missing/slip", 404, "Not Found", None, None
        )

        with self.assertRaises(ParaLearnResultNotFoundError):
            ParaLearnClient().fetch_result(attempt_reference=str(attempt.pk))
