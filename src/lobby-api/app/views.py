from django.http import JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
from .models import Lobby
import logging
import requests

logger = logging.getLogger(__name__)

def create_lobby(request):
    if request.method == 'POST':
        name = request.POST.get('lobby_name')
        raw_password = request.POST.get('lobby_password', '')
        print("name: " + name)
        auth_response = requests.get(
            "http://nginx:80/user-api/profile/",
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': request.headers.get('X-CSRFToken'),
            },
            cookies=request.COOKIES
        )

        if auth_response.status_code != 200:
            return JsonResponse({'error': 'Unauthorized user'}, status=401)
        
        try:
            lobby = Lobby(name=name)
            if raw_password:
                lobby.set_password(raw_password)
            lobby.save()

            return JsonResponse(
                {'message': 'Lobby created successfully!', 'lobby': lobby.id, 'lobby_name': lobby.name}, 
                status=201
            )        
        except IntegrityError:
            return JsonResponse(
            {'error': 'A lobby with this name already exists.'}, 
            status=400
            )

    return JsonResponse(
        {'error': 'Invalid request method. Only POST is allowed.'}, 
        status=405
    )

def get_lobby(request, lobby_id):
    if request.method == 'GET':
        try:
            lobby = Lobby.objects.get(id=lobby_id)
            # Return detailed information about the lobby
            lobby_data = {
                'id': lobby.id,
                'name': lobby.name,
                'current_player_count': lobby.current_player_count,
                'p1': lobby.p1,
                'p2': lobby.p2,
                'password_protected': bool(lobby.password), 
            }
            return JsonResponse({'message': 'Lobby retrieved successfully', 'lobby': lobby_data}, status=200)
        except Lobby.DoesNotExist:
            return JsonResponse({'error': 'Lobby not found'}, status=404)
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

    


def all(request):
    if request.method == 'GET':
        lobbies = Lobby.objects.all()

        lobby_list = []
        for lobby in lobbies:
            lobby_list.append({
                'id': lobby.id,
                'name': lobby.name,
                'current_player_count': lobby.current_player_count,
                'p1': lobby.p1,
                'p2': lobby.p2,
                'password_protected': bool(lobby.password), 
            })
        return JsonResponse(lobby_list, safe=False)
    
    return JsonResponse(
        {'error': 'Invalid request method. Only GET is allowed.'}, 
        status=405
    )

def player_joined(request, lobby_id):
    print(f"Received a POST request for lobby_id {lobby_id}")
    print(f"Request method: {request.method}")
    print(f"Request body: {request.body}")
    if request.method == "POST":
        try:
            lobby = Lobby.objects.get(id=lobby_id)
            if lobby.current_player_count == 2:
                return JsonResponse({'error': f'Lobby full'}, status=400)
            lobby.current_player_count += 1
            lobby.save()
            return JsonResponse({'message': f'Player joined lobby {lobby_id}'}, status=200)
        except Lobby.DoesNotExist:
            return JsonResponse({'error': 'Lobby not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def player_left(request, lobby_id, user_name):
    if request.method == "POST":
        try:
            lobby = Lobby.objects.get(id=lobby_id)
            lobby.current_player_count -= 1
            if lobby.p1 == user_name:
                lobby.p1 = None
            if lobby.p2 == user_name:
                lobby.p2 = None
            lobby.save()
            return JsonResponse({
            'roles': {
                'p1': f'{lobby.p1}',
                'p2': f'{lobby.p2}'
            },
            'cur_player': lobby.current_player_count
            }, status=200)
        except Lobby.DoesNotExist:
            return JsonResponse({'error': 'Lobby not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def delete_lobby_entry(request, lobby_id):
    if request.method == "POST":
        try:
            lobby = Lobby.objects.get(id=lobby_id)
            lobby.delete()  # Delete the lobby from the database
            return JsonResponse({'message': f'Lobby {lobby_id} deleted'}, status=200)
        except Lobby.DoesNotExist:
            return JsonResponse({'error': 'Lobby not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def select_player(request, player, lobby_id, user_name):
    if request.method == "POST" and player in ('p1', 'p2'):
        print("player_entry in POST request and player: p1 or p2")
        try:
            lobby = Lobby.objects.get(id=lobby_id)
        except Lobby.DoesNotExist:
            return JsonResponse({'error': 'Lobby not found'}, status=404)
        if player == 'p1' and lobby.p2 == user_name:
            lobby.p2 = None
        elif player == 'p2' and lobby.p1 == user_name:
            lobby.p1 = None
        setattr(lobby, player, user_name)
        lobby.save()
        return JsonResponse({'p1': f'{lobby.p1}', 'p2': f'{lobby.p2}'}, status=200)
    return JsonResponse({'error': 'Invalid method or player'}, status=405)


def desselect_player(request, player, lobby_id):
    if request.method == "POST" and player in ('p1', 'p2'):
        print("player_entry in POST request and player: p1 or p2")
        try:
            lobby = Lobby.objects.get(id=lobby_id)
        except Lobby.DoesNotExist:
            return JsonResponse({'error': 'Lobby not found'}, status=404)
        setattr(lobby, player, "None")
        lobby.save()
        return JsonResponse({'p1': f'{lobby.p1}', 'p2': f'{lobby.p2}'}, status=200)
    return JsonResponse({'error': 'Invalid method or player'}, status=405)

def get_players(request, lobby_id):
    if request.method == "GET":
        try:
            lobby = Lobby.objects.get(id=lobby_id)
            return JsonResponse({'p1': f'{lobby.p1}', 'p2': f'{lobby.p2}'}, status=200)
        except Lobby.DoesNotExist:
            return JsonResponse({'error': 'Lobby not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)