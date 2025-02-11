from django.urls import re_path
from .consumers import LobbyConsumer
from .tournament_consumers import TournamentConsumer

websocket_urlpatterns = [
    re_path(r'ws/lobby/tournament/(?P<lobby_id>\w+)/(?P<user_name>\w+)/$', TournamentConsumer.as_asgi()),
    re_path(r'ws/lobby/(?P<pac_pong>\w+)/(?P<lobby_id>\w+)/(?P<user_name>\w+)/$', LobbyConsumer.as_asgi()),
]