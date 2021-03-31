from enum import Enum
from Resources import Resource
from Board import Board


class Player:
    resources = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.SHEEP: 0, Resource.IRON: 0, Resource.WHEAT: 0}
    devCards = []

    def __init__(self, index, board, name=None, is_computer=False):
        self.index = index
        self.name = name
        self.is_computer = is_computer
        self.devCards = []
        self.longest_road = 0
        self.board = board
        self.hand = board.hands[index]

    def buy_devops(self):
        return self.hand.buy_development_card()

    def buy_settlement(self, cr):
        return self.hand.buy_settlement()

    def buy_city(self, cr):
        return self.hand.buy_city(cr)

    def buy_road(self, road):
        return self.hand.buy_road(road)

    def use_knight(self):
        if "knight" in self.devCards:
            self.devCards.remove("knight")
            # TODO add a function to move the robber and get one reasource card frrom another player

    #########################################################################
    # AI player functions
    #########################################################################
    def computer_1st_settlement(self):
        return (0, 0), (0, 0)

    def computer_2nd_settlement(self):
        return (1, 1), (1, 1)
