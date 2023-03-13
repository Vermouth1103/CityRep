# mysite_login/urls.py

from django.conf.urls import url
from django.contrib import admin
from . import views


app_name = "login"
urlpatterns = [
    url("^admin/", admin.site.urls),
    url("login/", views.LoginView().as_view(), name="login"),
    # url("register/", views.register),
]