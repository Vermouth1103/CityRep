from django.urls import path
from . import views

app_name = "indtraffic"
urlpatterns = [
    path("routeplan_des/", views.RoutePlanDesView.as_view(), name="routeplan_des"),
    path("routeplan_pre/", views.RoutePlanPreView.as_view(), name="routeplan_pre"),
    path("routeplan_upload/", views.RoutePlanUploadView.as_view(), name="routeplan_upload"),
    path("routeplan_train/", views.RoutePlanTrainView.as_view(), name="routeplan_train"),
    path("nextloc_des/", views.NextLocDesView.as_view(), name="nextloc_des"),
    path("nextloc_pre/", views.NextLocPreView.as_view(), name="nextloc_pre"),
    path("nextloc_upload/", views.NextLocUploadView.as_view(), name="nextloc_upload"),
    path("nextloc_train/", views.NextLocTrainView.as_view(), name="nextloc_train")
]