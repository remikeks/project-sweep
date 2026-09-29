"""Provider-neutral content asset workflow used by staff APIs and future portals."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import CourseAsset


class WorkflowError(ValueError):
    pass


TRANSITIONS = {
    "submit": (CourseAsset.PublicationStatus.DRAFT, CourseAsset.PublicationStatus.IN_REVIEW),
    "approve": (CourseAsset.PublicationStatus.IN_REVIEW, CourseAsset.PublicationStatus.APPROVED),
    "publish": (CourseAsset.PublicationStatus.APPROVED, CourseAsset.PublicationStatus.PUBLISHED),
    "retire": (CourseAsset.PublicationStatus.PUBLISHED, CourseAsset.PublicationStatus.RETIRED),
}


def create_external_asset(*, user, course, module, payload):
    """Register an asset uploaded to external object storage, initially as a draft."""
    asset = CourseAsset(
        course=course,
        module=module,
        title=payload["title"],
        asset_type=payload["asset_type"],
        external_url=payload["external_url"],
        version=payload.get("version") or "1.0",
        language=payload.get("language") or "en",
        order=payload.get("order") or 0,
        is_downloadable=payload.get("is_downloadable", True),
        created_by=user,
    )
    asset.full_clean()
    asset.save()
    return asset


@transaction.atomic
def transition_asset(*, user, asset, action):
    try:
        expected_status, next_status = TRANSITIONS[action]
    except KeyError as exc:
        raise WorkflowError("Unknown content workflow action.") from exc
    if asset.status != expected_status:
        raise WorkflowError(
            f"Cannot {action} an asset while it is {asset.get_status_display().lower()}."
        )

    asset.status = next_status
    now = timezone.now()
    if action == "approve":
        asset.reviewed_by = user
        asset.reviewed_at = now
    elif action == "publish":
        asset.published_by = user
        asset.published_at = now
    asset.save()
    return asset
