from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("schools/", include("schools.urls")),
    path("courses/", include("courses.urls")),
    path("learning/", include("learning.urls")),
    path("credentials/", include("credentials.urls")),
    path("ai-tutor/", include("ai_tutor.urls")),
    path("feedback/", include("feedback.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Badges/certificates no longer depend on this (see credentials/views.py —
# they're rendered on demand instead of read from MEDIA_ROOT). This is kept
# so other MEDIA_URL uploads (e.g. school icons) still resolve on a live
# deploy and not only when DEBUG=True.
#
# NOTE: django.conf.urls.static.static() silently returns an empty list
# whenever DEBUG=False (that's the actual reason badge/certificate images
# 404'd on Render even before the rest of today's fix) — it is NOT just a
# "use this in dev" convention, it's a hard no-op in production. So this
# uses the underlying view directly instead. It still only serves files
# that exist on THIS instance's local disk right now — /media/ is
# gitignored and Render's disk is ephemeral, so anything else stored under
# MEDIA_ROOT (e.g. admin-uploaded school icons) should move to persistent/
# cloud storage or be committed as a static asset instead.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", static_serve, {"document_root": settings.MEDIA_ROOT}),
]
