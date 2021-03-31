from enum import Enum
from Resources import Resource
from Board import Board


class Player:
    resources = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.SHEEP: 0, Resource.IRON: 0, Resource.WHEAT: 0}
    devCards = []

    def __init__(self, index, name=None, is_computer=False):
        self.index = index
        self.name = name
        self.is_computer = is_computer
        self.devCards = []
        self.longest_road = 0
        self.board = None

    def buy_devops(self):
        if self.resources[Resource.SHEEP] < 1 or self.resources[Resource.IRON] < 1 or self.resources[
            Resource.WHEAT] < 1:
            print("Not enough resources")
            return False
        self.resources[Resource.SHEEP] -= 1
        self.resources[Resource.IRON] -= 1
        self.resources[Resource.WHEAT] -= 1
        return True

    def buy_settelement(self):
        if self.resources[Resource.SHEEP] < 1 or self.resources[Resource.CLAY] < 1 or self.resources[
            Resource.WHEAT] < 1 or self.resources[Resource.WOOD] < 1:
            print("Not enough resources")
            return
        self.resources[Resource.SHEEP] -= 1
        self.resources[Resource.WOOD] -= 1
        self.resources[Resource.WHEAT] -= 1
        self.resources[Resource.CLAY] -= 1
        # TODO need to add the settlement to the map with the right color
        return

    def buy_City(self):
        if self.resources[Resource.IRON] < 3 or self.resources[Resource.WHEAT] < 2:
            print("Not enough resources")
            return
        self.resources[Resource.WHEAT] -= 2
        self.resources[Resource.IRON] -= 3
        # TODO need to add the city to the map with the right color
        return

    def buy_road(self):
        if self.resources[Resource.CLAY] < 1 or self.resources[Resource.WOOD] < 1:
            print("Not enough resources")
            return
        self.resources[Resource.CLAY] -= 1
        self.resources[Resource.WOOD] -= 1

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
