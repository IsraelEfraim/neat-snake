import pygame
from pygame.locals import *
import tron
import neat
import math
import random


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

            [left, right] = self.nn.activate(self.get_data(board))

            if left:
                self.direction = tron.Direction.shift(self.direction, -2)
            elif right:
                self.direction = tron.Direction.shift(self.direction, 2)

            return self.direction

        return feedback


def chunks(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def run_generation(genomes, config):
    # create networks
    generation = [(neat.nn.FeedForwardNetwork.create(genome, config), genome)
                  for _, genome in genomes]

    random.shuffle(generation)

    for s1, s2 in chunks(generation, 2):
        nn1, g1 = s1
        nn2, g2 = s2

        p1 = NeatTronPlayer(tron.Direction.RIGHT, distance, nn1)
        p2 = NeatTronPlayer(tron.Direction.LEFT, distance, nn2)

        tron_game = create_tron_game(80, 80, [p1, p2])
        winner = run_tron_game(tron_game, 10)

        g1.fitness = 1 / p1.moves + 1 if winner == 0 else 0
        g2.fitness = 1 / p2.moves + 1 if winner == 1 else 0


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

    player_skin = pygame.Surface(block)
    player_skin.fill((255, 255, 255))

    clock = pygame.time.Clock()

    while not tron_game.is_over():
        clock.tick(0)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

        tron_game.next_state()
        board = tron_game.get_board()

        screen.fill((0, 0, 0))

        # Render

        # Players
        for line in range(width):
            for column in range(height):
                if not board[line][column] is None:
                    screen.blit(
                        player_skin, (line * block_size, column * block_size))

        pygame.display.update()

    return tron_game.get_winner()


if __name__ == '__main__':
    config_path = './model/config-feedforward.txt'
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(run_generation, 10000)
