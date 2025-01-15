from django.db import models
from user_management.models import Profile
from django.utils.timezone import now
import logging

class GameData(models.Model):
	GAME_MODES = [
		('single-player', 'Single Player'),
		('multi-player', 'Multi Player')
	]
	gameMode = models.CharField(max_length=30, choices=GAME_MODES)
	players = models.ManyToManyField(Profile, related_name="games")
	gameFinished = models.BooleanField(default=True)
	score = models.JSONField(default=list)
	dateTime = now()
	
	def __str__(self):
		player_names = [player.user.username for player in self.players.all()]
		score_strings = [str(points)  for points in self.score]
		return (str(self.dateTime) + ':' + 'players:' + ", ".join(player_names) + 
				'\tscore: ' + "-".join(score_strings))
