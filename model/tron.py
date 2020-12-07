class Direction:
    ALL = [(-1, -1), (0, -1), (1, -1), (1, 0),
           (1, 1), (0, 1), (-1, 1), (-1, 0)]

    _, UP, _, RIGHT, _, DOWN, _, LEFT = ALL

    @staticmethod
    def opposite_of(direction):
        idx = Direction.ALL.index(direction)
        return Direction.ALL[(idx + len(Direction.ALL) // 2) % len(Direction.ALL)]


class TronGame:
    '''
    TronGame Constructor
    Parameters:
    width - board horizontal size
    height - board vertical size
    players - list of head -> board -> Move
    seeds - list of (x, y)
    '''

    def __init__(self, width, height, players, seeds):
        self.width = width
        self.height = height
        self.seeds = seeds
        self.setup(players, seeds)

    def setup(self, players, seeds):
        self.players = [(True, head, player) for head, player in zip(
            seeds, players)] if players and seeds else []
        self.board = [[None for line in range(self.width)]
                      for column in range(self.height)]
        self.remaining = len(self.players)

        # update board with player positions
        for idx, player in enumerate(self.players):
            _, head, _ = player
            x, y = head
            self.board[x][y] = idx

    def reset(self):
        players = [player for _, _, player in self.players]
        self.setup(players, self.seeds)

    def next_state(self):
        if self.players and not self.is_over():
            for idx, player in enumerate(self.players):
                active, head, action = player

                if active:
                    self.ask_move(idx, head, action)

    def ask_move(self, idx, head, action):
        x, y = head

        # ask the player's move
        heading = action(head, self.board)
        x, y = head_to(head, heading)

        # check bounds
        if (x >= 0 and x < self.width) and (y >= 0 and y < self.height):
            if self.board[x][y] is None:
                self.board[x][y] = idx
                self.players[idx] = (True, (x, y), action)
            else:
                self.invalidate_player(idx)
        else:
            self.invalidate_player(idx)

    '''
    def next_position(self, head, direction):
        x, y = head

        if direction == TronGame.UP:
            y -= 1
        elif direction == TronGame.DOWN:
            y += 1
        elif direction == TronGame.LEFT:
            x -= 1
        elif direction == TronGame.RIGHT:
            x += 1

        return (x, y)
    '''

    def invalidate_player(self, idx):
        active, head, action = self.players[idx]

        if active:
            self.players[idx] = (False, head, action)
            self.remaining -= 1

    def get_board(self):
        return self.board

    def get_remaining(self):
        return self.remaining

    def get_winner(self):
        return None

    def is_over(self):
        return self.get_remaining() <= 1


def head_to(head, heading):
    x, y = head
    i, j = heading
    return x + i, y + j


def get_orientation_vector(heading):
    heading_index = Direction.ALL.index(heading)
    amount = len(Direction.ALL)

    return [Direction.ALL[(heading_index + idx) % amount]
            for idx in range(-3, 4)]


def get_boundary(head, heading, tron_game):
    board = tron_game.get_board()
    last = head
    x, y = head_to(head, heading)

    while (x >= 0 and x < tron_game.width and y >= 0 and y < tron_game.height) and board[x][y] is None:
        last = (x, y)
        x, y = head_to((x, y), heading)

    return last


def get_all_boundaries(head, heading, tron_game):
    directions = get_orientation_vector(heading)
    return map(lambda direction: get_boundary(head, direction, tron_game), directions)
