from django.urls import path

from . import views

urlpatterns = [
    path("content/", views.content_portal, name="content_portal"),
    path("content-api/catalog/", views.content_catalog, name="content_catalog"),
    path("content-api/uploads/sign/", views.create_upload_intent, name="create_content_upload_intent"),
    path("content-api/assets/", views.create_asset, name="create_course_asset"),
    path("content-api/assets/import/", views.import_assets, name="import_course_assets"),
    path("content-api/assets/<int:asset_id>/preview/", views.preview_asset, name="preview_course_asset"),
    path("content-api/assets/<int:asset_id>/replacement-upload/", views.create_replacement_upload_intent, name="create_course_asset_replacement_upload"),
    path("content-api/assets/<int:asset_id>/replace/", views.replace_asset, name="replace_course_asset"),
    path("content-api/assets/<int:asset_id>/<slug:action>/", views.transition_asset_view, name="transition_course_asset"),
    path("assets/<int:asset_id>/download/", views.course_asset_download, name="course_asset_download"),
    path("paralearn/webhook/", views.paralearn_result_webhook, name="paralearn_result_webhook"),
    path("<slug:slug>/assessment/launch/", views.paralearn_launch, name="paralearn_launch"),
    path("assessment-attempts/<uuid:attempt_id>/retry/", views.paralearn_retry_launch, name="paralearn_retry_launch"),
    path("assessment-attempts/<uuid:attempt_id>/reconcile/", views.paralearn_reconcile_result, name="paralearn_reconcile_result"),
    path("", views.course_list, name="course_list"),
    path("<slug:slug>/", views.course_detail, name="course_detail"),
    path("<slug:slug>/modules/<int:module_order>/", views.course_module_detail, name="course_module_detail"),
    path("<slug:slug>/modules/<int:module_order>/complete/", views.complete_course_module, name="complete_course_module"),
    path("<slug:slug>/assessment/", views.course_quiz, name="course_quiz"),
]
