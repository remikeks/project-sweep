from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from courses.models import Course
from schools.models import School, SchoolExamQuestion

from . import services
from .models import CourseProgress, SchoolExamAttempt


@login_required
@require_POST
def enroll_in_school_view(request, slug):
    school = get_object_or_404(School, slug=slug, is_active=True)
    _, created = services.enroll_in_school(request.user, school)
    if created:
        messages.success(
            request,
            f"You're enrolled in {school.name}. All {school.course_count} of its courses "
            "have been added to your dashboard.",
        )
    else:
        messages.info(request, f"You're already enrolled in {school.name}.")
    return redirect("school_detail", slug=school.slug)


@login_required
@require_POST
def enroll_in_course_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    _, created = services.enroll_in_course(request.user, course)
    if created:
        messages.success(request, f"You're enrolled in {course.title}.")
    else:
        messages.info(request, f"You're already enrolled in {course.title}.")

    first_module = course.modules.order_by("order", "id").first()
    if first_module:
        return redirect("course_module_detail", slug=course.slug, module_order=first_module.order)
    return redirect("course_detail", slug=course.slug)


@login_required
def dashboard(request):
    """The user's personal learning dashboard: schools, courses, progress."""
    school_enrollments = request.user.school_enrollments.select_related("school")
    course_enrollments = request.user.course_enrollments.select_related("course", "course__school")

    progress_map = {
        p.course_id: p for p in CourseProgress.objects.filter(user=request.user)
    }

    course_rows = []
    for enrollment in course_enrollments:
        progress = progress_map.get(enrollment.course_id)
        course_rows.append({"course": enrollment.course, "progress": progress})

    school_rows = []
    for enrollment in school_enrollments:
        completed, total, fully_completed = services.school_completion_status(
            request.user, enrollment.school
        )
        school_rows.append(
            {
                "school": enrollment.school,
                "completed": completed,
                "total": total,
                "fully_completed": fully_completed,
                "percent": int((completed / total) * 100) if total else 0,
            }
        )

    is_new_learner = not school_rows and not course_rows
    starter_schools = []
    starter_courses = []
    if is_new_learner:
        starter_schools = list(School.objects.filter(is_active=True).order_by("order", "id")[:3])
        starter_courses = list(
            Course.objects.filter(is_active=True).select_related("school").order_by("order", "id")[:3]
        )

    context = {
        "course_rows": course_rows,
        "school_rows": school_rows,
        "completed_courses_count": sum(
            1 for row in course_rows if row["progress"] and row["progress"].status == "completed"
        ),
        "completed_schools_count": sum(1 for row in school_rows if row["fully_completed"]),
        "is_new_learner": is_new_learner,
        "starter_schools": starter_schools,
        "starter_courses": starter_courses,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def school_exam(request, slug):
    """Display and grade a school's certification exam."""
    school = get_object_or_404(School, slug=slug, is_active=True)
    completed, total, fully_completed = services.school_completion_status(request.user, school)

    if not fully_completed:
        messages.warning(
            request,
            f"Complete all {total} courses in {school.name} before taking its certification exam.",
        )
        return redirect("school_detail", slug=school.slug)

    questions = SchoolExamQuestion.objects.filter(school=school).prefetch_related("choices")

    if not questions:
        messages.info(request, "This school's certification exam isn't configured yet.")
        return redirect("school_detail", slug=school.slug)

    if request.method == "POST":
        result = services.grade_school_exam(user=request.user, school=school, post_data=request.POST)
        context = {"school": school, "result": result}
        return render(request, "schools/exam_result.html", context)

    context = {"school": school, "questions": questions}
    return render(request, "schools/school_exam.html", context)
