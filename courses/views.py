from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from schools.models import School

from .models import Course


def course_list(request):
    """Search and filter courses across every school."""
    query = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    school_slug = request.GET.get("school", "").strip()

    courses = Course.objects.filter(is_active=True).select_related("school")

    if query:
        courses = courses.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(content__icontains=query)
        )
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    if school_slug:
        courses = courses.filter(school__slug=school_slug)

    enrolled_course_ids = set()
    completed_course_ids = set()
    if request.user.is_authenticated:
        enrolled_course_ids = set(
            request.user.course_enrollments.values_list("course_id", flat=True)
        )
        from learning.models import CourseProgress

        completed_course_ids = set(
            CourseProgress.objects.filter(
                user=request.user, status=CourseProgress.Status.COMPLETED
            ).values_list("course_id", flat=True)
        )

    context = {
        "courses": courses,
        "query": query,
        "difficulty": difficulty,
        "school_slug": school_slug,
        "schools": School.objects.filter(is_active=True),
        "difficulty_choices": Course.Difficulty.choices,
        "enrolled_course_ids": enrolled_course_ids,
        "completed_course_ids": completed_course_ids,
    }
    return render(request, "courses/course_list.html", context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    is_enrolled = False
    progress = None
    badge = None
    latest_attempt = None

    if request.user.is_authenticated:
        is_enrolled = course.enrollments.filter(user=request.user).exists()
        from learning.models import CourseProgress, QuizAttempt
        from credentials.models import Badge

        progress = CourseProgress.objects.filter(user=request.user, course=course).first()
        badge = Badge.objects.filter(user=request.user, course=course).first()
        latest_attempt = (
            QuizAttempt.objects.filter(user=request.user, course=course)
            .order_by("-submitted_at")
            .first()
        )

    context = {
        "course": course,
        "is_enrolled": is_enrolled,
        "progress": progress,
        "badge": badge,
        "latest_attempt": latest_attempt,
        "question_count": course.question_count,
    }
    return render(request, "courses/course_detail.html", context)


@login_required
def course_quiz(request, slug):
    """Display and grade the multiple-choice assessment for a course."""
    course = get_object_or_404(Course, slug=slug, is_active=True)

    if not course.enrollments.filter(user=request.user).exists():
        messages.warning(request, "You need to enroll in this course before taking its assessment.")
        return redirect("course_detail", slug=course.slug)

    questions = course.questions.prefetch_related("choices").all()

    if not questions:
        messages.info(request, "This course does not have an assessment configured yet.")
        return redirect("course_detail", slug=course.slug)

    if request.method == "POST":
        from learning.services import grade_course_quiz

        result = grade_course_quiz(user=request.user, course=course, post_data=request.POST)
        context = {
            "course": course,
            "questions": questions,
            "result": result,
        }
        return render(request, "courses/quiz_result.html", context)

    context = {"course": course, "questions": questions}
    return render(request, "courses/quiz.html", context)
