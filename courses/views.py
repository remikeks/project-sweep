from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe

import bleach
import markdown

from schools.models import School

from .models import Course, CourseModule
from .content_api import content_catalog, create_asset, import_assets, transition_asset_view


ALLOWED_MARKDOWN_TAGS = {
    "a", "blockquote", "br", "code", "em", "h1", "h2", "h3", "h4",
    "hr", "li", "ol", "p", "pre", "strong", "table", "tbody", "td",
    "th", "thead", "tr", "ul",
}
ALLOWED_MARKDOWN_ATTRIBUTES = {"a": ["href", "title"]}


def render_course_markdown(value):
    """Render staff-authored Markdown without allowing executable HTML."""
    rendered = markdown.markdown(value or "", extensions=["fenced_code", "tables"])
    cleaned = bleach.clean(
        rendered,
        tags=ALLOWED_MARKDOWN_TAGS,
        attributes=ALLOWED_MARKDOWN_ATTRIBUTES,
        protocols=["http", "https", "mailto"],
        strip=True,
    )
    return mark_safe(cleaned)


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
        from learning.models import CourseEnrollment, CourseProgress

        enrolled_course_ids = set(
            CourseEnrollment.objects.filter(user=request.user).values_list("course_id", flat=True)
        )
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

    first_module = course.modules.order_by("order", "id").first()
    context = {
        "course": course,
        "is_enrolled": is_enrolled,
        "progress": progress,
        "badge": badge,
        "latest_attempt": latest_attempt,
        "question_count": course.question_count,
        "first_module": first_module,
    }
    return render(request, "courses/course_detail.html", context)


def course_module_detail(request, slug, module_order):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    module = get_object_or_404(CourseModule, course=course, order=module_order)

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = course.enrollments.filter(user=request.user).exists()

    if request.user.is_authenticated and not is_enrolled:
        messages.warning(request, "You need to enroll in this course before accessing its modules.")
        return redirect("course_detail", slug=course.slug)

    ordered_modules = list(course.modules.order_by("order", "id"))
    module_ids = [mod.id for mod in ordered_modules]
    current_index = module_ids.index(module.id) if module.id in module_ids else -1

    prev_module = None
    next_module = None
    next_course = None

    is_course_completed = False
    if request.user.is_authenticated:
        from learning.models import CourseProgress

        is_course_completed = CourseProgress.objects.filter(
            user=request.user,
            course=course,
            status=CourseProgress.Status.COMPLETED,
        ).exists()

    if is_course_completed:
        next_course = (
            course.school.courses.filter(is_active=True)
            .filter(Q(order__gt=course.order) | Q(order=course.order, id__gt=course.id))
            .order_by("order", "id")
            .first()
        )

    assets = module.assets.filter(status="published")

    if current_index > 0:
        prev_module = ordered_modules[current_index - 1]
    if current_index != -1 and current_index < len(ordered_modules) - 1:
        next_module = ordered_modules[current_index + 1]

    context = {
        "course": course,
        "module": module,
        "is_enrolled": is_enrolled,
        "prev_module": prev_module,
        "next_module": next_module,
        "next_course": next_course,
        "question_count": course.question_count,
        "is_course_completed": is_course_completed,
        "assets": assets,
        "module_overview_html": render_course_markdown(module.overview),
        "module_content_html": render_course_markdown(module.content),
        "module_summary_html": render_course_markdown(module.module_summary),
        "knowledge_check_html": render_course_markdown(module.knowledge_check),
        "practical_activity_html": render_course_markdown(module.practical_activity),
    }
    return render(request, "courses/course_module_detail.html", context)


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
        next_course = (
            course.school.courses.filter(is_active=True)
            .filter(Q(order__gt=course.order) | Q(order=course.order, id__gt=course.id))
            .order_by("order", "id")
            .first()
        )
        context = {
            "course": course,
            "questions": questions,
            "result": result,
            "next_course": next_course,
        }
        return render(request, "courses/quiz_result.html", context)

    context = {"course": course, "questions": questions}
    return render(request, "courses/quiz.html", context)
