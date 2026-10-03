from django.urls import path

from . import views

urlpatterns = [
    path("", views.my_credentials, name="my_credentials"),
    path("badges/<uuid:uid>/png/", views.badge_png, name="badge_png"),
    path("badges/<uuid:uid>/pdf/", views.badge_pdf, name="badge_pdf"),
    path("certificates/<uuid:uid>/png/", views.certificate_png, name="certificate_png"),
    path("certificates/<uuid:uid>/pdf/", views.certificate_pdf, name="certificate_pdf"),
    path("verify/<uuid:uid>/", views.verify_credential, name="verify_credential"),
]
