from django.urls import path
from . import views

app_name = "pop_traffic"
urlpatterns = [
    path("speedprediction_des", views.SpeedPredictionDes.as_view(), name="speedprediction_des"),
    path("speedprediction_pre", views.SpeedPredictionPre.as_view(), name="speedprediction_pre"),
    path("flowprediction_des", views.FlowPredictionDes.as_view(), name="flowprediction_des"),
    path("flowprediction_pre", views.FlowPredictionPre.as_view(), name="flowprediction_pre")
]