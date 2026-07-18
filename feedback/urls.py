from django.urls import path

from . import views

urlpatterns = [
    path("submit/", views.submit_feedback, name="submit_feedback"),
]
