from django.urls import path

from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("<slug:slug>/", views.course_detail, name="course_detail"),
    path("<slug:slug>/modules/<int:module_order>/", views.course_module_detail, name="course_module_detail"),
    path("<slug:slug>/assessment/", views.course_quiz, name="course_quiz"),
]
