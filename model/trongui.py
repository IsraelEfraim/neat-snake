import pygame
from pygame.locals import *
import tron


class TronPlayer:
    def __init__(self, direction):
        self.direction = direction
        self.head = None

    def action(self):
        def feedback(head, board):
            self.head = tron.head_to(head, self.direction)
            return self.direction

        return feedback

    def set_direction(self, direction, override=False):
        if override or not direction == tron.Direction.opposite_of(self.direction):
            self.direction = direction


def to_block_unit(block_size):
    def multiply_pos(pos):
        x, y = pos
        return (x * block_size, y * block_size)
    return multiply_pos


if __name__ == '__main__':
    width, height = 80, 80

    block_size = 10
    block = (block_size, block_size)
    to_block = to_block_unit(block_size)

    tron_player_1 = TronPlayer(tron.Direction.RIGHT)
    tron_player_2 = TronPlayer(tron.Direction.LEFT)

    players = [tron_player_1.action(), tron_player_2.action()]

    seeds = [(20, 20), (60, 20)]

    tron_game = tron.TronGame(width, height, players, seeds)

    pygame.init()

    pygame.display.set_caption('TheTron')
    screen = pygame.display.set_mode(to_block((width, height)))

    player_skin = pygame.Surface(block)
    player_skin.fill((255, 255, 255))

    radar_colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0),
                    (255, 0, 0), (128, 0, 128), (140, 111, 214), (255, 192, 203)]

    clock = pygame.time.Clock()

    while True:
        clock.tick(15)

        if tron_game.is_over():
            tron_player_1.set_direction(tron.Direction.RIGHT, True)
            tron_player_2.set_direction(tron.Direction.LEFT, True)
            tron_game.reset()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()

            if event.type == KEYDOWN:
                if event.key == K_w:
                    tron_player_1.set_direction(tron.Direction.UP)
                elif event.key == K_s:
                    tron_player_1.set_direction(tron.Direction.DOWN)
                elif event.key == K_a:
                    tron_player_1.set_direction(tron.Direction.LEFT)
                elif event.key == K_d:
                    tron_player_1.set_direction(tron.Direction.RIGHT)
                elif event.key == K_UP:
                    tron_player_2.set_direction(tron.Direction.UP)
                elif event.key == K_DOWN:
                    tron_player_2.set_direction(tron.Direction.DOWN)
                elif event.key == K_LEFT:
                    tron_player_2.set_direction(tron.Direction.LEFT)
                elif event.key == K_RIGHT:
                    tron_player_2.set_direction(tron.Direction.RIGHT)

        tron_game.next_state()
        board = tron_game.get_board()

        screen.fill((0, 0, 0))

        radar = tron.get_all_boundaries(
            tron_player_1.head, tron_player_1.direction, tron_game)

        # Render

        # Distances
        for color, pos in zip(radar_colors, radar):
            x, y = to_block(pos)
            x, y = x + block_size / 2, y + block_size / 2

            hx, hy = to_block(tron_player_1.head)
            hx, hy = hx + block_size / 2, hy + block_size / 2

            pygame.draw.line(screen, color, (hx, hy), (x, y), 1)
            pygame.draw.circle(screen, color, (x, y), 3)

        # Players
        for line in range(width):
            for column in range(height):
                if not board[line][column] is None:
                    screen.blit(
                        player_skin, (line * block_size, column * block_size))

        pygame.display.update()
