from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.db import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.settings import api_settings

class UserSerializer(serializers.ModelSerializer):
    twoFA_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'twoFA_active']

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
        if obj.avatar:
            return obj.avatar.url
        return f"{settings.STATIC_URL}images/default_avatar.jpeg"

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

class TokenWith2FASerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        jwt_data = super().validate(attrs)
        token_instance = self.get_token(self.user)

        if self.user.profile.is_2fa_enabled:
            token_instance['2fa_verified'] = False
        else:
            token_instance['2fa_verified'] = True

        jwt_data['refresh'] = str(token_instance)
        jwt_data['access'] = str(token_instance.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return jwt_data
