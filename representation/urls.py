from django.urls import path
from . import views

app_name = "representation"
urlpatterns = [
    path("representation_des/", views.RepresentationDesView.as_view(), name="representation_des"),
    path("model_des/", views.ModelDesView.as_view(), name="model_des"),
    path("data_des/", views.DataDesView.as_view(), name="data_des"),
    path("model_train/", views.ModelTrainView.as_view(), name="model_train"),
    path("model_pre/", views.ModelPreView.as_view(), name="model_pre")
]