from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png")
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        base_display_name = instance.username
        unique_display_name = base_display_name
        while Profile.objects.filter(display_name=unique_display_name).exists():
            unique_display_name = f"{base_display_name}_{get_random_string(5)}"

        Profile.objects.create(user=instance, display_name=unique_display_name)
