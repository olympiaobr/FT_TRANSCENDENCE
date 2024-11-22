from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png")
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.user.username

