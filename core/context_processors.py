from django.conf import settings


def curriculum_features(request):
    """Expose reviewed curriculum feature flags to the shared site shell."""
    return {
        "foundation_orientation_enabled": settings.FOUNDATION_ORIENTATION_ENABLED,
    }
