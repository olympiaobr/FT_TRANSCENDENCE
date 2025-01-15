from django.urls import path
from . import views

urlpatterns = [
	path('addgame/', views.GameDataCreate.as_view(), name='add-game'),
	path('listgames/', views.GameDataList.as_view()),
    #path('gethistory/', views.gethistory_view, name='gethistory'),
]
