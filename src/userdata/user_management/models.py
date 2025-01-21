from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.timezone import now

def defaultStats():
	initStats = dict()
	initStats["games-wins"] = 0
	initStats["games-losses"] = 0
	initStats["games-draws"] = 0
	initStats["games-played"] = 0
	initStats["ranking-score"] = 0
	return initStats

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	display_name = models.CharField(max_length=50, unique=True)
	avatar = models.ImageField(upload_to="avatars/", default="images/default_avatar.jpeg")
	friends = models.ManyToManyField("self", blank=True)
	stats = models.JSONField(default=defaultStats)
	twoFA_active = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username

class TwoFactorCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (now() - self.timestamp).seconds < 300
