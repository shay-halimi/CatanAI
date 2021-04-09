from Board import Board


class SimpleHeuristic:
    def __init__(self, id, board: Board):
        self.id = id
        self.board = board
        self.hand = board.hands[id]