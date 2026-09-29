"""Staff-only JSON contract for a future Supabase-hosted content portal.

The portal uploads files directly to its object storage and sends SWEEP an
external URL plus metadata. SWEEP remains the authority for the publication
workflow and what learners can see.
"""

import json

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from .content_workflow import WorkflowError, create_external_asset, transition_asset
from .models import Course, CourseAsset, CourseModule


def _payload(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError as exc:
        raise WorkflowError("Request body must be valid JSON.") from exc


def _asset_json(asset):
    return {
        "id": asset.id,
        "course_slug": asset.course.slug,
        "module_order": asset.module.order if asset.module_id else None,
        "title": asset.title,
        "asset_type": asset.asset_type,
        "external_url": asset.external_url,
        "version": asset.version,
        "language": asset.language,
        "status": asset.status,
        "order": asset.order,
        "is_downloadable": asset.is_downloadable,
        "reviewed_at": asset.reviewed_at.isoformat() if asset.reviewed_at else None,
        "published_at": asset.published_at.isoformat() if asset.published_at else None,
    }


@require_GET
@permission_required("courses.view_courseasset", raise_exception=True)
def content_catalog(request):
    courses = Course.objects.select_related("school").prefetch_related("modules", "assets")
    return JsonResponse({
        "courses": [
            {
                "slug": course.slug,
                "title": course.title,
                "school": course.school.name,
                "modules": [{"order": module.order, "title": module.title} for module in course.modules.all()],
                "assets": [_asset_json(asset) for asset in course.assets.all()],
            }
            for course in courses
        ]
    })


@require_POST
@permission_required("courses.add_courseasset", raise_exception=True)
def create_asset(request):
    try:
        payload = _payload(request)
        course = get_object_or_404(Course, slug=payload.get("course_slug"))
        module_order = payload.get("module_order")
        module = None
        if module_order is not None:
            module = get_object_or_404(CourseModule, course=course, order=module_order)
        asset = create_external_asset(user=request.user, course=course, module=module, payload=payload)
    except (WorkflowError, KeyError, ValueError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except ValidationError as exc:
        return JsonResponse({"ok": False, "error": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)
    return JsonResponse({"ok": True, "asset": _asset_json(asset)}, status=201)


@require_POST
@permission_required("courses.bulk_import_courseasset", raise_exception=True)
def import_assets(request):
    try:
        payload = _payload(request)
        rows = payload.get("assets")
        if not isinstance(rows, list) or not rows:
            raise WorkflowError("Provide a non-empty 'assets' list.")
        with transaction.atomic():
            created = []
            for row in rows:
                course = get_object_or_404(Course, slug=row.get("course_slug"))
                module = None
                if row.get("module_order") is not None:
                    module = get_object_or_404(CourseModule, course=course, order=row["module_order"])
                created.append(create_external_asset(user=request.user, course=course, module=module, payload=row))
    except (WorkflowError, KeyError, ValueError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except ValidationError as exc:
        return JsonResponse({"ok": False, "error": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)
    return JsonResponse({"ok": True, "assets": [_asset_json(asset) for asset in created]}, status=201)


@require_POST
def transition_asset_view(request, asset_id, action):
    required_permission = {
        "submit": "courses.change_courseasset",
        "approve": "courses.review_courseasset",
        "publish": "courses.publish_courseasset",
        "retire": "courses.publish_courseasset",
    }.get(action)
    if not required_permission or not request.user.has_perm(required_permission):
        return JsonResponse({"ok": False, "error": "You do not have permission for this action."}, status=403)
    asset = get_object_or_404(CourseAsset, pk=asset_id)
    try:
        asset = transition_asset(user=request.user, asset=asset, action=action)
    except WorkflowError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    return JsonResponse({"ok": True, "asset": _asset_json(asset)})
