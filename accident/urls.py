from django.urls import path
from . import views

app_name = "accident"
urlpatterns = [
    path("accident_des", views.AccidentDes.as_view(), name="accident_des"),
    path("accident_pre", views.AccidentPre.as_view(), name="accident_pre")
]