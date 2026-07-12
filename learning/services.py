"""
Core business logic for SWEEP enrollment, progress tracking, and
assessment grading. Keeping this out of views.py/models.py makes the
rules easy to find and easy to unit test.
"""

from django.utils import timezone

from courses.models import Course
from schools.models import School, SchoolExamChoice, SchoolExamQuestion

from .models import (
    CourseEnrollment,
    CourseProgress,
    QuizAttempt,
    SchoolEnrollment,
    SchoolExamAttempt,
)


# --------------------------------------------------------------------------
# Enrollment
# --------------------------------------------------------------------------

def enroll_in_course(user, course: Course):
    """Enroll a user in a single course (idempotent)."""
    enrollment, created = CourseEnrollment.objects.get_or_create(user=user, course=course)
    CourseProgress.objects.get_or_create(user=user, course=course)
    return enrollment, created


def enroll_in_school(user, school: School):
    """
    Enroll a user in a school, which enrolls them in every active course
    that school currently offers (idempotent).
    """
    school_enrollment, created = SchoolEnrollment.objects.get_or_create(user=user, school=school)

    for course in school.active_courses:
        enrollment, _ = CourseEnrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={"via_school_enrollment": school_enrollment},
        )
        if enrollment.via_school_enrollment_id is None:
            enrollment.via_school_enrollment = school_enrollment
            enrollment.save(update_fields=["via_school_enrollment"])
        CourseProgress.objects.get_or_create(user=user, course=course)

    return school_enrollment, created


def school_completion_status(user, school: School):
    """Return (completed_count, total_count, is_fully_completed) for a user/school pair."""
    all_courses = school.active_courses
    total = all_courses.count()
    if total == 0:
        return 0, 0, False

    completed = CourseProgress.objects.filter(
        user=user,
        course__in=all_courses,
        status=CourseProgress.Status.COMPLETED,
    ).count()
    return completed, total, completed == total


# --------------------------------------------------------------------------
# Course assessment grading
# --------------------------------------------------------------------------

def grade_course_quiz(user, course: Course, post_data):
    """
    Grade a submitted course assessment, update progress, record the
    attempt, and award a badge if the user passed. Returns a result dict
    used by the template to render feedback.
    """
    questions = list(course.questions.prefetch_related("choices").all())
    total = len(questions)
    correct = 0

    for question in questions:
        selected_id = post_data.get(f"question_{question.id}")
        if selected_id and question.choices.filter(id=selected_id, is_correct=True).exists():
            correct += 1

    score = round((correct / total) * 100) if total else 0
    passed = score >= course.passing_score

    QuizAttempt.objects.create(
        user=user,
        course=course,
        score=score,
        passed=passed,
        correct_count=correct,
        question_count=total,
    )

    progress, _ = CourseProgress.objects.get_or_create(user=user, course=course)
    progress.attempts_count += 1
    progress.best_score = max(progress.best_score, score)

    newly_completed = False
    if passed:
        if progress.status != CourseProgress.Status.COMPLETED:
            progress.status = CourseProgress.Status.COMPLETED
            progress.completed_at = timezone.now()
            newly_completed = True
    elif progress.status == CourseProgress.Status.NOT_STARTED:
        progress.status = CourseProgress.Status.IN_PROGRESS
    progress.save()

    badge_awarded = False
    if passed:
        from credentials.services import award_badge

        _, badge_awarded = award_badge(user, course)

    completed_count, total_count, school_fully_completed = school_completion_status(
        user, course.school
    )

    return {
        "course": course,
        "score": score,
        "passed": passed,
        "correct_count": correct,
        "question_count": total,
        "newly_completed": newly_completed,
        "badge_awarded": badge_awarded,
        "school_fully_completed": school_fully_completed,
        "school_completed_count": completed_count,
        "school_total_count": total_count,
    }


# --------------------------------------------------------------------------
# School certification exam grading
# --------------------------------------------------------------------------

def grade_school_exam(user, school: School, post_data):
    """
    Grade a submitted school certification exam and award a certificate
    if the user passed. Returns a result dict used by the template.
    """
    questions = list(SchoolExamQuestion.objects.filter(school=school).prefetch_related("choices"))
    total = len(questions)
    correct = 0

    for question in questions:
        selected_id = post_data.get(f"exam_question_{question.id}")
        if selected_id and SchoolExamChoice.objects.filter(
            id=selected_id, question=question, is_correct=True
        ).exists():
            correct += 1

    score = round((correct / total) * 100) if total else 0
    passed = score >= school.passing_score

    SchoolExamAttempt.objects.create(
        user=user,
        school=school,
        score=score,
        passed=passed,
        correct_count=correct,
        question_count=total,
    )

    certificate_awarded = False
    if passed:
        from credentials.services import award_certificate

        _, certificate_awarded = award_certificate(user, school)

    return {
        "school": school,
        "score": score,
        "passed": passed,
        "correct_count": correct,
        "question_count": total,
        "certificate_awarded": certificate_awarded,
    }
