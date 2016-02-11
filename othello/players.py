import numpy as np
from othello.game import *
from copy import deepcopy


class Player:
    """
    Represents the players in the game; white and black.
    """
    white = 1
    black = -1

    def __init__(self, color):
        self.color = color

    def __str__(self):
        """
        Pretty print the player names, e.g. 'white' or 'black'.
        """
        return self.color

    def __int__(self):
        """
        Get the numeric representation of the player, as used on the board.
        """
        if self.color == 'white':
            return Player.white
        elif self.color == 'black':
            return Player.black
        else:
            raise ValueError

    def get_move(self):
        # implement in subclasses
        pass


class Human(Player):
    """
    This player asks for input from the terminal.
    """

    def get_move(self):
        """
        Ask human for desired move.
        """
        prompt = 'Player %s: ' % str(self)
        position = input(prompt)
        return position


class WeightBoard(Board):
    def __str__(self):
        return str(self._board)

    def __add__(self, other):
        return self._board + other


class AI(Player):
    """
    Base class for MiniMax and AlphaBeta AI agents.
    """

    def __init__(self, color, time_limit=None, edge_weight=3,
                 corner_weight=10,
                 depth=None):
        super().__init__(color)

        if depth is None:
            self.depth = np.inf
        else:
            self.depth = depth

        self.player = int(self)
        self._time_limit = time_limit
        self._weight_board = WeightBoard() + 1

        # set the edges on the weight board
        self._weight_board[:, 0] = edge_weight
        self._weight_board[0, :] = edge_weight
        self._weight_board[:, -1] = edge_weight
        self._weight_board[-1, :] = edge_weight

        # set the corners to the corner weights
        self._weight_board[0, 0] = corner_weight
        self._weight_board[-1, 0] = corner_weight
        self._weight_board[0, -1] = corner_weight
        self._weight_board[-1, -1] = corner_weight

        self._expanded_states = 0

    def result(self, state, a):
        self._expanded_states += 1

        state_copy = deepcopy(state)

        if state.__class__.__name__.startswith('Game'):
            # todo: need a way to copy this properly! (or don't copy at all??)
            state_copy.board = Board()
            state_copy.board._board = state.board._board.copy()

        state_copy.move(a)
        return state_copy

    def utility(self, state):
        """
        Here we use the weight board to gauge how well a player is doing

        :param state: Game, a game state
        :return: float/int, score for the current state given the player set
            at initialization
        """
        # todo: fix this problem!
        # print("\n\n")
        # print(self._weight_board)
        # print(state.board._board)
        # print(self._weight_board * state.board._board)
        # print(self._weight_board * np.arange(64).reshape((8, 8)))
        # print(state * np.arange(64).reshape((8, 8)))

        # utility = np.sum(np.sum(self._weight_board * state))
        utility = np.sum(state.board) * int(self.player)
        print(utility)
        return utility  # * int(self.player)

    def __str__(self):
        return ("%s for player %s: %s expanded states" %
                (self.__class__.__name__, self.player, self._expanded_states))


class MiniMaxAI(AI):

    def search(self, state):
        moves = state.legal_moves()
        scores = [self.min_value(self.result(state, a), self.depth)
                  for a in moves]
        return moves[np.argmax(scores)]

    def max_value(self, state, depth):
        if self.cut_off(state, depth):
            return self.utility(state)
        v = -np.inf
        for a in state.legal_moves():
            v = max(v, self.min_value(self.result(state, a), depth - 1))
        return v

    def min_value(self, state, depth):
        if self.cut_off(state, depth):
            return self.utility(state)
        v = np.inf
        for a in state.legal_moves():
            v = min(v, self.max_value(self.result(state, a), depth - 1))
        return v

    def cut_off(self, state, depth):
        return state.is_terminal() or depth <= 0


class AlphaBetaAI(AI):

    def search(self, state):
        self.best_move = None
        v = self.max_value(state, -np.inf, np.inf)
        return v

    def max_value(self, state, alpha, beta):
        if state.is_terminal():
            return self.utility(state)
        v = -np.inf
        for a in state.legal_moves():
            v = max(v, self.min_value(self.result(state, a), alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, state, alpha, beta):
        if state.is_terminal():
            return self.utility(state)
        v = np.inf
        for a in state.legal_moves():
            v = min(v, self.max_value(self.result(state, a), alpha, beta))
            if v <= alpha:
                return v
            beta = min(alpha, v)
        return v


if __name__ == '__main__':
    board = Board()
    players = [Player('black'), Player('white')]
    game = Game(board, players, visualise=True)
    game.board[3, 2] = int(players[1])
    game.board[3, 1] = int(players[1])

    print(game.board)
    ai = MiniMaxAI(color='black', depth=0)
    print(ai.search(game))