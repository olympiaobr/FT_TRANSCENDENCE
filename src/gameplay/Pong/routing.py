from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
	re_path(r'ws/gameplay/(?P<max_player>\w+)/(?P<lobby_id>\w+)/$',consumers.PongGame.as_asgi())
]