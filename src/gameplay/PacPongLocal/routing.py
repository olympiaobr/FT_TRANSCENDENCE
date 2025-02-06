from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
	re_path(r'ws/gameplay/PacPong/local/(?P<max_score>\w+)/(?P<lobby_id>\w+)/$',consumers.PacPongGameLocal.as_asgi())
]