import pygame
import os
import sys
import random
import neat

W_WIDTH = 1500
W_HEIGHT = 900
F_HEIGHT = 50
BIRD_X = 300

pygame.init()
screen = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Comic Sans MS', 30)
ff_font = pygame.font.SysFont('Comic Sans MS', 100)
pygame.display.set_caption("Flappy Bird")
curr_gen = 0
high_score = 0
curr_score = 0
fast_forward = False

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
	def __init__(self, genome, config):
		self.width = 90
		self.height = 90
		self.x = BIRD_X
		self.term = 8
		self.grav = 0.1
		self.up = -6
		self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

		self.y = 400
		self.vel = 0

		# NN Inputs: bird: velocity, height,  pipe:  gap offset, distance to next 
		self.brain = neat.nn.FeedForwardNetwork.create(genome, config)
		self.genome = genome
		self.genome.fitness = 0

	def move(self):
		self.genome.fitness += 0.1
		self.y += self.vel
		if (self.vel < self.term):
			self.vel += self.grav

	def jump(self):
		self.vel = self.up

	def decide(self, pipe):
		output = self.brain.activate((self.vel, pipe.gap_offset + pipe.gap_height - self.y, pipe.x - self.x + self.width))
		if (output[0] > 0.5):
		 	self.jump()

	def draw(self):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))

class FlappyBird:
	def __init__(self, generation):
		self.next_pipes = [Pipe(), Pipe(2400)]
		self.past_pipes = []
		self.pipespeed = 3

		self.birds = generation
		self.floor = Floor()

	def handle_events(self):
		global fast_forward
		for event in pygame.event.get():
			if (event.type == pygame.QUIT):
				sys.exit()
			elif (event.type == pygame.KEYDOWN):
				if (event.key == pygame.K_SPACE):
					fast_forward = not fast_forward
					if (fast_forward == True):
						screen.fill((255, 255, 255))
						ff_text = ff_font.render(">>> Fast Forwarding >>>", False, (0, 0, 0))
						screen.blit(ff_text, (200, 350))
						pygame.display.update()
					

	def birds_decide(self):
		for bird in self.birds:
			bird.decide(self.next_pipes[0])

	def move_entities(self):
		global high_score, curr_score
		for pipe in self.past_pipes:
			if (pipe.move(self.pipespeed) == 2):
				self.past_pipes.pop(0)
				self.next_pipes.append(Pipe())

		for pipe in self.next_pipes:
			if (pipe.move(self.pipespeed) == 1):
				curr_score += 1
				if (curr_score > high_score):
					high_score = curr_score
				self.past_pipes.append(self.next_pipes.pop(0))
				for bird in self.birds:
					bird.genome.fitness += 10

		for bird in self.birds:
			bird.move()

	def check_collision(self, bird):
		for pipe in self.next_pipes:
			if (bird.x + bird.width > pipe.x and pipe.x + pipe.width > bird.x):
				if (bird.y < pipe.gap_offset or bird.y + bird.height > pipe.gap_offset + pipe.gap_height):
					return True
		if (bird.y + bird.height > self.floor.y):
			return True
		return False

	def draw_entities(self):
		global high_score
		screen.fill((255, 255, 255))
		for pipe in self.next_pipes:
			pipe.draw()
		for pipe in self.past_pipes:
			pipe.draw()
		for bird in self.birds:
			bird.draw()
		
		self.floor.draw()
		text = font.render("High Score: " + str(high_score), False, (0, 0, 0))
		screen.blit(text, (100, 100))
		text = font.render("Score: " + str(curr_score), False, (0, 0, 0))
		screen.blit(text, (100, 150))
		text = font.render("Generation: " + str(curr_gen), False, (0, 0, 0))
		screen.blit(text, (100, 200))

		pygame.display.update()

	def tick(self):
		clock.tick(120)

	def step(self):
		self.handle_events()
		self.birds_decide()
		self.move_entities()

		for bird in self.birds:
			if (self.check_collision(bird)):
				self.birds.remove(bird)
		
		return len(self.birds) == 0


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def train(genomes, config):
	global curr_gen, fast_forward, curr_score
	curr_score = 0
	birds = []
	for genome_id, genome in genomes:
		birds.append(Bird(genome, config))

	flappy = FlappyBird(generation = birds)
	while True:
		if (flappy.step()):
			break
		if (not fast_forward or curr_score > 15):
			flappy.draw_entities()
			flappy.tick()
			

	curr_gen += 1

	

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config.txt')
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
p.add_reporter(neat.StatisticsReporter())

winner = p.run(train, 500)

# show final stats
print('\nBest genome:\n{!s}'.format(winner))
