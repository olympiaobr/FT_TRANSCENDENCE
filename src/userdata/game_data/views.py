import logging
from django.shortcuts import render, redirect
from django.db import IntegrityError
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import HttpResponse
from .serializers import GameDataSerializer
from .models import GameData
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)

class GameDataCreate(generics.CreateAPIView):
    # API endpoint that allows creation of a new customer
    logger.info("Game creation request recieved")
    queryset = GameData.objects.all()
    serializer_class = GameDataSerializer


class GameDataList(generics.ListAPIView):
    # API endpoint that allows customer to be viewed.
    queryset = GameData.objects.all()
    serializer_class = GameDataSerializer

@api_view(['POST'])
def addgame_view(request):
    logger.info("Game data upload request received.")
    