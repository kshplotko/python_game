import pygame
import json
from pygame import *
from Camera import *

pygame.init()

with open("Data/sprite_map.json") as file:
	sprite_map = json.load(file)
with open("Data/levels.json") as file:
	levels = json.load(file)

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
	"height": int(screen_stat["tile"]*4/5),
	"color": "#00FF19"
}
active_level = 0


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

def collisions_interact(_interact):
	global level, active_level, level_begin, player

	for i in _interact:
		if sprite.collide_rect(player, i["sprite"]):
			m = i["x"]
			n = i["y"]
			key = level[n][m]

			if key == "k":
				level[n] = level[n][:m] + " " + level[n][m+1:]
				for l in range(len(level)):
					if level[l].find("d") > -1:
						z = level[l].index("d")
						level[l] = level[l][:z] + "D" + level[l][z+1:]

			if key == "D":
				if active_level+1 >= len(levels):
					print("end game!")
				else:
					active_level += 1
					level = levels[active_level]
					level_begin = True

			if key == "W":
				level_begin = True
			if key == "s":
				player.rect.height = int(player.rect.height / 4)
				player.rect.width  = int(player.rect.width  / 4)
				player.image = pygame.transform.scale(player.image, (player.rect.width, player.rect.height))
				level[n] = level[n][:m] + " " + level[n][m+1:]


def player_move(left, right, jump, _obstacles, _interact):
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

	collisions_interact(_interact)


player = sprite.Sprite()
player.image = Surface((player_stat["width"], player_stat["height"]))
player.image.fill(Color(player_stat["color"]))
player.image = image.load(sprite_map["player"])

# player.rect = Rect(player_stat["x"], player_stat["y"], player_stat["width"], player_stat["height"])
player.rect = Rect(0, 0, player_stat["width"], player_stat["height"])

DISPLAY = (screen_stat["width"]*screen_stat["tile"], screen_stat["height"]*screen_stat["tile"])

screen = pygame.display.set_mode(DISPLAY)
pygame.display.set_caption("Test game")

background = Surface(DISPLAY)
background.fill(Color("#ffffff"))

obstacles_sprites = sprite_map["obstacles"]
interact_sprites  = sprite_map["interact"]

level = levels[active_level].copy()
timer = pygame.time.Clock()
left = right = jump = False
level_begin = True
camera = Camera(camera_configure)


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
	interact = []

	if level_begin:
		level = levels[active_level].copy()
		camera.size(len(level[0])*screen_stat["tile"], len(level)*screen_stat["tile"])

	for y in range(len(level)):
		for x in range(len(level[y])):
			coordX = x*screen_stat["tile"]
			coordY = y*screen_stat["tile"]

			if level[y][x] in obstacles_sprites or level[y][x] in interact_sprites:
				tile_sprite = sprite.Sprite()

				if level[y][x] in obstacles_sprites:
					tile_sprite.image = image.load(obstacles_sprites[level[y][x]])
					tile_sprite.rect = Rect(
						coordX,
						coordY,
						screen_stat["tile"],
						screen_stat["tile"]
					)

					obstacles.append(tile_sprite)

				if level[y][x] in interact_sprites:
					io = interact_sprites[level[y][x]]
					tile_sprite.image = image.load(io["sprite"])
					tile_sprite.rect = Rect(
						coordX + int((screen_stat["tile"]-io["w"])/2),
						coordY + int((screen_stat["tile"]-io["h"])/2),
						io["w"],
						io["h"]
					)
					if "draw_at" in io:
						if io["draw_at"] == "bottom":
							tile_sprite.rect.y = coordY + screen_stat["tile"] - io["h"]

					interact.append({
						"sprite": tile_sprite,
						"x": x,
						"y": y
					})

				objects.add(tile_sprite)

			if level_begin and level[y][x] == "p":
				player.rect.left = coordX
				player.rect.top  = coordY
				player.rect.width  = player_stat["width"]
				player.rect.height = player_stat["height"]
				player.image = image.load(sprite_map["player"])

				level_begin = False

	objects.add(player)
	player_move(left, right, jump, obstacles, interact)

	camera.update(player, screen_stat["width"]*screen_stat["tile"], screen_stat["height"]*screen_stat["tile"])
	for obj in objects:
		screen.blit(obj.image, camera.apply(obj))

	pygame.display.update()
