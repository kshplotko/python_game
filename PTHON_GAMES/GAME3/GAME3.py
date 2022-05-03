import pygame
import json
from pygame import *
from Camera import *

pygame.init()

screen_stat = {
	"width": 10,
	"height": 10,
	"tile": 48
}

player_stat = {
	"x": 100,
	"y": 100,
	"speed": 5,
	"jump_power": 10,
	"onGround": False,
	"dx": 0,
	"dy": 0,
	"ddy": 0.35,
	"width":  int(screen_stat["tile"]/2),
	"height": int(screen_stat["tile"]*4/5)
}

def collisions_obstacles(_dx, _dy, _obstacles):
	global player_stat, player

	for p in _obstacles:
		if sprite.collide_rect(player, p):
			if _dx > 0:
				player.rect.right = p.rect.left
			if _dx < 0:
				player.rect.left = p.rect.right
			if _dy > 0:
				player.rect.bottom = p.rect.top
				player_stat["onGround"] = True
				player_stat["dy"] = 0
			if _dy < 0:
				player.rect.top = p.rect.bottom
				player_stat["dy"] = 0

def player_move(left, right, jump, _obstacles):
	global player_stat, player

	if left:
		player_stat["dx"] = -player_stat["speed"]
	if right:
		player_stat["dx"] = player_stat["speed"]
	if not(left or right):
		player_stat["dx"] = 0

	if player_stat["onGround"] and jump:
		player_stat["dy"] = -player_stat["jump_power"]
	if not player_stat["onGround"]:
		player_stat["dy"] += player_stat["ddy"]

	player_stat["onGround"] = False

	player.rect.x += player_stat["dx"]
	collisions_obstacles(player_stat["dx"], 0, _obstacles)

	player.rect.y += player_stat["dy"]
	collisions_obstacles(0, player_stat["dy"], _obstacles)

player = sprite.Sprite()
player.image = Surface((player_stat["width"], player_stat["height"]))
player.image.load("player.png")
player.rect = Rect(player_stat["x"], player_stat["y"], player_stat["width"], player_stat["height"])

level = [
	"##########",
	"#        #",
	"#        #",
	"#      ###",
	"###      #",
	"#        #",
	"#     #  #",
	"#       ##",
	"#  #     #",
	"##########"
]

DISPLAY = (screen_stat["width"]*screen_stat["tile"], screen_stat["height"]*screen_stat["tile"])
screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("Toonel Droid")

background = Surface(DISPLAY)
background.fill(Color("#ffffff"))

left = right = jump = False
timer = pygame.time.Clock()

while 1:
	timer.tick(60)
	for e in pygame.event.get():
		if e.type == QUIT:
			exit()
		if e.type == KEYDOWN and e.key in [K_LEFT, K_a]:
			left = True
		if e.type == KEYDOWN and e.key in [K_RIGHT, K_d]:
			right = True
		if e.type == KEYDOWN and e.key in [K_UP, K_SPACE, K_w]:
			jump = True

		if e.type == KEYUP and e.key in [K_LEFT, K_a]:
			left = False
		if e.type == KEYUP and e.key in [K_RIGHT, K_d]:
			right = False
		if e.type == KEYUP and e.key in [K_UP, K_SPACE, K_w]:
			jump = False

	screen.blit(background, (0,0))

	objects = pygame.sprite.Group()
	obstacles = []

	for y in range(len(level)):
		for x in range(len(level[y])):
			coordX = x*screen_stat["tile"]
			coordY = y*screen_stat["tile"]

			if level[y][x] == "#":
				tile_sprite = sprite.Sprite()
				tile_sprite.image = Surface((screen_stat["tile"], screen_stat["tile"]))
				tile_sprite.image.fill = image.load("")
				tile_sprite.rect = Rect(coordX, coordY, screen_stat["tile"], screen_stat["tile"])

				obstacles.append(tile_sprite)
				objects.add(tile_sprite)

	player_move(left, right, jump, obstacles)
	objects.add(player)

	objects.draw(screen)

	pygame.display.update()
