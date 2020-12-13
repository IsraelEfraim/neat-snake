import neat
import pygame
from pygame.locals import *
from model import tron
import math
import random

generation_number = 0


class NeatTronPlayer(tron.TronPlayer):
    def __init__(self, direction, distance, nn):
        super().__init__(direction)
        self.distance = distance
        self.nn = nn
        self.boundaries = []
        self.moves = 0

    def update_boundaries(self, board):
        self.boundaries = tron.get_all_boundaries(
            self.head, self.direction, board)
        return self.boundaries

    def get_data(self, board):
        radar = self.update_boundaries(board)
        return [self.distance(self.head, limit) for limit in radar]

    def action(self):
        def feedback(head, board):
            self.moves += 1
            self.head = head

            output = self.nn.activate(self.get_data(board))
            direction = output.index(max(output))

            if direction == 0:
                pass
            if direction == 1:
                self.direction = tron.Direction.shift(self.direction, -2)
            if direction == 2:
                self.direction = tron.Direction.shift(self.direction, 2)

            return self.direction

        return feedback


def chunks(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def even_chunks(lst, n):
    return [chunk + [lst[random.randint(0, len(lst) - 1)]
                     for idx in range(0, n - len(chunk))] for chunk in chunks(lst, n)]


def run_generation(genomes, config):
    global generation_number
    generation_number += 1

    # create networks
    generation = [(neat.nn.FeedForwardNetwork.create(genome, config), genome)
                  for _, genome in genomes]

    for _, g in generation:
        g.fitness = (0, 0)

    random.shuffle(generation)

    for s1, s2 in even_chunks(generation, 2):
        nn1, g1 = s1
        nn2, g2 = s2

        d1 = tron.Direction.ALL[1 + random.randint(0, 3) * 2]
        d2 = tron.Direction.ALL[1 + random.randint(0, 3) * 2]

        p1 = NeatTronPlayer(d1, distance, nn1)
        p2 = NeatTronPlayer(d2, distance, nn2)

        tron_game = create_tron_game(80, 80, [p1, p2])
        winner = run_tron_game(tron_game, 10)

        def fit(fitness, moves, winner):
            qty, total = fitness
            curr_score = moves * 2 if winner else 1
            return (qty + 1, total + curr_score)

        g1.fitness = fit(g1.fitness, p1.moves, winner == 0)
        g2.fitness = fit(g2.fitness, p2.moves, winner == 1)

    for _, g in generation:
        qty, total = g.fitness
        g.fitness = total / qty


def to_block_unit(block_size):
    def multiply_pos(pos):
        x, y = pos
        return (x * block_size, y * block_size)
    return multiply_pos


def distance(pos0, pos1):
    x0, y0 = pos0
    x1, y1 = pos1

    return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


def create_tron_game(width, height, players):
    actions = [p.action() for p in players]
    seeds = [(20, 20), (60, 20)]

    return tron.TronGame(width, height, actions, seeds)


def run_tron_game(tron_game, block_size):
    width, height = tron_game.width, tron_game.height

    block = (block_size, block_size)
    to_block = to_block_unit(block_size)

    pygame.init()

    pygame.display.set_caption('TheTron')
    screen = pygame.display.set_mode(to_block((width, height)))
    generation_font = pygame.font.SysFont("Arial", 24)

    blue = pygame.Surface(block)
    blue.fill((0, 193, 247))

    yellow = pygame.Surface(block)
    yellow.fill((248, 194, 33))

    colors = [blue, yellow]

    clock = pygame.time.Clock()

    global generation_number

    while not tron_game.is_over():
        clock.tick(0)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

        tron_game.next_state()
        board = tron_game.get_board()

        screen.fill((46, 52, 64))

        # Render

        # Players
        for line in range(width):
            for column in range(height):
                if not board[line][column] is None:
                    screen.blit(
                        colors[board[line][column]], (line * block_size, column * block_size))

        text = generation_font.render(
            "Generation : " + str(generation_number), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen.get_width() / 2, 30)
        screen.blit(text, text_rect)

        pygame.display.update()

    return tron_game.get_winner()


if __name__ == '__main__':
    pygame.font.init()

    config_path = './model/config-feedforward.txt'
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(run_generation, 10000)
