from django.urls import path
from . import views
from main.views import IndexView 

app_name = "login"
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout")
]