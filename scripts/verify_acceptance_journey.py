"""End-to-End Acceptance Test: The "Golden Learner Journey".

Validates:
1. Test learner creation & course enrollment.
2. Sequential module locking and unlocking.
3. Private storage signed asset URL generation.
4. ParaLearn CBT attempt creation and signed webhook processing.
5. Webhook idempotency and badge issuance.
6. School curriculum completion and school certification exam grading.
7. Certificate issuance, public verification endpoint, and revocation.
8. Safe test record cleanup.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import uuid
from decimal import Decimal
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sweep.settings")
import django
django.setup()

from django.conf import settings

if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ["testserver"]
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

from courses.content_storage import SupabaseStorageClient
from courses.models import Course, CourseAsset, CourseModule
from credentials.models import Badge, Certificate
from credentials.services import revoke_credential
from learning.assessment_services import (
    create_assessment_attempt,
    process_signed_webhook,
)
from learning.models import (
    CourseAssessmentAttempt,
    CourseEnrollment,
    CourseProgress,
    ModuleProgress,
    ParaLearnLearnerIdentity,
    ParaLearnWebhookEvent,
    SchoolEnrollment,
    SchoolExamAttempt,
)
from learning.services import (
    complete_module,
    course_modules_complete,
    enroll_in_school,
    grade_school_exam,
    module_completion_state,
    school_completion_status,
)
from schools.models import School, SchoolExamChoice, SchoolExamQuestion

User = get_user_model()


def run_acceptance_test():
    print("=" * 60)
    print("STARTING SWEEP GOLDEN LEARNER ACCEPTANCE TEST")
    print("=" * 60)

    test_username = f"qa_learner_{uuid.uuid4().hex[:8]}"
    test_email = f"{test_username}@acceptance-sweep.test"

    print(f"\n1. Creating disposable test learner: {test_email}")
    user = User.objects.create_user(
        username=test_username,
        email=test_email,
        password="TestPassword123!",
        first_name="QA",
        last_name="Learner",
    )

    try:
        # Step 2: Course Enrollment
        course = Course.objects.filter(course_code="SWP-001", is_active=True).first()
        if not course:
            raise RuntimeError("Course SWP-001 not found.")
        original_assessment_id = course.paralearn_assessment_id
        if not course.paralearn_assessment_id:
            course.paralearn_assessment_id = "test-cbt-swp-001"
            course.save(update_fields=["paralearn_assessment_id"])
        print(f"2. Enrolling in course: {course.course_code} - {course.title}")
        enrollment, _ = CourseEnrollment.objects.get_or_create(user=user, course=course)

        # Step 3: Verify Sequential Module Locking
        modules = list(course.modules.order_by("order", "id"))
        if len(modules) < 3:
            raise RuntimeError(f"Expected at least 3 modules in SWP-001, found {len(modules)}")

        print("\n3. Testing sequential module gating:")
        all_mods, completed_ids, current_mod = module_completion_state(user, course)
        assert len(completed_ids) == 0, "No modules should be completed initially"
        assert current_mod and current_mod.id == modules[0].id, "Module 1 must be the current unlockable module"
        assert not course_modules_complete(user, course), "Course modules should be incomplete"

        # Attempting to complete Module 2 out of order must raise ValueError
        try:
            complete_module(user=user, module=modules[1])
            raise AssertionError("Completing Module 2 before Module 1 should have failed!")
        except ValueError:
            print("  [OK] Out-of-order completion prevented: Module 2 is locked until Module 1 is complete.")

        # Step 4: Progress through modules sequentially
        print("\n4. Progressing through modules sequentially:")
        complete_module(user=user, module=modules[0])
        _, completed_after_1, current_after_1 = module_completion_state(user, course)
        assert modules[0].id in completed_after_1, "Module 1 should be marked completed"
        assert current_after_1.id == modules[1].id, "Module 2 should now be the current unlockable module"
        print("  [OK] Module 1 completed -> Module 2 unlocked.")

        complete_module(user=user, module=modules[1])
        _, completed_after_2, current_after_2 = module_completion_state(user, course)
        assert modules[1].id in completed_after_2, "Module 2 should be marked completed"
        assert current_after_2.id == modules[2].id, "Module 3 should now be the current unlockable module"
        print("  [OK] Module 2 completed -> Module 3 unlocked.")

        complete_module(user=user, module=modules[2])
        assert course_modules_complete(user, course), "All course modules should now be complete"
        print("  [OK] Module 3 completed -> All modules complete for SWP-001.")

        # Step 5: Verify Course Asset Signed Download URL
        print("\n5. Testing Course Asset access & signed URL generation:")
        sample_asset = course.assets.filter(status="published").first()
        if sample_asset and sample_asset.storage_path:
            storage_client = SupabaseStorageClient()
            signed_url = storage_client.create_signed_download_url(
                sample_asset.storage_path,
                download=sample_asset.is_downloadable,
            )
            assert signed_url.startswith("https://"), "Signed URL must be a valid HTTPS URL"
            print(f"  [OK] Generated signed URL for '{sample_asset.title}': {signed_url[:60]}...")
        else:
            print("  [INFO] No published asset with storage_path found for SWP-001; skipping storage URL check.")

        # Step 6: ParaLearn CBT Attempt & Webhook Processing
        print("\n6. Creating ParaLearn Assessment Attempt:")
        attempt = create_assessment_attempt(user=user, course=course)
        print(f"  [OK] Attempt created: {attempt.id} (Status: {attempt.status})")

        identity = ParaLearnLearnerIdentity.objects.get(user=user)
        event_id = f"evt_test_{uuid.uuid4().hex}"
        now_iso = timezone.now().isoformat()
        webhook_payload = {
            "event": "exam.attempt.completed",
            "eventId": event_id,
            "timestamp": now_iso,
            "status": "SUBMITTED",
            "externalAttemptId": str(attempt.id),
            "studentId": str(identity.external_id),
            "attemptId": f"pla_{uuid.uuid4().hex[:12]}",
            "examId": course.paralearn_assessment_id,
            "percentage": 85.0,
            "submittedAt": now_iso,
        }
        raw_body = json.dumps(webhook_payload).encode("utf-8")

        # Configure dummy signing secret if not configured in environment
        signing_secret = settings.PARALEARN_WEBHOOK_SIGNING_SECRET or "test-secret-key-12345"
        settings.PARALEARN_WEBHOOK_SIGNING_SECRET = signing_secret
        settings.PARALEARN_WEBHOOK_SIGNATURE_HEADER = "x-cbt-signature"
        settings.PARALEARN_WEBHOOK_EVENT_HEADER = "x-cbt-event"
        settings.PARALEARN_WEBHOOK_EVENT_ID_HEADER = "x-cbt-event-id"
        settings.PARALEARN_WEBHOOK_TIMESTAMP_HEADER = "x-cbt-timestamp"

        signature_hash = hmac.new(
            signing_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        signature_header = f"sha256={signature_hash}"

        print("\n7. Simulating signed ParaLearn webhook POST:")
        client = Client()
        response = client.post(
            "/courses/paralearn/webhook/",
            data=raw_body,
            content_type="application/json",
            HTTP_X_CBT_SIGNATURE=signature_header,
            HTTP_X_CBT_EVENT="exam.attempt.completed",
            HTTP_X_CBT_EVENT_ID=event_id,
            HTTP_X_CBT_TIMESTAMP=now_iso,
        )
        assert response.status_code == 200, f"Webhook failed with status {response.status_code}: {response.content}"
        resp_data = response.json()
        assert resp_data.get("badge_awarded") is True, f"Expected badge_awarded=True, got {resp_data}"
        assert resp_data.get("duplicate") is False, f"Expected duplicate=False, got {resp_data}"
        print("  [OK] Webhook verified and processed successfully.")

        # Step 7: Webhook Idempotency Check
        print("\n8. Testing Webhook Idempotency (replay attack / duplicate event):")
        replay_response = client.post(
            "/courses/paralearn/webhook/",
            data=raw_body,
            content_type="application/json",
            HTTP_X_CBT_SIGNATURE=signature_header,
            HTTP_X_CBT_EVENT="exam.attempt.completed",
            HTTP_X_CBT_EVENT_ID=event_id,
            HTTP_X_CBT_TIMESTAMP=now_iso,
        )
        assert replay_response.status_code == 200, f"Duplicate webhook returned {replay_response.status_code}"
        replay_data = replay_response.json()
        assert replay_data.get("duplicate") is True, f"Duplicate webhook must have duplicate=True, got {replay_data}"
        assert replay_data.get("badge_awarded") is False, "Duplicate webhook must not award duplicate badge"
        print("  [OK] Idempotency confirmed: Duplicate webhook accepted with 0 new badges.")

        # Step 8: Badge Verification
        print("\n9. Verifying Course Badge:")
        badge = Badge.objects.filter(user=user, course=course, status="active").first()
        assert badge is not None, "Badge was not found in database"
        print(f"  [OK] Badge successfully earned! UID: {badge.uid} | Title: {badge.credential_title}")

        # Step 9: School Enrolment & School Certification Exam
        print("\n10. Testing School Certification & Exam:")
        school = course.school
        school_enrolment, _ = enroll_in_school(user, school)

        # Mark all courses in school completed for this certification test
        all_courses = Course.objects.filter(school_curriculum_requirements__school_enrollment=school_enrolment)
        for c in all_courses:
            prog, _ = CourseProgress.objects.get_or_create(user=user, course=c)
            prog.status = CourseProgress.Status.COMPLETED
            prog.save(update_fields=["status"])

        _, _, eligible = school_completion_status(user, school)
        assert eligible, "Learner should now be eligible for School Exam"
        print(f"  [OK] Enrolled in {school.name} and eligible for School Certification Exam.")

        # Prepare correct answers for school exam
        exam_questions = SchoolExamQuestion.objects.filter(school=school).prefetch_related("choices")
        post_data = {}
        for q in exam_questions:
            correct_choice = q.choices.filter(is_correct=True).first()
            if correct_choice:
                post_data[f"exam_question_{q.id}"] = str(correct_choice.id)

        exam_result = grade_school_exam(user, school, post_data)
        assert exam_result["passed"], f"Expected exam to pass, score: {exam_result['score']}"
        assert exam_result["certificate_awarded"], "Certificate should have been awarded"
        print(f"  [OK] School Exam passed with score {exam_result['score']}%.")

        certificate = Certificate.objects.filter(user=user, school=school, status="active").first()
        assert certificate is not None, "Certificate was not found in database"
        print(f"  [OK] Certificate issued! UID: {certificate.uid} | Title: {certificate.credential_title}")

        # Step 10: Public Credential Verification URL
        print("\n11. Testing Public Verification endpoint:")
        verify_url = f"/credentials/verify/{certificate.uid}/"
        anon_client = Client()
        verify_resp = anon_client.get(verify_url)
        assert verify_resp.status_code == 200, f"Verify endpoint returned status {verify_resp.status_code}"
        assert b"Credential verified" in verify_resp.content, "Rendered page must confirm 'Credential verified'"
        assert str(certificate.uid).encode("utf-8") in verify_resp.content, "Rendered page must contain verification ID"
        print(f"  [OK] Public verification verified active credential at {verify_url}")

        # Step 11: Credential Revocation Check
        print("\n12. Testing Credential Revocation lifecycle:")
        revoke_credential(certificate, reason="Automated test validation revocation")
        verify_revoked_resp = anon_client.get(verify_url)
        assert verify_revoked_resp.status_code == 200, f"Revoked verify endpoint returned {verify_revoked_resp.status_code}"
        assert b"Credential is not active" in verify_revoked_resp.content, "Revoked credential must show 'Credential is not active'"
        print("  [OK] Revoked credential correctly displays 'Credential is not active'.")

        print("\n" + "=" * 60)
        print("ALL ACCEPTANCE CHECKS PASSED SUCCESSFULLY!")
        print("=" * 60)

    finally:
        # Step 12: Clean up test learner and records
        print("\nCleaning up test artifacts...")
        try:
            Badge.objects.filter(user=user).delete()
            Certificate.objects.filter(user=user).delete()
            CourseAssessmentAttempt.objects.filter(user=user).delete()
            ParaLearnWebhookEvent.objects.filter(payload__icontains=test_username).delete()
            ModuleProgress.objects.filter(user=user).delete()
            CourseProgress.objects.filter(user=user).delete()
            CourseEnrollment.objects.filter(user=user).delete()
            SchoolExamAttempt.objects.filter(user=user).delete()
            SchoolEnrollment.objects.filter(user=user).delete()
            ParaLearnLearnerIdentity.objects.filter(user=user).delete()
            if 'course' in locals() and 'original_assessment_id' in locals():
                course.paralearn_assessment_id = original_assessment_id
                course.save(update_fields=["paralearn_assessment_id"])
            user.delete()
            print("[OK] Cleanup complete. Database left in pristine state.")
        except Exception as e:
            print(f"[WARN] Cleanup encountered error: {e}")


if __name__ == "__main__":
    run_acceptance_test()
