from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Lobby(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="Unique name for the lobby. Acts as an identifier."
    )
    current_player_count = models.PositiveIntegerField(
        default=0, 
        help_text="The number of players currently in the lobby. Maximum is 2."
    )
    p1 = models.CharField(
        default=None,
        max_length=100, 
        blank=True, 
        null=True,
        help_text="The first player in the lobby."
    )
    p2 = models.CharField(
        default=None,
        max_length=100, 
        blank=True, 
        null=True,
        help_text="The first player in the lobby."
    )
    password = models.CharField(
        max_length=128, 
        blank=True, 
        null=True, 
        help_text="Optional password for private lobbies."
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.name