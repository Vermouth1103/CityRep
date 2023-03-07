from django.urls import path
from . import views

app_name = "ind_traffic"
urlpatterns = [
    path("routeplan_des", views.RoutePlanDes.as_view(), name="routeplan_des"),
    path("routeplan_pre", views.RoutePlanPre.as_view(), name="routeplan_pre"),
    path("nextloc_des", views.NextLocDes.as_view(), name="nextloc_des"),
    path("nextloc_pre", views.NextLocPre.as_view(), name="nextloc_pre")
]