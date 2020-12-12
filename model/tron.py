class Direction:
    ALL = [(-1, -1), (0, -1), (1, -1), (1, 0),
           (1, 1), (0, 1), (-1, 1), (-1, 0)]

    _, UP, _, RIGHT, _, DOWN, _, LEFT = ALL

    @staticmethod
    def shift(direction, amount):
        idx = Direction.ALL.index(direction)
        return Direction.ALL[(idx + amount) % len(Direction.ALL)]

    @staticmethod
    def opposite_of(direction):
        return Direction.shift(len(Direction.ALL) // 2)


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
        winner = None

        def is_active(enumerated):
            _, player = enumerated
            active, _, _ = player

            return active

        if self.is_over():
            remaining = list(filter(is_active, enumerate(self.players)))

            if remaining:
                [player] = remaining
                winner, _ = player

        return winner

    def is_over(self):
        return self.get_remaining() <= 1


class TronPlayer:
    def __init__(self, direction):
        self.seed = direction
        self.direction = direction
        self.head = None

    def reset(self):
        self.direction = self.seed
        self.head = None

    def action(self):
        def feedback(head, board):
            self.head = head_to(head, self.direction)
            return self.direction

        return feedback

    def set_direction(self, direction, override=False):
        if override or not direction == Direction.opposite_of(self.direction):
            self.direction = direction


def head_to(head, heading):
    x, y = head
    i, j = heading
    return x + i, y + j


def get_orientation_vector(heading):
    heading_index = Direction.ALL.index(heading)
    amount = len(Direction.ALL)

    return [Direction.ALL[(heading_index + idx) % amount]
            for idx in range(-3, 4)]


def get_boundary(head, heading, board):
    last = head
    x, y = head_to(head, heading)

    width = len(board[0]) if board else 0
    height = len(board)

    while (x >= 0 and x < width and y >= 0 and y < height) and board[x][y] is None:
        last = (x, y)
        x, y = head_to((x, y), heading)

    return last


def get_all_boundaries(head, heading, board):
    directions = get_orientation_vector(heading)
    return map(lambda direction: get_boundary(head, direction, board), directions)
