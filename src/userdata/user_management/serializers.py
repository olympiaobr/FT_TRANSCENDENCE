from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.db import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    friends = UserSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    stats = serializers.JSONField(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'display_name', 'avatar_url', 'friends', 'stats', 'password']

    def get_avatar_url(self, obj):
        """Return the avatar URL or a default if not set."""
        if obj.avatar:
            return obj.avatar.url  # URL for uploaded avatar
        return f"{settings.STATIC_URL}images/default-avatar.jpeg"

    def update(self, instance, validated_data):
        instance.display_name = validated_data.get('display_name', instance.display_name)

        avatar = validated_data.get('avatar')
        if avatar:
            instance.avatar.save(avatar.name, avatar)

        password = validated_data.pop('password', None)
        if password:
            instance.user.set_password(password)
            instance.user.save()

        instance.save()
        return instance
