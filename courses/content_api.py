"""Authenticated JSON endpoints for the SWEEP content-admin portal."""

import json
import re
from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .content_auth import (
    PortalAuthenticationError,
    PortalConfigurationError,
    content_actor_from_request,
    require_content_permission,
)
from .content_storage import (
    StorageConfigurationError,
    StorageRequestError,
    SupabaseStorageClient,
    build_storage_path,
    canonical_storage_url,
    validate_upload_metadata,
)
from .content_workflow import WorkflowError, create_external_asset, transition_asset
from .models import ContentUploadIntent, Course, CourseAsset, CourseModule

_VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,2}(?:[-+][A-Za-z0-9.-]+)?$")
_LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})?$")
_url_validator = URLValidator(schemes=["https"])


def _error(message, status=400):
    return JsonResponse({"ok": False, "error": message}, status=status)


def _payload(request, *, max_bytes=None):
    if max_bytes is not None:
        try:
            content_length = int(request.META.get("CONTENT_LENGTH") or 0)
        except ValueError:
            raise WorkflowError("Request Content-Length is invalid.")
        if content_length > max_bytes:
            raise WorkflowError("Request body is too large.")
    try:
        raw = request.body or b"{}"
        if max_bytes is not None and len(raw) > max_bytes:
            raise WorkflowError("Request body is too large.")
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise WorkflowError("Request body must be valid JSON.") from exc
    if not isinstance(value, dict):
        raise WorkflowError("Request body must be a JSON object.")
    return value


def _asset_json(asset):
    return {
        "id": asset.id,
        "course_slug": asset.course.slug,
        "module_order": asset.module.order if asset.module_id else None,
        "title": asset.title,
        "asset_type": asset.asset_type,
        "external_url": asset.external_url,
        "storage_path": asset.storage_path,
        "original_filename": asset.original_filename,
        "content_type": asset.content_type,
        "size_bytes": asset.size_bytes,
        "version": asset.version,
        "language": asset.language,
        "status": asset.status,
        "order": asset.order,
        "is_downloadable": asset.is_downloadable,
        "created_by": asset.created_by_id,
        "reviewed_at": asset.reviewed_at.isoformat() if asset.reviewed_at else None,
        "published_at": asset.published_at.isoformat() if asset.published_at else None,
        "retired_at": asset.retired_at.isoformat() if asset.retired_at else None,
        "replaces": asset.replaces_id,
    }


def _resolve_placement(payload):
    slug = payload.get("course_slug")
    if not isinstance(slug, str) or not slug.strip():
        raise WorkflowError("course_slug is required.")
    course = Course.objects.filter(slug=slug.strip()).first()
    if not course:
        raise WorkflowError("The selected course does not exist.")
    module_order = payload.get("module_order")
    if module_order is None:
        return course, None
    if isinstance(module_order, bool) or not isinstance(module_order, int) or module_order < 0:
        raise WorkflowError("module_order must be a non-negative integer or null.")
    module = CourseModule.objects.filter(course=course, order=module_order).first()
    if not module:
        raise WorkflowError("The selected module does not belong to this course.")
    return course, module


def _validate_common_asset_fields(payload):
    title = payload.get("title")
    if not isinstance(title, str) or not (title := title.strip()) or len(title) > 200:
        raise WorkflowError("title is required and must be 200 characters or fewer.")
    asset_type = payload.get("asset_type")
    valid_types = {value for value, _ in CourseAsset.AssetType.choices}
    if asset_type not in valid_types:
        raise WorkflowError("asset_type is not supported.")
    version = payload.get("version", "1.0")
    if not isinstance(version, str) or not _VERSION_RE.fullmatch(version) or len(version) > 40:
        raise WorkflowError("version must be a semantic version such as 1.0 or 2.1.3.")
    language = payload.get("language", "en")
    if not isinstance(language, str) or not _LANGUAGE_RE.fullmatch(language) or len(language) > 20:
        raise WorkflowError("language must be a simple BCP 47 code such as en or en-GB.")
    order = payload.get("order", 0)
    if isinstance(order, bool) or not isinstance(order, int) or not 0 <= order <= 32767:
        raise WorkflowError("order must be a non-negative number no greater than 32767.")
    is_downloadable = payload.get("is_downloadable", True)
    if not isinstance(is_downloadable, bool):
        raise WorkflowError("is_downloadable must be true or false.")
    return {
        "title": title,
        "asset_type": asset_type,
        "version": version,
        "language": language,
        "order": order,
        "is_downloadable": is_downloadable,
    }


def _validated_external_url(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise WorkflowError("external_url is required and must be a secure HTTPS URL.")
    value = value.strip()
    try:
        _url_validator(value)
    except ValidationError as exc:
        raise WorkflowError("external_url must be a secure HTTPS URL.") from exc
    parsed = urlparse(value)
    if not parsed.netloc or parsed.username or parsed.password or parsed.fragment:
        raise WorkflowError("external_url is not a safe asset URL.")
    return value


def _intent_for_payload(*, raw_intent_id, actor, course, module, replacement_for=None):
    if not raw_intent_id:
        return None
    try:
        intent = ContentUploadIntent.objects.select_related("course", "module").get(pk=raw_intent_id)
    except (ContentUploadIntent.DoesNotExist, ValueError, TypeError) as exc:
        raise WorkflowError("The upload authorization is invalid.") from exc
    if intent.requested_by_id != actor.user.id:
        raise WorkflowError("This upload authorization belongs to a different author.")
    if intent.consumed_at or intent.expires_at <= timezone.now():
        raise WorkflowError("This upload authorization has expired. Start the upload again.")
    if intent.course_id != course.id or intent.module_id != (module.id if module else None):
        raise WorkflowError("This upload authorization does not match the selected course or module.")
    if intent.replacement_for_id != (replacement_for.id if replacement_for else None):
        raise WorkflowError("This upload authorization does not match this replacement.")
    return intent


def _asset_payload_from_request(payload, *, actor, course, module, allow_storage_without_intent=False, replacement_for=None):
    cleaned = _validate_common_asset_fields(payload)
    intent = _intent_for_payload(
        raw_intent_id=payload.get("upload_intent_id"),
        actor=actor,
        course=course,
        module=module,
        replacement_for=replacement_for,
    )
    if intent:
        if intent.asset_type != cleaned["asset_type"]:
            raise WorkflowError("The selected asset type does not match the signed upload.")
        cleaned.update(
            {
                "external_url": canonical_storage_url(intent.storage_path),
                "storage_path": intent.storage_path,
                "original_filename": intent.original_filename,
                "content_type": intent.content_type,
                "size_bytes": intent.size_bytes,
            }
        )
        return cleaned, intent
    external_url = _validated_external_url(payload.get("external_url"))
    storage_path = payload.get("storage_path", "")
    if storage_path:
        if not allow_storage_without_intent:
            raise WorkflowError("Register Supabase uploads using the one-use upload authorization.")
        try:
            expected_url = canonical_storage_url(storage_path)
        except (StorageConfigurationError, ValueError) as exc:
            raise WorkflowError("storage_path cannot be validated against the configured Supabase bucket.") from exc
        if external_url != expected_url:
            raise WorkflowError("external_url does not match the configured storage object path.")
    cleaned.update({"external_url": external_url, "storage_path": storage_path})
    return cleaned, None


def _can_submit(actor, asset):
    return actor.is_superuser or asset.created_by_id == actor.user.id


def _can_create_replacement(actor, asset):
    return actor.is_superuser or asset.created_by_id == actor.user.id


def _create_intent(*, actor, payload, replacement_for=None):
    course, module = _resolve_placement(payload)
    asset_type = payload.get("asset_type")
    filename = payload.get("filename")
    content_type = payload.get("content_type", "").lower() if isinstance(payload.get("content_type"), str) else ""
    size_bytes = payload.get("size_bytes")
    try:
        validate_upload_metadata(asset_type=asset_type, filename=filename, content_type=content_type, size_bytes=size_bytes)
        client = SupabaseStorageClient()
        storage_path = build_storage_path(
            course_slug=course.slug,
            module_order=module.order if module else None,
            filename=filename,
        )
        signed_upload = client.create_signed_upload_url(storage_path)
    except (StorageConfigurationError, StorageRequestError, ValueError) as exc:
        raise WorkflowError(str(exc)) from exc
    intent = ContentUploadIntent.objects.create(
        course=course,
        module=module,
        requested_by=actor.user,
        replacement_for=replacement_for,
        storage_path=storage_path,
        original_filename=filename.strip(),
        asset_type=asset_type,
        content_type=content_type,
        size_bytes=size_bytes,
        expires_at=signed_upload.expires_at,
    )
    return intent, signed_upload


@require_GET
@require_content_permission("courses.view_courseasset")
def content_catalog(request):
    courses = Course.objects.select_related("school").prefetch_related(
        "modules", Prefetch("assets", queryset=CourseAsset.objects.select_related("module"))
    )
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
@require_content_permission("courses.add_courseasset")
def create_upload_intent(request):
    try:
        intent, signed_upload = _create_intent(
            actor=request.content_actor, payload=_payload(request, max_bytes=16 * 1024)
        )
    except WorkflowError as exc:
        return _error(str(exc), 503 if "unavailable" in str(exc).lower() else 400)
    return JsonResponse({
        "ok": True,
        "upload_intent_id": str(intent.id),
        "upload_url": signed_upload.url,
        "storage_path": signed_upload.storage_path,
        "external_url": canonical_storage_url(signed_upload.storage_path),
        "expires_at": signed_upload.expires_at.isoformat(),
    }, status=201)


@require_POST
@require_content_permission("courses.add_courseasset")
def create_asset(request):
    try:
        payload = _payload(request)
        course, module = _resolve_placement(payload)
        cleaned, intent = _asset_payload_from_request(payload, actor=request.content_actor, course=course, module=module)
        with transaction.atomic():
            asset = create_external_asset(user=request.content_actor.user, course=course, module=module, payload=cleaned)
            if intent:
                intent.consumed_at = timezone.now()
                intent.save(update_fields=["consumed_at"])
    except (WorkflowError, ValueError) as exc:
        return _error(str(exc))
    except ValidationError as exc:
        return _error(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
    return JsonResponse({"ok": True, "asset": _asset_json(asset)}, status=201)


@require_POST
@require_content_permission("courses.bulk_import_courseasset")
def import_assets(request):
    try:
        payload = _payload(request, max_bytes=settings.CONTENT_PORTAL_MAX_IMPORT_BYTES)
        rows = payload.get("assets")
        if not isinstance(rows, list) or not rows:
            raise WorkflowError("Provide a non-empty 'assets' list.")
        if len(rows) > settings.CONTENT_PORTAL_MAX_IMPORT_ROWS:
            raise WorkflowError(f"Import is limited to {settings.CONTENT_PORTAL_MAX_IMPORT_ROWS} assets at a time.")
        resolved = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                raise WorkflowError(f"Asset {index} must be a JSON object.")
            course, module = _resolve_placement(row)
            cleaned, intent = _asset_payload_from_request(
                row, actor=request.content_actor, course=course, module=module, allow_storage_without_intent=True
            )
            if intent:
                raise WorkflowError("Bulk imports cannot consume interactive upload authorizations.")
            resolved.append((course, module, cleaned))
        with transaction.atomic():
            created = [
                create_external_asset(user=request.content_actor.user, course=course, module=module, payload=cleaned)
                for course, module, cleaned in resolved
            ]
    except (WorkflowError, ValueError) as exc:
        return _error(str(exc))
    except ValidationError as exc:
        return _error(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
    return JsonResponse({"ok": True, "assets": [_asset_json(asset) for asset in created]}, status=201)


@require_POST
@require_content_permission("courses.add_courseasset")
def create_replacement_upload_intent(request, asset_id):
    asset = get_object_or_404(CourseAsset, pk=asset_id)
    if not _can_create_replacement(request.content_actor, asset):
        return _error("Only the original author may prepare a replacement for this asset.", 403)
    if asset.status not in {CourseAsset.PublicationStatus.PUBLISHED, CourseAsset.PublicationStatus.RETIRED}:
        return _error("Only a published or retired asset can be replaced.")
    try:
        payload = _payload(request, max_bytes=16 * 1024)
        payload["course_slug"] = asset.course.slug
        payload["module_order"] = asset.module.order if asset.module_id else None
        intent, signed_upload = _create_intent(actor=request.content_actor, payload=payload, replacement_for=asset)
    except WorkflowError as exc:
        return _error(str(exc), 503 if "unavailable" in str(exc).lower() else 400)
    return JsonResponse({
        "ok": True,
        "upload_intent_id": str(intent.id),
        "upload_url": signed_upload.url,
        "storage_path": signed_upload.storage_path,
        "external_url": canonical_storage_url(signed_upload.storage_path),
        "expires_at": signed_upload.expires_at.isoformat(),
    }, status=201)


@require_POST
@require_content_permission("courses.add_courseasset")
def replace_asset(request, asset_id):
    asset = get_object_or_404(CourseAsset, pk=asset_id)
    if not _can_create_replacement(request.content_actor, asset):
        return _error("Only the original author may replace this asset.", 403)
    if asset.status not in {CourseAsset.PublicationStatus.PUBLISHED, CourseAsset.PublicationStatus.RETIRED}:
        return _error("Only a published or retired asset can be replaced.")
    try:
        payload = _payload(request)
        payload["course_slug"] = asset.course.slug
        payload["module_order"] = asset.module.order if asset.module_id else None
        course, module = _resolve_placement(payload)
        cleaned, intent = _asset_payload_from_request(
            payload, actor=request.content_actor, course=course, module=module, replacement_for=asset
        )
        with transaction.atomic():
            replacement = create_external_asset(
                user=request.content_actor.user, course=course, module=module, payload={**cleaned, "replaces": asset}
            )
            if intent:
                intent.consumed_at = timezone.now()
                intent.save(update_fields=["consumed_at"])
    except (WorkflowError, ValueError) as exc:
        return _error(str(exc))
    except ValidationError as exc:
        return _error(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
    return JsonResponse({"ok": True, "asset": _asset_json(replacement)}, status=201)


@require_GET
@require_content_permission("courses.view_courseasset")
def preview_asset(request, asset_id):
    asset = get_object_or_404(CourseAsset, pk=asset_id)
    try:
        if asset.storage_path:
            url = SupabaseStorageClient().create_signed_download_url(asset.storage_path)
            expires_at = timezone.now() + timedelta(seconds=min(max(int(settings.SUPABASE_STORAGE_SIGNED_URL_TTL), 60), 7200))
        elif asset.external_url:
            url = asset.external_url
            expires_at = None
        elif asset.file:
            url = asset.file.url
            expires_at = None
        else:
            raise WorkflowError("This asset has no previewable file.")
    except (StorageConfigurationError, StorageRequestError, WorkflowError) as exc:
        return _error(str(exc), 503)
    return JsonResponse({"ok": True, "url": url, "expires_at": expires_at.isoformat() if expires_at else None})


@require_POST
def transition_asset_view(request, asset_id, action):
    required_permission = {
        "submit": "courses.change_courseasset",
        "approve": "courses.review_courseasset",
        "publish": "courses.publish_courseasset",
        "retire": "courses.publish_courseasset",
    }.get(action)
    if not required_permission:
        return _error("Unknown content workflow action.")
    try:
        actor = content_actor_from_request(request)
    except PortalConfigurationError as exc:
        return _error(str(exc), 503)
    except PortalAuthenticationError as exc:
        return _error(str(exc), 401)
    if not actor.is_superuser and not actor.has_perm(required_permission):
        return _error("You do not have permission for this action.", 403)
    asset = get_object_or_404(CourseAsset, pk=asset_id)
    if action == "submit" and not _can_submit(actor, asset):
        return _error("Only the original author may submit this draft for review.", 403)
    try:
        asset = transition_asset(user=actor.user, asset=asset, action=action)
    except WorkflowError as exc:
        return _error(str(exc))
    return JsonResponse({"ok": True, "asset": _asset_json(asset)})
