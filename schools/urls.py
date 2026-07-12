from django.urls import path

from . import views

urlpatterns = [
    path("", views.school_list, name="school_list"),
    path("<slug:slug>/", views.school_detail, name="school_detail"),
]
