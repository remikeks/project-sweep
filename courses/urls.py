from django.urls import path

from . import views

urlpatterns = [
    path("content-api/catalog/", views.content_catalog, name="content_catalog"),
    path("content-api/assets/", views.create_asset, name="create_course_asset"),
    path("content-api/assets/import/", views.import_assets, name="import_course_assets"),
    path("content-api/assets/<int:asset_id>/<slug:action>/", views.transition_asset_view, name="transition_course_asset"),
    path("", views.course_list, name="course_list"),
    path("<slug:slug>/", views.course_detail, name="course_detail"),
    path("<slug:slug>/modules/<int:module_order>/", views.course_module_detail, name="course_module_detail"),
    path("<slug:slug>/assessment/", views.course_quiz, name="course_quiz"),
]
