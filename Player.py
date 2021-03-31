from Resources import Resource
from Board import Board


class Player:
    def __init__(self, index, board: Board, name=None, is_computer=False):
        self.index = index
        self.name = name
        self.is_computer = is_computer
        self.board = board
        self.hand = board.hands[index]

    def buy_devops(self):
        return self.hand.buy_development_card()

    def buy_settlement(self, cr):
        return self.hand.buy_settlement(cr)

    def buy_city(self, cr):
        return self.hand.buy_city(cr)

    def buy_road(self, road):
        return self.hand.buy_road(road)

    def use_knight(self, terrain, dst):
        self.hand.use_knight(terrain, dst)

    #########################################################################
    # AI player functions
    #########################################################################
    def computer_1st_settlement(self):
        return (0, 0), (0, 0)

    def computer_2nd_settlement(self):
        return (1, 1), (1, 1)
