from rest_framework import serializers
from .models import GameData
from user_management.models import Profile
from django.contrib.auth.models import User
import re

class GameDataSerializer(serializers.ModelSerializer):
	players = serializers.ListField(
		child=serializers.CharField(),
		write_only=True
	)

	class Meta:
		model = GameData
		fields = ['id', 'gameMode', 'players', 'score', 'dateTime']

	def validate_gameMode(self, value):
		if value not in dict(GameData.GAME_MODES):
			raise serializers.ValidationError("Invalid gameMode. Valid options are: " +
												', '.join(dict(GameData.GAME_MODES).keys()))
		return value
	
	def validate_score(self, value):
		if not value:
			raise serializers.ValidationError({"score": "There is no score given"})
		isinstance(value, int):
		if not all(isinstance(score, int) and score >= 0 for score in value):
			raise serializers.ValidationError("All scores must be non-negative integers.")
		return value
	
	def validate_players(self, value):
		profiles = []
		if not value:
			raise serializers.ValidationError({"players": "There must at least exist one player"})
		for player_name in value:
			try:
				user = User.objects.get(username=player_name)
				profile = Profile.objects.get(user=user)
				profiles.append(profile)
			except User.DoesNotExist:
				raise serializers.ValidationError(f"User with username '{player_name}' does not exist.")
			except Profile.DoesNotExist:
				raise serializers.ValidationError(f"Profile for user '{player_name}' does not exist.")
		return profiles

	def validate(self, data):
		players = data.get("players",[])
		gameMode = data.get("gameMode")
		# number of players validation
		if not players:
			raise serializers.ValidationError({"players": "There must at least exist one player"})
		if gameMode == 'single-player' and len(players) != 1:
			raise serializers.ValidationError({"gameMode": f"Too many players for mode \'{gameMode}\'"})
		if gameMode == 'multi-player' and len(players) < 2:
			raise serializers.ValidationError({"gameMode": f"Not enough players for mode \'{gameMode}\'"})
		return data
	
	def create(self, validated_data):
		profiles = validated_data('players')
		game = GameData.objects.create(**validated_data)
		game.players.set(profiles)
		return game
	
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['players'] = [profile.user.username for profile in instance.players.all()]
		return representation
