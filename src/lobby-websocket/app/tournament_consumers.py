from channels.generic.websocket import AsyncWebsocketConsumer
import json
import httpx
import random
import logging
logger = logging.getLogger(__name__)

class PlayerSlots:
    def __init__(self):
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None
    def reset(self):
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None

class PlayerSlotsRound2:
    def __init__(self):
        self.p1 = None
        self.p2 = None
    def reset(self):
        self.p1 = None
        self.p2 = None

class LobbySession:
    def __init__(self):
        self.enable_start = True
        self.enable_game3 = True
        self.player_names = {}
        self.player_ready = []
        self.players = PlayerSlots()
        self.players2 = PlayerSlotsRound2()


class TournamentConsumer(AsyncWebsocketConsumer):

    LobbySessions = {}

	################## CONNECT ##################

    async def connect(self):
        self.lobby_id = self.scope['url_route']['kwargs']['lobby_id']
        self.user_name = self.scope["url_route"]["kwargs"]["user_name"]
        self.lobby_group_name = f"lobby_{self.lobby_id}"
        self.roles = {"p1": None, "p2": None, "p3": None, "p4": None}

        self.cookies = self.scope.get('cookies', {})
        self.csrf_token = self.cookies.get('csrftoken', None)

        if self.csrf_token:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://nginx:80/user-api/profile/",
                    headers={
                        'Content-Type': 'application/json',
                        'X-CSRFToken': self.csrf_token,
                    },
                    cookies=self.cookies,
                )
                if response.status_code != 200:
                    await self.close(code=4001)
                    return
        else:
            await self.close(code=4001)
            return
        
        await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name
        )        
        if self.lobby_group_name not in self.LobbySessions:
            self.LobbySessions[self.lobby_group_name] = LobbySession()
        self.lobby_session = self.LobbySessions[self.lobby_group_name]
        
        await self.accept()

	################## RECEIVE ##################

    async def receive(self, text_data):
        # Handle messages from the WebSocket
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'player_joined':
            player_joined_success = await self.player_joined()

            if player_joined_success:
                self.lobby_session.player_names[self.user_name] = self.channel_name
                await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'send_player_joined',
                    'player_names' : self.lobby_session.player_names
                }
            )
            else:
                await self.disconnect(4001)

        elif action == 'restart_tournament':
            self.lobby_session.players.reset()
            self.lobby_session.players2.reset()
            self.lobby_session.enable_game3 = True
            self.assign_roles()
            await self.start_tournament()

        elif action == 'start_tournament':
            self.lobby_session.enable_start = False
            await self.start_tournament()

        elif action == 'start_game_1':
            await self.send_2players(
                self.lobby_session.player_names.get(self.lobby_session.players.p1), 
                self.lobby_session.player_names.get(self.lobby_session.players.p2), 
                'start_game_1'
                )
        elif action == 'start_game_2':
            await self.send_2players(
                self.lobby_session.player_names.get(self.lobby_session.players.p3), 
                self.lobby_session.player_names.get(self.lobby_session.players.p4), 
                'start_game_2'
                )
        elif action == 'start_game_3':
            await self.send_2players(
                self.lobby_session.player_names.get(self.lobby_session.players2.p1), 
                self.lobby_session.player_names.get(self.lobby_session.players2.p2), 
                'start_game_3'
                )
        elif action == 'p1_win':
            self.lobby_session.players2.p1 = data.get('winner')
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'send_p1_round2',
                    'p1_round2' : self.lobby_session.players2.p1,
                }
            )
        elif action == 'p2_win':
            self.lobby_session.players2.p2 = data.get('winner')
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'send_p2_round2',
                    'p2_round2' : self.lobby_session.players2.p2,
                }
            )
        elif action == 'winner':
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'send_winner',
                    'winner' : data.get('winner'),
                }
            )

        if (self.lobby_session.players2.p1 != None and self.lobby_session.players2.p2 != None and self.lobby_session.enable_game3):
            self.lobby_session.enable_game3 = False
            await self.send_2players(
                self.lobby_session.player_names.get(self.lobby_session.players2.p1), 
                self.lobby_session.player_names.get(self.lobby_session.players2.p2), 
                'enable_3'
                )


        if len(self.lobby_session.player_names) == 4 and self.lobby_session.enable_start:
            self.assign_roles()
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'enable_tournament_button',
                    'message' : 'tournament button enabled',
                }
            )
        elif len(self.lobby_session.player_names) == 4 and self.lobby_session.enable_start:
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'enable_reset_button',
                    'message' : 'tournament reset button enabled',
                }
            )
    
        else :
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'disable_tournament_button',
                    'message' : 'tournament button disabled'
                }
            )


    def assign_roles(self):
        player_list = list(self.lobby_session.player_names.keys())
        random.shuffle(player_list)        
        self.lobby_session.players.p1 = self.lobby_session.player_names[0]
        self.lobby_session.players.p2 = self.lobby_session.player_names[1]
        self.lobby_session.players.p3 = self.lobby_session.player_names[2]
        self.lobby_session.players.p4 = self.lobby_session.player_names[3]

    def get_assigned_roles(self):
        return {
            'p1': self.lobby_session.players.p1,
            'p2': self.lobby_session.players.p2,
            'p3': self.lobby_session.players.p3,
            'p4': self.lobby_session.players.p4,
        }
    
    async def start_tournament(self):
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'send_start_tournament',
                'roles' : self.get_assigned_roles(),
            }
        )
        await self.send_2players(
            self.lobby_session.player_names.get(self.lobby_session.players.p1), 
            self.lobby_session.player_names.get(self.lobby_session.players.p2), 
            'enable_start_1'
        )
        await self.send_2players(
            self.lobby_session.player_names.get(self.lobby_session.players.p1), 
            self.lobby_session.player_names.get(self.lobby_session.players.p2), 
            'enable_start_2'
        )
    
    async def send_start_tournament(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_tournament',
            'roles': event['roles']
        }))

    async def send_2players(self, player1, player2, event_type):
        if player1:
            await self.channel_layer.send(
                player1,
                {
                    'type': event_type,
                    'message': 'ok'
                }
            )
        if player2:
            await self.channel_layer.send(
                player2,
                {
                    'type': event_type,
                    'message': 'ok'
                }
            )

    async def send_winner(self, event):
        await self.send(text_data=json.dumps({
            'type': 'winner',
            'winner' : event['winner']
        })) 

    async def send_p1_round2(self, event):
        await self.send(text_data=json.dumps({
            'type': 'p1_round2',
            'p1_round2' : event['p1_round2']
        }))  

    async def send_p2_round2(self, event):
        await self.send(text_data=json.dumps({
            'type': 'p2_round2',
            'p2_round2' : event['p2_round2']
        }))  

    async def send_player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player_names' : event['player_names']
        }))       

    async def enable_tournament_button(self, event):
        await self.send(text_data=json.dumps({
            'type': 'enable_tournament_button',
            'message' : event['message']
        }))

    async def disable_tournament_button(self, event):
        await self.send(text_data=json.dumps({
            'type': 'disable_tournament_button',
            'message' : event['message']
        }))

    async def start_1(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_1',
            'message' : event['message']
        }))
    async def start_2(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_2',
            'message' : event['message']
        }))
    async def start_3(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_3',
            'message' : event['message']
        }))   

    async def player_joined(self):
        url = f"http://nginx:80/lobby/player_joined/{self.lobby_id}/{self.user_name}/"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={'key': 'value'})
            if response.status_code != 200:
                return False
            return True


	################## DISCONNECT ##################

    async def disconnect(self, close_code):

        if close_code == 4001:
            return
        elif close_code != 4003:
            del self.lobby_session.player_names[self.user_name]
            if await self.player_left() == 0:
                await self.delete_lobby_entry()

        await self.channel_layer.group_discard(
            self.lobby_group_name,
            self.channel_name
        )

    async def player_left(self):
        url = f"http://nginx:80/lobby/player_left/{self.lobby_id}/{self.user_name}/"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={'key': 'value'})
            if response.status_code != 200:
                print(f"Failed to leave lobby {self.lobby_id}: {response.text}")
                return
            
            data = response.json()
            self.roles = data.get('roles', {})

            await self.update_roles()
            return data.get('cur_player')

    async def delete_lobby_entry(self):
        url = f"http://nginx:80/lobby/delete/{self.lobby_id}/"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                    url,
                    headers={
                        'Content-Type': 'application/json',
                        'X-CSRFToken': self.csrf_token,
                    },
                    cookies=self.cookies,
                )
            if response.status_code != 200:
                print(f"Failed to delete lobby {self.lobby_id}: {response.text}")
                return

    async def player_left(self):
        self.lobby_session.players.reset()
        self.lobby_session.players2.reset()
        self.lobby_session.enable_game3 = True
        self.lobby_session.enable_start = True

        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'send_player_left',
                'roles': self.lobby_session.player_names,
            }
        )

    async def send_update_roles(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'roles': event['roles'],
        }))
