from django.db import models

import pygame, sys

# Create your models here.
def handlePaddleRMovement(event):

	return 0,0


class pong(models.Model):
	pygame.init()

	#arbirary base values
	screen_width = 1000
	screen_height = 500

	#create screen (needs to be handeled by fontend eventually)
	screen = pygame.display.set_mode((screen_width, screen_height))
	pygame.display.set_caption("game")

	#set timing clock for game logic
	clock = pygame.time.Clock()
	
	paddle_width = screen_width/100*0.1
	paddle_heigth = screen_height/100*20
	ball_sizex = screen_width/100*1
	ball_sizey = screen_height/100*2

	ball = pygame.Rect(0,0,ball_sizex,ball_sizey)
	paddleL = pygame.Rect(0,0,paddle_width,paddle_heigth)
	paddleR = pygame.Rect(0,0,paddle_width,paddle_heigth)

	paddleR.centery = screen_height/2
	paddleR.centerx = screen_width - paddle_width

	paddleL.centery = screen_height/2
	paddleL.centerx = 0 + paddle_width

	ball.center = (screen_width/2,screen_height/2)

	ball_start_speedx = 2
	ball_start_speedy = 2

	ball_speedX = 0
	ball_speedY = 0
	ball_bounce_mult = 1.52
	paddleL_speed = 0
	paddleR_speed = 0

	Lscore = 0
	Rscore = 0

	gamestate = [None] * 6
	gamestate[4] = Lscore
	gamestate[5] = Rscore
	#gamestate: paddleL.y, paddleR.y, ball.x, ball.y, Lscore, Rscore

	log = open("gamedata.txt", "w")

	last_ball_speed = 0
	last_paddleR_speed = 0

	ball_speedX = ball_start_speedx
	ball_speedY = ball_start_speedy

	while True:
		#check for events (not sure how to get that from the frontend in the end)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					paddleR_speed = -6
				if event.key == pygame.K_DOWN:
					paddleR_speed = 6
				if event.key == pygame.K_w:
					paddleL_speed = -6
				if event.key == pygame.K_s:
					paddleL_speed = 6
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					paddleR_speed = 0
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_w or event.key == pygame.K_s:
					paddleL_speed = 0

	#update screen (frontend will have to handle that eventually)
		pygame.display.update()
		clock.tick(60)
		screen.fill("black")
		pygame.draw.rect(screen,'white',ball)
		pygame.draw.rect(screen,'white',paddleL)
		pygame.draw.rect(screen,'white',paddleR)

		#move ball
		ball.x += ball_speedX
		ball.y += ball_speedY
		
		#make sure data stays inside playing field
		if ball.y < 0:
			ball.y = 0

		if ball.y > screen_height:
			ball.y = screen_height

		#write ball location to gamedata

		#move left paddle
		paddleL.y += paddleL_speed
		#safety against moving and being out of bounds

		if paddleL.y >= screen_height - paddle_heigth or paddleL.y <= 0:
			paddleL_speed = 0
		if paddleL.y > screen_height-paddle_heigth:
			paddleL.y = screen_height-paddle_heigth
		if paddleL.y < 0:
			paddleL.y = 0

		#move right paddle
		paddleR.y += paddleR_speed

		#safety against moving and being out of bounds
		if paddleR.y >= screen_height - paddle_heigth or paddleR.y <= 0:
			paddleR_speed = 0
		if paddleR.y > screen_height-paddle_heigth:
			paddleR.y = screen_height-paddle_heigth
		if paddleR.y < 0:
			paddleR.y = 0


		gamestate[0] = paddleL.y
		gamestate[1] = paddleR.y
		gamestate[2] = ball.x
		if gamestate[2] < 0:
			gamestate[2] = 0
		if gamestate[2] > screen_width:
			gamestate[2] = screen_width
		gamestate[3] = ball.y


		#make ball bounce on top and bottom
		if ball.y <= 0 or ball.y >= screen_height:
			ball_speedY *= -1
		#make ball reset if i leaves screen on x axis
		if ball.x > screen_width or ball.x < 0:
			ball.x = screen_width/2
			ball.y = screen_height/2
			ball_speedY = ball_start_speedy
			ball_speedX = ball_start_speedx
			if ball.x > screen_width:
				Lscore += 1
				gamestate[4] = Lscore
			if (ball.x < 0):
				Rscore += 1
				gamestate[5] = Rscore

		if ball.colliderect(paddleL):
			if paddleL_speed > 0:
				ball_speedY += ball_bounce_mult
			if paddleL_speed < 0:
				ball_speedY -= ball_bounce_mult
			ball_speedX *= -1
		if ball.colliderect(paddleR):
			if paddleR_speed > 0:
				ball_speedY += ball_bounce_mult
			if paddleR_speed < 0:
				ball_speedY -= ball_bounce_mult
			ball_speedX *= -1

		log.write(' '.join(str(x) for x in gamestate) + "\n")
