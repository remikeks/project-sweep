"""
Core business logic for SWEEP enrollment, progress tracking, and
assessment grading. Keeping this out of views.py/models.py makes the
rules easy to find and easy to unit test.
"""

from django.db import transaction
from django.utils import timezone

from courses.models import Course, CourseModule
from schools.models import School, SchoolExamChoice, SchoolExamQuestion

from .models import (
    CourseEnrollment,
    CourseProgress,
    QuizAttempt,
    SchoolEnrollment,
    SchoolCurriculumRequirement,
    ModuleProgress,
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
        SchoolCurriculumRequirement.objects.get_or_create(
            school_enrollment=school_enrollment, course=course, defaults={"order": course.order}
        )

    return school_enrollment, created


def school_completion_status(user, school: School):
    """Return (completed_count, total_count, is_fully_completed) for a user/school pair."""
    enrollment = SchoolEnrollment.objects.filter(user=user, school=school).first()
    if not enrollment:
        return 0, 0, False
    all_courses = Course.objects.filter(school_curriculum_requirements__school_enrollment=enrollment)
    total = all_courses.count()
    if total == 0:
        return 0, 0, False

    completed = CourseProgress.objects.filter(
        user=user,
        course__in=all_courses,
        status=CourseProgress.Status.COMPLETED,
    ).count()
    return completed, total, completed == total


def module_completion_state(user, course: Course):
    """Return ordered modules, completed IDs, and the sole module currently unlockable."""
    modules = list(course.modules.order_by("order", "id"))
    completed_ids = set(ModuleProgress.objects.filter(user=user, module__course=course).values_list("module_id", flat=True))
    current = next((module for module in modules if module.id not in completed_ids), None)
    return modules, completed_ids, current


def course_modules_complete(user, course: Course) -> bool:
    modules, completed_ids, _ = module_completion_state(user, course)
    return not modules or len(completed_ids) == len(modules)


def complete_module(*, user, module: CourseModule):
    """Idempotently complete only the next sequential module for an enrolled learner."""
    if not CourseEnrollment.objects.filter(user=user, course=module.course).exists():
        raise PermissionError("You must be enrolled in this course.")
    with transaction.atomic():
        modules = list(CourseModule.objects.select_for_update().filter(course=module.course).order_by("order", "id"))
        completed = set(ModuleProgress.objects.filter(user=user, module__in=modules).values_list("module_id", flat=True))
        if module.id in completed:
            return ModuleProgress.objects.get(user=user, module=module), False
        expected = next((item for item in modules if item.id not in completed), None)
        if expected is None or expected.id != module.id:
            raise ValueError("Complete the previous module before continuing.")
        progress, created = ModuleProgress.objects.get_or_create(user=user, module=module)
        course_progress, _ = CourseProgress.objects.get_or_create(user=user, course=module.course)
        if course_progress.status == CourseProgress.Status.NOT_STARTED:
            course_progress.status = CourseProgress.Status.IN_PROGRESS
            course_progress.save(update_fields=["status"])
        return progress, created


# --------------------------------------------------------------------------
# Course assessment grading
# --------------------------------------------------------------------------

def grade_course_quiz(user, course: Course, post_data):
    """
    Grade the deprecated local knowledge check and retain its historical
    record. It must never update course completion or award a badge: ParaLearn
    CBT is the only authority for those actions.

    The function remains for backwards-compatible reporting/import work while
    the old quiz UI is no longer exposed as the course assessment route.
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

    return {
        "course": course,
        "score": score,
        "passed": passed,
        "correct_count": correct,
        "question_count": total,
        "authoritative": False,
        "newly_completed": False,
        "badge_awarded": False,
        "school_fully_completed": False,
        "school_completed_count": 0,
        "school_total_count": 0,
    }


# --------------------------------------------------------------------------
# School certification exam grading
# --------------------------------------------------------------------------

def grade_school_exam(user, school: School, post_data):
    """
    Grade a submitted school certification exam and award a certificate
    if the user passed. Returns a result dict used by the template.
    """
    _, _, eligible = school_completion_status(user, school)
    if not eligible:
        raise PermissionError("Complete the enrolled curriculum before taking this examination.")
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

    with transaction.atomic():
        # Recheck eligibility under the write transaction before issuing.
        _, _, eligible = school_completion_status(user, school)
        if not eligible:
            raise PermissionError("Your curriculum completion changed; please try again.")
        SchoolExamAttempt.objects.create(
            user=user, school=school, score=score, passed=passed,
            correct_count=correct, question_count=total,
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
