"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lobby/create/', views.create_lobby),
    path('lobby/<int:lobby_id>/', views.get_lobby),
    path('lobby/all/', views.all),
    path('lobby/player_joined/<int:lobby_id>/', views.player_joined),
    path('lobby/player_left/<int:lobby_id>/<str:user_name>/', views.player_left),
    path('lobby/delete/<int:lobby_id>/', views.delete_lobby_entry),
    path('lobby/players/<int:lobby_id>/', views.get_players),
    path('lobby/player_select/<str:player>/<int:lobby_id>/<str:user_name>/', views.select_player),
    path('lobby/player_deselect/<str:player>/<int:lobby_id>/', views.desselect_player),
]
