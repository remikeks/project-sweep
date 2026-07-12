from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("schools/<slug:slug>/enroll/", views.enroll_in_school_view, name="enroll_in_school"),
    path("courses/<slug:slug>/enroll/", views.enroll_in_course_view, name="enroll_in_course"),
    path("schools/<slug:slug>/exam/", views.school_exam, name="school_exam"),
]
