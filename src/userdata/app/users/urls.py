from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import signup, profile, login_view, logout_view, profile_view

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("profile/", profile, name="profile"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
