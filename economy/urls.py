from django.urls import path
from . import views

app_name = "economy"
urlpatterns = [
    path("introduction/", views.IntroductionView.as_view(), name="introduction"),
    path("representation_train/", views.RepresentationTrainView.as_view(), name="representation_train"),
    path("representation_pre/", views.RepresentationPreView.as_view(), name="representation_pre")
]