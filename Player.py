from enum import Enum
from DevStack import DevStack
import Game
from Resources import Resource

class Player:
    resources = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.SHEEP: 0, Resource.IRON: 0, Resource.WHEAT: 0}
    devCards = []

    def __init__(self, index, name=None):
        self.index = index
        self.name = name
        self.resources = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.SHEEP: 0, Resource.IRON: 0, Resource.WHEAT: 0}
        self.devCards = []

    def add_resources(resource, number):
        Player.resources[resource] += number

    def buy_devops(self):
        if Resource.SHEEP < 1 or Resource.IRON < 1 or Resource.WHEAT < 1:
            print("Not enough resources")
            return
        self.resources[Resource.SHEEP] -= 1
        self.resources[Resource.IRON] -= 1
        self.resources[Resource.WHEAT] -= 1
        self.devCards.append(Game.devStack.get())

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
