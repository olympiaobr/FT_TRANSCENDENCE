from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import signup, profile, login_view, logout_view, profile_view

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
]
