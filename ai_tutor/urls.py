from django.urls import path

from . import views

urlpatterns = [
    path("ask/", views.tutor_ask, name="tutor_ask"),
]
