import pygame
import sys
import random

W_WIDTH = 1500
W_HEIGHT = 900
F_HEIGHT = 50
BIRD_X = 300

pygame.init()
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Comic Sans MS', 30)
pygame.display.set_caption("Flappy Bird")

class Floor:
	def __init__(self):
		self.width = W_WIDTH
		self.height = F_HEIGHT
		self.x = 0
		self.y = W_HEIGHT - F_HEIGHT

	def draw(self):
		pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(self.x, self.y, self.width, self.height))


class Pipe:
	def __init__(self, x = 1600):
		self.width = 100
		self.gap_height = 300
		self.gap_buffer = 50
		self.x = x

		self.gap_offset = random.randint(self.gap_buffer, W_HEIGHT - self.gap_height - self.gap_buffer - F_HEIGHT)

	def size_width(self):
		if (self.x < 0):
			return self.width + self.x
		elif (self.x > W_WIDTH - self.width):
			return W_WIDTH - self.x
		else:
			return self.width

	def position_upper(self):
		left = self.x if self.x > 0 else 0
		top = 0
		return (left, top)

	def position_lower(self):
		left = self.x if self.x > 0 else 0
		top = self.gap_offset + self.gap_height
		return (left, top)

	def size_upper(self):
		height = self.gap_offset
		return (self.size_width(), height)

	def size_lower(self):
		height = W_HEIGHT - self.gap_height - self.gap_offset - F_HEIGHT
		return (self.size_width(), height)

	def draw(self):
		if (self.x > W_WIDTH):
			return
		pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(self.position_upper(), self.size_upper()))
		pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(self.position_lower(), self.size_lower()))

	def move(self, speed):
		self.x -= speed
		if (self.x + self.width < 0):
			return 2
		if (self.x + self.width < BIRD_X):
			return 1
		return 0

class Bird:
	def __init__(self):
		self.width = 90
		self.height = 90
		self.x = BIRD_X
		self.term = 8
		self.grav = 0.1
		self.up = -6

		self.y = 400
		self.vel = 0

	def move(self):
		self.y += self.vel
		if (self.vel < self.term):
			self.vel += self.grav

	def jump(self):
		self.vel = self.up

	def draw(self):
		pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(self.x, self.y, self.width, self.height))

class FlappyBird:
	def __init__(self):
		self.next_pipes = [Pipe(), Pipe(2400)]
		self.past_pipes = []
		self.pipespeed = 3
		self.score = 0

		self.bird = Bird()
		self.floor = Floor()

	def handle_events(self):
		for event in pygame.event.get():
			if (event.type == pygame.QUIT):
				sys.exit()
			elif (event.type == pygame.KEYDOWN):
				if (event.key == pygame.K_SPACE):
					self.bird.jump()

	def move_entities(self):
		for pipe in self.past_pipes:
			if (pipe.move(self.pipespeed) == 2):
				self.past_pipes.pop(0)
				self.next_pipes.append(Pipe())

		for pipe in self.next_pipes:
			if (pipe.move(self.pipespeed) == 1):
				self.score += 1
				self.past_pipes.append(self.next_pipes.pop(0))

		self.bird.move()

	def check_collision(self):
		for pipe in self.next_pipes:
			if (self.bird.x + self.bird.width > pipe.x and pipe.x + pipe.width > self.bird.x):
				if (self.bird.y < pipe.gap_offset or self.bird.y + self.bird.height > pipe.gap_offset + pipe.gap_height):
					return True
		if (self.bird.y + self.bird.height > self.floor.y):
			return True
		return False

	def draw_entities(self):
		screen.fill((255, 255, 255))
		for pipe in self.next_pipes:
			pipe.draw()
		for pipe in self.past_pipes:
			pipe.draw()
		self.floor.draw()
		self.bird.draw()

		text = font.render("Score: " + str(self.score), False, (0, 0, 0))
		screen.blit(text, (100, 100))

		pygame.display.update()

while True:
	flappy = FlappyBird()
	while True:
		flappy.handle_events()
		flappy.move_entities()
		if (flappy.check_collision()):
			break
		flappy.draw_entities()
		clock.tick(120)
