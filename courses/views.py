from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import io
import json

import bleach
import markdown

from django.conf import settings
from django.core.management import call_command
from schools.models import School

from .models import Course, CourseAsset, CourseModule
from .content_api import (
    content_catalog,
    create_asset,
    create_replacement_upload_intent,
    create_upload_intent,
    import_assets,
    preview_asset,
    replace_asset,
    transition_asset_view,
)
from .content_storage import StorageConfigurationError, StorageRequestError, SupabaseStorageClient, storage_is_configured
from learning.assessment_services import (
    AssessmentResultError,
    create_assessment_attempt,
    launch_assessment_attempt,
    process_signed_webhook,
    reconcile_assessment_attempt,
)
from learning.models import CourseAssessmentAttempt
from learning.services import complete_module, course_modules_complete, module_completion_state
from learning.paralearn import (
    ParaLearnError,
    launch_is_configured,
    result_reconciliation_is_configured,
    verify_webhook_signature,
    webhook_is_configured,
)


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


@login_required
@permission_required("courses.view_courseasset", raise_exception=True)
def content_portal(request):
    """Django-session workspace for authors, reviewers, and publishers."""
    courses = Course.objects.select_related("school").prefetch_related(
        "modules",
        Prefetch("assets", queryset=CourseAsset.objects.select_related("module")),
    )
    catalog = [
        {
            "slug": course.slug,
            "title": course.title,
            "school": course.school.name,
            "modules": [{"order": module.order, "title": module.title} for module in course.modules.all()],
            "assets": [
                {
                    "id": asset.id,
                    "title": asset.title,
                    "asset_type": asset.asset_type,
                    "asset_type_label": asset.get_asset_type_display(),
                    "status": asset.status,
                    "status_label": asset.get_status_display(),
                    "version": asset.version,
                    "language": asset.language,
                    "order": asset.order,
                    "module_order": asset.module.order if asset.module_id else None,
                    "module_title": asset.module.title if asset.module_id else "Course-wide",
                    "original_filename": asset.original_filename,
                    "size_bytes": asset.size_bytes,
                    "created_by": asset.created_by_id,
                    "replaces": asset.replaces_id,
                }
                for asset in course.assets.all()
            ],
        }
        for course in courses
    ]
    return render(
        request,
        "courses/content_portal.html",
        {
            "content_courses": courses,
            "storage_ready": storage_is_configured(),
            "can_author": request.user.has_perm("courses.add_courseasset"),
            "can_reviewer": request.user.has_perm("courses.review_courseasset"),
            "can_publisher": request.user.has_perm("courses.publish_courseasset"),
            "can_import": request.user.has_perm("courses.bulk_import_courseasset"),
            "content_catalog_data": catalog,
        },
    )


@login_required
def course_asset_download(request, asset_id):
    """Give enrolled learners a short-lived Storage URL for a published asset."""
    asset = get_object_or_404(
        CourseAsset.objects.select_related("course", "module"),
        pk=asset_id,
        status=CourseAsset.PublicationStatus.PUBLISHED,
        course__is_active=True,
    )
    if not asset.course.enrollments.filter(user=request.user).exists():
        messages.warning(request, "You need to enroll in this course before accessing its resources.")
        return redirect("course_detail", slug=asset.course.slug)
    if asset.storage_path and storage_is_configured():
        try:
            return redirect(
                SupabaseStorageClient().create_signed_download_url(
                    asset.storage_path,
                    download=asset.is_downloadable,
                )
            )
        except (StorageConfigurationError, StorageRequestError):
            return HttpResponse("This course resource is temporarily unavailable.", status=503)
    if asset.file:
        return redirect(asset.file.url)
    if asset.external_url:
        return redirect(asset.external_url)
    return HttpResponse("This course resource is unavailable.", status=404)


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
    verified_completion = False
    modules_complete = False

    if request.user.is_authenticated:
        is_enrolled = course.enrollments.filter(user=request.user).exists()
        from learning.models import CourseProgress
        from credentials.models import Badge

        progress = CourseProgress.objects.filter(user=request.user, course=course).first()
        badge = Badge.objects.filter(user=request.user, course=course).first()
        latest_attempt = (
            CourseAssessmentAttempt.objects.filter(user=request.user, course=course)
            .order_by("-created_at")
            .first()
        )
        verified_completion = CourseAssessmentAttempt.objects.filter(
            user=request.user,
            course=course,
            status=CourseAssessmentAttempt.Status.PASSED,
            result_verified_at__isnull=False,
        ).exists()
        modules_complete = course_modules_complete(request.user, course)

    modules = list(course.modules.order_by("order", "id"))
    first_module = modules[0] if modules else None

    completed_module_ids = set()
    current_unlocked_module_id = None
    if is_enrolled:
        _, completed_module_ids, current_mod = module_completion_state(request.user, course)
        current_unlocked_module_id = current_mod.id if current_mod else None

    context = {
        "course": course,
        "modules": modules,
        "completed_module_ids": completed_module_ids,
        "current_unlocked_module_id": current_unlocked_module_id,
        "is_enrolled": is_enrolled,
        "progress": progress,
        "badge": badge,
        "latest_attempt": latest_attempt,
        "verified_completion": verified_completion,
        "paralearn_assessment_ready": bool(course.paralearn_assessment_id),
        "paralearn_assessment_configured": bool(course.paralearn_assessment_id),
        "first_module": first_module,
        "modules_complete": modules_complete,
        "course_assets": course.assets.filter(status="published").select_related("module"),
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
    completed_module_ids = set()
    current_module = None
    if request.user.is_authenticated:
        from learning.models import CourseProgress

        is_course_completed = CourseProgress.objects.filter(
            user=request.user,
            course=course,
            status=CourseProgress.Status.COMPLETED,
        ).exists()
        _, completed_module_ids, current_module = module_completion_state(request.user, course)

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
        "paralearn_assessment_ready": bool(course.paralearn_assessment_id),
        "is_course_completed": is_course_completed,
        "assets": assets,
        "module_completed": module.id in completed_module_ids,
        "module_unlocked": is_course_completed or (current_module and current_module.id == module.id) or module.id in completed_module_ids,
        "modules_complete": not current_module,
        "module_overview_html": render_course_markdown(module.overview),
        "module_content_html": render_course_markdown(module.content),
        "module_summary_html": render_course_markdown(module.module_summary),
        "knowledge_check_html": render_course_markdown(module.knowledge_check),
        "practical_activity_html": render_course_markdown(module.practical_activity),
        "is_anonymous_visitor": not request.user.is_authenticated,
    }
    return render(request, "courses/course_module_detail.html", context)


@login_required
@require_POST
def complete_course_module(request, slug, module_order):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    module = get_object_or_404(CourseModule, course=course, order=module_order)
    try:
        _, created = complete_module(user=request.user, module=module)
    except PermissionError:
        messages.warning(request, "You need to enroll in this course first.")
        return redirect("course_detail", slug=course.slug)
    except ValueError as exc:
        messages.warning(request, str(exc))
        return redirect("course_module_detail", slug=course.slug, module_order=module.order)
    if created:
        messages.success(request, "Module marked complete.")
    return redirect("course_module_detail", slug=course.slug, module_order=module.order)


@login_required
def course_quiz(request, slug):
    """Preserve the former URL without allowing the local quiz to pass a course."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    messages.info(request, "Course completion is now verified through the ParaLearn CBT assessment.")
    return redirect("course_detail", slug=course.slug)


def _assessment_unavailable(request, course, message, status=503, retry_attempt=None):
    """Show a safe assessment error without losing a traceable retry path."""
    return render(
        request,
        "courses/assessment_unavailable.html",
        {
            "course": course,
            "assessment_message": message,
            "retry_attempt": retry_attempt,
        },
        status=status,
    )


@login_required
@require_POST
def paralearn_launch(request, slug):
    """Create and launch a ParaLearn assessment for an enrolled learner."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not course.enrollments.filter(user=request.user).exists():
        messages.warning(request, "You need to enroll in this course before taking its assessment.")
        return redirect("course_detail", slug=course.slug)
    if not course_modules_complete(request.user, course):
        messages.warning(request, "Complete each course module in order before taking the assessment.")
        return redirect("course_detail", slug=course.slug)
    if not course.paralearn_assessment_id:
        return _assessment_unavailable(
            request,
            course,
            "This course does not yet have a ParaLearn CBT assessment identifier.",
            status=409,
        )
    if not launch_is_configured():
        return _assessment_unavailable(
            request,
            course,
            "The ParaLearn assessment service is not configured yet. Please contact the course team.",
        )

    attempt = create_assessment_attempt(user=request.user, course=course)
    try:
        _, launch_url = launch_assessment_attempt(attempt=attempt)
    except (ParaLearnError, AssessmentResultError):
        # Never send a learner to an untracked direct exam URL here. The
        # provider webhook is deliberately bound to this attempt UUID, and a
        # raw launch would make the eventual result ineligible for completion
        # or credential issuance.
        return _assessment_unavailable(
            request,
            course,
            "We could not start your ParaLearn assessment. Your retryable attempt has been saved.",
            retry_attempt=attempt,
        )
    return redirect(launch_url)


@login_required
@require_POST
def paralearn_retry_launch(request, attempt_id):
    """Retry a failed launch with the same provider idempotency key."""
    attempt = get_object_or_404(
        CourseAssessmentAttempt.objects.select_related("course"),
        pk=attempt_id,
        user=request.user,
    )
    if attempt.status != CourseAssessmentAttempt.Status.LAUNCH_FAILED:
        messages.info(request, "This assessment launch cannot be retried in its current state.")
        return redirect("course_detail", slug=attempt.course.slug)

    if not launch_is_configured():
        return _assessment_unavailable(
            request,
            attempt.course,
            "The ParaLearn assessment service is not configured yet. Please contact the course team.",
        )
    try:
        _, launch_url = launch_assessment_attempt(attempt=attempt)
    except (ParaLearnError, AssessmentResultError):
        return _assessment_unavailable(
            request,
            attempt.course,
            "We could not restart your ParaLearn assessment. Please try again later.",
            retry_attempt=attempt,
        )
    return redirect(launch_url)


@login_required
@require_POST
def paralearn_reconcile_result(request, attempt_id):
    """Let a learner request recovery of a delayed provider result."""
    attempt = get_object_or_404(
        CourseAssessmentAttempt.objects.select_related("course"),
        pk=attempt_id,
        user=request.user,
    )
    try:
        reconciled, result_is_new, _ = reconcile_assessment_attempt(attempt=attempt)
    except (ParaLearnError, AssessmentResultError):
        messages.warning(request, "We could not verify a ParaLearn result yet. Please try again later.")
    else:
        if result_is_new and reconciled.passed:
            messages.success(request, "Your ParaLearn result was verified and your course badge has been awarded.")
        elif reconciled.status == CourseAssessmentAttempt.Status.DISQUALIFIED:
            messages.warning(request, "ParaLearn marked this assessment disqualified. Please contact the course team.")
        elif reconciled.status in {CourseAssessmentAttempt.Status.PASSED, CourseAssessmentAttempt.Status.FAILED}:
            messages.info(request, "Your ParaLearn result has already been verified.")
        else:
            messages.info(request, "ParaLearn has not published a final result for this assessment yet.")
    return redirect("course_detail", slug=attempt.course.slug)


@csrf_exempt
@require_POST
def paralearn_result_webhook(request):
    """Accept only configured, HMAC-verified ParaLearn result events."""
    if not webhook_is_configured():
        return JsonResponse({"detail": "ParaLearn webhook verification is not configured."}, status=503)

    raw_payload = request.body
    signature = request.headers.get(settings.PARALEARN_WEBHOOK_SIGNATURE_HEADER)
    if not verify_webhook_signature(raw_payload, signature):
        return JsonResponse({"detail": "Invalid webhook signature."}, status=401)
    if request.headers.get(settings.PARALEARN_WEBHOOK_EVENT_HEADER) != "exam.attempt.completed":
        return JsonResponse({"detail": "Unexpected ParaLearn webhook event."}, status=422)
    event_id = request.headers.get(settings.PARALEARN_WEBHOOK_EVENT_ID_HEADER, "")
    if not event_id:
        return JsonResponse({"detail": "Missing ParaLearn webhook event ID."}, status=422)
    # The provider timestamp is correlation metadata. The signed body remains
    # the authority for completed_at; retaining this check prevents accepting a
    # malformed delivery contract without relying on a client-supplied clock.
    timestamp = request.headers.get(settings.PARALEARN_WEBHOOK_TIMESTAMP_HEADER)
    if not timestamp:
        return JsonResponse({"detail": "Missing ParaLearn webhook timestamp."}, status=422)
    try:
        payload = json.loads(raw_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"detail": "Webhook body must be valid JSON."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"detail": "Webhook body must be a JSON object."}, status=400)
    if payload.get("timestamp") != timestamp:
        return JsonResponse({"detail": "Webhook timestamp does not match its signed payload."}, status=422)

    try:
        event, result_applied, badge_awarded = process_signed_webhook(
            payload=payload,
            raw_payload=raw_payload,
            event_id=event_id,
        )
    except AssessmentResultError as exc:
        return JsonResponse({"detail": str(exc)}, status=422)
    return JsonResponse(
        {
            "event_id": event.event_id,
            "duplicate": not result_applied,
            "result_applied": result_applied,
            "badge_awarded": badge_awarded,
        }
    )


@csrf_exempt
def paralearn_cron_reconcile(request):
    """Vercel Cron endpoint to run reconcile_paralearn_results on schedule."""
    if not settings.CRON_SECRET:
        return JsonResponse({"detail": "CRON_SECRET is not configured on this environment."}, status=503)
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {settings.CRON_SECRET}":
        return JsonResponse({"detail": "Unauthorized cron request."}, status=401)

    if not result_reconciliation_is_configured():
        return JsonResponse(
            {
                "status": "skipped",
                "detail": "ParaLearn reconciliation credentials are not configured.",
            },
            status=200,
        )

    out = io.StringIO()
    err = io.StringIO()
    try:
        call_command("reconcile_paralearn_results", stdout=out, stderr=err)
    except Exception as exc:
        return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    return JsonResponse(
        {
            "status": "success",
            "output": out.getvalue().strip(),
            "errors": err.getvalue().strip(),
        }
    )
