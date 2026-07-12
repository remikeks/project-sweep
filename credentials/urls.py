from django.urls import path

from . import views

urlpatterns = [
    path("", views.my_credentials, name="my_credentials"),
]
