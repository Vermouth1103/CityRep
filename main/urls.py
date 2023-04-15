from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required


app_name = "main"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]