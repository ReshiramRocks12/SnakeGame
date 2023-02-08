import pygame
import random
import math
import copy
from enum import Enum

class Direction(Enum):
	NORTH = 0
	SOUTH = 1
	EAST = 2
	WEST = 3

class SnakeBlock():
	def __init__(self, pos_x: float, pos_y: float, facing: Direction, is_head: bool = False, colour: tuple = (0, 0, 255)) -> None:
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.facing = facing
		self.is_head = is_head
		self.turns = {}
		self.colour = colour
	
pygame.init()

GRID_SQUARES = 15
GRID_SIZE = 30
FPS_LIMIT = 120
APPLE_LIMIT = 1
MOVE_STEP = 1.5

screen_size = GRID_SQUARES * GRID_SIZE
screen = pygame.display.set_mode((screen_size, screen_size))
clock = pygame.time.Clock()
font_text = pygame.font.Font('freesansbold.ttf', 14)
font_subtitle = pygame.font.Font('freesansbold.ttf', 20)
font_title = pygame.font.Font('freesansbold.ttf', 48)
running = True
paused = False
game_over = False
invul = 0.5 * FPS_LIMIT

snake = [
	SnakeBlock(screen_size / 2.0, screen_size / 2.0, None),
	SnakeBlock(screen_size / 2.0, screen_size / 2.0, None, colour=(0, 191, 255)),
	SnakeBlock(screen_size / 2.0, screen_size / 2.0, None, True, colour=(0, 0, 0))
]
direction_to_face = None

apples = []
score = 0
high_score = -1

def displayBackground() -> None:
	for x in range(GRID_SQUARES):
		i = x % 2
		for y in range(GRID_SQUARES):
			grid = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
			if x == 0 or y == 0 or x == GRID_SQUARES - 1 or y == GRID_SQUARES - 1:
				pygame.draw.rect(screen, (153, 76, 21), grid)
			elif i % 2 == 0:
				pygame.draw.rect(screen, (0x84, 0xC0, 0x11), grid)
			else:
				pygame.draw.rect(screen, (0x56, 0x7D, 0x46), grid)

			i += 1

def displaySnake() -> None:
	for s in snake:
		snake_rect = pygame.Rect(s.pos_x - (GRID_SIZE / 2), s.pos_y - (GRID_SIZE / 2), GRID_SIZE, GRID_SIZE)
		pygame.draw.rect(screen, s.colour, snake_rect)

	if game_over:
		gameOver()
	
def spawnApple() -> None:
	snake_pos = []

	for s in snake:
		snake_pos.append((math.floor(s.pos_x / GRID_SIZE), math.floor(s.pos_y / GRID_SIZE)))

	apple_x = snake_pos[0][0]
	apple_y = snake_pos[0][1]
	
	while (apple_x, apple_y) in snake_pos or (float(apple_x * GRID_SIZE), float(apple_y * GRID_SIZE)) in apples:
		apple_x = random.randint(1, GRID_SQUARES - 2)
		apple_y = random.randint(1, GRID_SQUARES - 2)

	apples.append((float(apple_x * GRID_SIZE), float(apple_y * GRID_SIZE)))


def displayApple() -> None:
	for a in apples:
		apple = pygame.Rect(a[0], a[1], GRID_SIZE, GRID_SIZE)
		pygame.draw.rect(screen, (226, 6, 44), apple)

def gameOver() -> None:
	global game_over, high_score
	high_score = score if score > high_score else high_score
	
	screen.blit(end_title, end_title_rect)
	screen.blit(end_text1, end_text_rect1)
	screen.blit(end_text2, end_text_rect2)

def updateSnake() -> None:
	global direction_to_face, score, game_over

	head = snake[-1]
	snake_pos = []

	for s in snake:
		if not s.is_head:
			snake_pos.append((math.floor(s.pos_x / GRID_SIZE), math.floor(s.pos_y / GRID_SIZE)))

	for a in apples:
		if a[0] == head.pos_x - (GRID_SIZE / 2) and a[1] == head.pos_y - (GRID_SIZE / 2):
			apples.remove(a)
			score += 1
			lb = snake[0]
			snake.insert(0, SnakeBlock(lb.pos_x, lb.pos_y, lb.facing, colour=(0, 0, 255) if len(snake) % 2 == 0 else (0, 191, 255)))
			snake[1].turns.clear()

	for i in range(len(snake)):
		sb = snake[i]

		if sb.is_head:
			if not direction_to_face == None:
				if (sb.pos_x - (GRID_SIZE / 2)) % GRID_SIZE == 0 and (sb.pos_y - (GRID_SIZE / 2)) % GRID_SIZE == 0:
					sb.facing = direction_to_face
					direction_to_face = None
					sb.turns[(sb.pos_x, sb.pos_y)] = sb.facing

			if sb.pos_x < GRID_SIZE + (GRID_SIZE / 2) or sb.pos_x > screen_size - GRID_SIZE - (GRID_SIZE / 2) or sb.pos_y < GRID_SIZE + (GRID_SIZE / 2) or sb.pos_y > screen_size - GRID_SIZE - (GRID_SIZE / 2):
				game_over = True
				return

		if not paused and not game_over:
			if not sb.is_head:
				if (sb.pos_x, sb.pos_y) in snake[i + 1].turns or sb.facing == None:
					if not sb.facing == None:
						sb.facing = snake[i + 1].turns[(sb.pos_x, sb.pos_y)]
						snake[i + 1].turns.pop((sb.pos_x, sb.pos_y))
						sb.turns[(sb.pos_x, sb.pos_y)] = sb.facing
					else:
						sb.facing = snake[i + 1].facing
			if not sb.is_head and (math.floor(sb.pos_x / GRID_SIZE), math.floor(sb.pos_y / GRID_SIZE)) == (math.floor(snake[i + 1].pos_x / GRID_SIZE), math.floor(snake[i + 1].pos_y / GRID_SIZE)):
				continue
			else:
				new_x = sb.pos_x
				new_y = sb.pos_y
				offset_x = 0
				offset_y = 0

				if sb.facing == Direction.NORTH:
					new_y -= MOVE_STEP
					offset_y = -15
				elif sb.facing == Direction.SOUTH:
					new_y += MOVE_STEP
					offset_y = 15
				elif sb.facing == Direction.WEST:
					new_x -= MOVE_STEP
					offset_x = -15
				elif sb.facing == Direction.EAST:
					new_x += MOVE_STEP
					offset_x = 15

				if sb.is_head and (math.floor((new_x + offset_x) / GRID_SIZE), math.floor((new_y + offset_y) / GRID_SIZE)) in snake_pos and invul == 0:
					game_over = True
					return
				else:
					sb.pos_x = new_x
					sb.pos_y = new_y
					
pygame.display.set_caption("Snake | Recreated by ReshiramRocks12")

snake_copy = copy.deepcopy(snake)

credits_text = font_text.render('https://github.com/ReshiramRocks12', True, (255, 255, 255))
credits_text_rect = credits_text.get_rect(center=(screen_size / 2, screen_size - (GRID_SIZE / 2)))

pause_title = font_title.render('PAUSED', True, (0, 0, 0))
pause_title_rect = pause_title.get_rect(center=(screen_size / 2, screen_size / 2))
pause_text1 = font_subtitle.render('Press [Esc] to Resume', True, (255, 250, 250))
pause_text_rect1 = pause_text1.get_rect(center=(screen_size / 2, (screen_size / 2) + pause_title_rect.height))
pause_text2 = font_subtitle.render('Press [Enter] to Quit', True, (255, 250, 250))
pause_text_rect2 = pause_text2.get_rect(center=(screen_size / 2, (screen_size / 2) + pause_title_rect.height + pause_text_rect1.height + (GRID_SIZE / 2)))

end_title = font_title.render('GAME OVER', True, (0, 0, 0))
end_title_rect = end_title.get_rect(center=(screen_size / 2, screen_size / 2))
end_text1 = font_subtitle.render('Press [Esc] to Restart', True, (255, 250, 250))
end_text_rect1 = end_text1.get_rect(center=(screen_size / 2, (screen_size / 2) + end_title_rect.height))
end_text2 = font_subtitle.render('Press [Enter] to Quit', True, (255, 250, 250))
end_text_rect2 = end_text2.get_rect(center=(screen_size / 2, (screen_size / 2) + end_title_rect.height + end_text_rect1.height + (GRID_SIZE / 2)))


while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.key.key_code('ESCAPE'):
				if not game_over:
					paused = not paused
				else:
					game_over = False
					apples.clear()
					snake = copy.deepcopy(snake_copy)
					score = 0
					invul = 0.5 * FPS_LIMIT
			elif (paused or game_over) and event.key == pygame.key.key_code('RETURN'):
				running = False
				break

		keys = pygame.key.get_pressed()
		
		if not paused and not game_over and direction_to_face == None:
			head = snake[-1]
			if keys[pygame.K_RIGHT] and not head.facing == Direction.WEST:
				direction_to_face = Direction.EAST
			elif keys[pygame.K_LEFT] and not head.facing == Direction.EAST:
				direction_to_face = Direction.WEST
			elif keys[pygame.K_UP] and not head.facing == Direction.SOUTH:
				direction_to_face = Direction.NORTH
			elif keys[pygame.K_DOWN] and not head.facing == Direction.NORTH:
				direction_to_face = Direction.SOUTH
	
	if not snake[-1].facing == None:
		if invul > 0:
			invul -= 1
		if len(apples) < APPLE_LIMIT and not game_over:
			spawnApple()

	displayBackground()
	updateSnake()
	displayApple()
	displaySnake()

	score_text = font_subtitle.render('Score: %d%s' % (score, '' if high_score == -1 else (' | High Score: %d' % high_score)), True, (255, 255, 255))
	score_text_rect = score_text.get_rect(center=(screen_size / 2, GRID_SIZE / 2))
	
	screen.blit(score_text, score_text_rect)
	screen.blit(credits_text, credits_text_rect)

	if paused:
		screen.blit(pause_title, pause_title_rect)
		screen.blit(pause_text1, pause_text_rect1)
		screen.blit(pause_text2, pause_text_rect2)

	pygame.display.update()
	clock.tick(FPS_LIMIT)
