from channels.generic.websocket import AsyncWebsocketConsumer
from .signals import game_update_signal

# from multiprocessing.shared_memory import SharedMemory
# from channels.db import database_sync_to_async
# from asgiref.sync import async_to_sync

import asyncio, time, threading, json

class GameSession():
	def __init__(self):
		self.streaming = False

		#usuable by more than one thread
		self.player_count = 0
		self.paddle_input = [[0,0],[0,0]]

		# locks
		self.player_count_lock = threading.Lock()
		self.input_lock = threading.Lock()

		self.screen_width = 1000
		self.screen_height = self.screen_width / 2
		self.thread = None
		self.player_count = 0
		self.paddle_input = [[0,0],[0,0]]

		# size
		self.screen_width = 1000
		self.screen_height = self.screen_width / 2
		self.paddle_width = self.screen_width/100*0.1
		self.paddle_heigth = self.screen_height/100*20
		self.ball_sizex = self.screen_width/100*1
		self.ball_sizey = self.screen_height/100*2

		# position
		self.ball = [0,0]
		self.paddleL = 0
		self.paddleR = 0

		self.ball_start_speedx = 2
		self.ball_start_speedy = 2
		self.ball_speedX = self.ball_start_speedx
		self.ball_speedY = self.ball_start_speedy
		self.ball_bounce_mult = 1.52
		self.passes = 0
		self.paddleL_speed = 0
		self.paddleR_speed = 0
		self.Lscore = 0
		self.Rscore = 0
		self.start = 0
		self.nonce = 0
		self.iterationStartT = 0

		#data in bits to send to frontend
		self.packed_data = (
		    (int(self.nonce) << (9 + 9 + 9 + 10 + 7 + 7)) |
			(int(self.paddleL) << (9 + 9 + 10 + 7 + 7)) |
			(int(self.paddleR) << (9 + 10 + 7 + 7)) |
			(int(self.ball[0]) << (10 + 7 + 7)) |
			(int(self.ball[1]) << (7 + 7)) |
			(int(self.Lscore) << 7) |
			int(self.Rscore)
			)

class PongGame(AsyncWebsocketConsumer):

	# sharedMemSize = 100
	GameSessions = {}

	################## CONNECT ##################

	async def connect(self):
		# This is called when the WebSocket connection is first made
		self.lobby_id = self.scope['url_route']['kwargs']['lobby_id']
		self.max_player_count = self.scope['url_route']['kwargs']['max_player']
		self.lobby_group_name = f"lobby_{self.lobby_id}"
		
		await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name
        )

		if self.lobby_group_name not in self.GameSessions:
			self.GameSessions[self.lobby_group_name] = GameSession()
			print(f"Created new GameSession for lobby: {self.lobby_group_name}")

		self.game_session = self.GameSessions[self.lobby_group_name]

		if self.game_session.streaming == True:
			print("Lobby is full. Rejecting connection.")
			await self.close()
			return

		self.game_session.player_count += 1

		if self.game_session.player_count == self.max_player_count:
			game_update_signal.connect(self.game_update_signal_handler, sender=self)
			self.game_session.streaming = True
			self.game_session.thread = threading.Thread(target= self.pong)
			self.gameThread.daemon = True
			self.gameThread.start()

		await self.accept()

	################## SIGNALHANDLER ##################

	async def game_update_signal_handler(self, **kwargs):

		game_state = {
			'type': 'game_update',
			'nonce': kwargs['nonce'],
			'paddleL': kwargs['paddleL'],
			'paddleR': kwargs['paddleR'],
			'ball_x': kwargs['ball_x'],
			'ball_y': kwargs['ball_y'],
			'Lscore': kwargs['Lscore'],
			'Rscore': kwargs['Rscore']
    	}

		await self.channel_layer.group_send(
        	self.lobby_group_name,
        	game_state
		)

	async def game_update(self, event):
		await self.send(text_data=json.dumps({
	        'nonce': event['nonce'],
	        'paddleL': event['paddleL'],
	        'paddleR': event['paddleR'],
	        'ball_x': event['ball_x'],
	        'ball_y': event['ball_y'],
	        'Lscore': event['Lscore'],
	        'Rscore': event['Rscore']
			}))
		
	################## RECEIVE ##################

	async def receive(self, text_data):
		encoded_data = int(text_data)
		player = (encoded_data >> 2) & 1
		direction = (encoded_data >> 1) & 1
		moving = encoded_data & 1
		await asyncio.to_thread(self.update_paddle_input, player, direction, moving)

	def update_paddle_input(self, player, direction, moving):
		with self.game_session.paddle_input_lock:
			self.game_session.paddle_input[player][direction] = moving

	################## DISCONNECT ##################

	async def disconnect(self, close_code):
		# This is called when the WebSocket connection is closed
		await asyncio.to_thread(self.decrease_player_count)
		self.game_session.streaming = False
		game_update_signal.disconnect(self.game_update_signal_handler, sender=self)

		await self.channel_layer.group_discard(
			self.lobby_group_name,
		    self.channel_name
		)

	def decrease_player_count(self):
		with self.game_session.player_count_lock:
			self.game_session.player_count -= 1
	
	################## THREAD ##################

	def pong(self):

		tickrate = 1/120
		self.game_session.start = int(time.time() * 1000)
		self.game_session.nonce = int(time.time() * 1000) - self.game_session.start
		self.game_session.iterationStartT = time.time()

		while True:
			with self.game_session.player_count_lock:
				if self.game_session.player_count != 2:
					break
			#gameclock logic
			duration = time.time() - self.game_session.iterationStartT
			sleeptime = tickrate - duration
			if sleeptime > 0:
				time.sleep(sleeptime)
			self.game_session.iterationStartT = time.time()

			#increase ball speed in x direction every two passes
			if self.game_session.passes > 0 and self.game_session.passes % 2 == 0:
				self.game_session.ball_speedX += 1
				self.game_session.passes = 0

			#check for events from fontend
			with self.game_session.paddle_input_lock:
				self.game_session.paddleL_speed = (self.game_session.paddle_input[0][1] - self.game_session.paddle_input[0][0]) * 6
				self.game_session.paddleR_speed = (self.game_session.paddle_input[1][1] - self.game_session.paddle_input[1][0]) * 6

			#move ball
			self.game_session.ball[0] += self.game_session.ball_speedX
			self.game_session.ball[1] += self.game_session.ball_speedY

			#make sure data stays inside playing field
			if self.game_session.ball[1] < 0:
				self.game_session.ball[1] = 0

			if self.game_session.ball[1] > self.game_session.screen_height:
				self.game_session.ball[1] = self.game_session.screen_height

			#move left paddle
			self.game_session.paddleL += self.game_session.paddleL_speed

			#safety against moving and being out of bounds
			if self.game_session.paddleL >= self.game_session.screen_height - self.game_session.paddle_heigth or self.game_session.paddleL <= 0:
				self.game_session.paddleL_speed = 0
			if self.game_session.paddleL > self.game_session.screen_height - self.game_session.paddle_heigth:
				self.game_session.paddleL = self.game_session.screen_height - self.game_session.paddle_heigth
			if self.game_session.paddleL < 0:
				self.game_session.paddleL = 0

			#move right paddle
			self.game_session.paddleR += self.game_session.paddleR_speed

			#safety against moving and being out of bounds
			if self.game_session.paddleR >= self.game_session.screen_height - self.game_session.paddle_heigth or self.game_session.paddleR <= 0:
				self.game_session.paddleR_speed = 0
			if self.game_session.paddleR > self.game_session.screen_height - self.game_session.paddle_heigth:
				self.game_session.paddleR = self.game_session.screen_height - self.game_session.paddle_heigth
			if self.game_session.paddleR < 0:
				self.game_session.paddleR = 0

			#make ball bounce on paddles
			#Left Paddle
			if(self.game_session.ball[0] < 0 + self.game_session.paddle_width and (self.game_session.ball[1] >= self.game_session.paddleL - self.game_session.ball_sizey and self.game_session.ball[1] <= self.game_session.paddleL + self.game_session.paddle_heigth)):
				self.game_session.ball[0] = 0 + self.game_session.paddle_width
				self.game_session.passes += 1
				if self.game_session.paddleL_speed > 0:
					self.game_session.ball_speedY += self.game_session.ball_bounce_mult
				if self.game_session.paddleL_speed < 0:
					self.game_session.ball_speedY -= self.game_session.ball_bounce_mult
				self.game_session.ball_speedX *= -1
			#Right Paddle 
			if(self.game_session.ball[0] > self.game_session.screen_width - self.game_session.paddle_width - self.game_session.ball_sizex and (self.game_session.ball[1] + self.game_session.ball_sizex >= self.game_session.paddleR and self.game_session.ball[1] <= self.game_session.paddleR + self.game_session.paddle_heigth)):
				self.game_session.ball[0] = self.game_session.screen_width - self.game_session.paddle_width - self.game_session.ball_sizex
				self.game_session.passes += 1
				if self.game_session.paddleR_speed > 0:
					self.game_session.ball_speedY += self.game_session.ball_bounce_mult
				if self.game_session.paddleR_speed < 0:
					self.game_session.ball_speedY -= self.game_session.ball_bounce_mult
				self.game_session.ball_speedX *= -1

			#make ball bounce on top and bottom
			if self.game_session.ball[1] <= 0 or self.game_session.ball[1] >= self.game_session.screen_height - self.game_session.ball_sizey:
				self.game_session.ball_speedY *= -1

			#make ball reset if i leaves screen on x axis
			if self.game_session.ball[0] > self.game_session.screen_width - self.game_session.ball_sizex:
				self.game_session.Lscore += 1
				self.game_session.ball_speedX = self.game_session.ball_start_speedx
				self.game_session.ball[0] = self.game_session.screen_width/2
				self.game_session.ball[1] = self.game_session.screen_height/2
				self.game_session.ball_speedY = self.game_session.ball_start_speedy
			if (self.game_session.ball[0] < 0):
				self.game_session.Rscore += 1
				self.game_session.ball_speedX = - self.game_session.ball_start_speedx
				self.game_session.ball[0] = self.game_session.screen_width/2
				self.game_session.ball[1] = self.game_session.screen_height/2
				self.game_session.ball_speedY = self.game_session.ball_start_speedy

			#update nonce
			self.game_session.nonce = int(time.time() * 1000) - self.game_session.start

			# Pack the data into a single integer
			# self.game_session.packed_data = (
			# 	(int(self.game_session.nonce) << (9 + 9 + 9 + 10 + 7 + 7)) |
			# 	(int(self.game_session.paddleL) << (9 + 9 + 10 + 7 + 7)) |
			# 	(int(self.game_session.paddleR) << (9 + 10 + 7 + 7)) |
			# 	(int(self.game_session.ball[0]) << (10 + 7 + 7)) |
			# 	(int(self.game_session.ball[1]) << (7 + 7)) |
			# 	(int(self.game_session.Lscore) << 7) |
			# 	int(self.game_session.Rscore)
			# )
			# game_update_signal.send(sender=self, packed_data=self.game_session.packed_data)

			game_update_signal.send(sender=self, 
						   nonce=self.game_session.nonce, 
						   paddleL=self.game_session.paddleL, 
						   paddleR=self.game_session.paddleR, 
						   ball_x=self.game_session.ball[0], 
						   ball_y=self.game_session.ball[1], 
						   Lscore=self.game_session.Lscore, 
						   Rscore=self.game_session.Rscore)