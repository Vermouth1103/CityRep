from django.urls import path
from . import views

app_name = "accident"
urlpatterns = [
    path("accident_des/", views.AccidentDesView.as_view(), name="accident_des"),
    path("accident_pre/", views.AccidentPreView.as_view(), name="accident_pre"),
    path("accident_upload/", views.AccidentUploadView.as_view(), name="accident_upload")
]