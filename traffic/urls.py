from django.urls import path
from . import views

app_name = "traffic"
urlpatterns = [
    path("introduction/", views.IntroductionView.as_view(), name="introduction"),
    path("representation_train/", views.RepresentationTrainView.as_view(), name="representation_train"),
    path("representation_upload/", views.RepresentationUploadView.as_view(), name="representation_upload"),
    path("representation_pre/", views.RepresentationPreView.as_view(), name="representation_pre"),
    path("speed_prediction/", views.SpeedPredicitonView.as_view(), name="speed_prediction"),
    path("flow_prediction/", views.FlowPredictionView.as_view(), name="flow_prediction"),
    path("route_plan/", views.RoutePlanView.as_view(), name="route_plan"),
    path("route_plan_upload/", views.RoutePlanUploadView.as_view(), name="route_plan_upload"),
    path("route_plan_train/", views.RoutePlanTrainView.as_view(), name="route_plan_train"),
    path("next_loc_prediction/", views.NextLocPredictionView.as_view(), name="next_loc_prediction"),
    path("next_loc_prediction_upload/", views.NextLocPredictionUploadView.as_view(), name="next_loc_prediction_upload"),
    path("next_loc_prediction_train/", views.NextLocPredictionTrainView.as_view(), name="next_loc_prediction_train"),
    path("accident/", views.AccidentView.as_view(), name="accident"),
    path("accident_upload/", views.AccidentUploadView.as_view(), name="accident_upload")
]