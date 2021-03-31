# from collections import deque
from random import shuffle


class DevCard:
    name = "DevCard"
    ok_to_use = False


class KnightCard(DevCard):
    name = "knight"


class VictoryPointCard(DevCard):
    name = "victory point"
    ok_to_use = True


class Monopole(DevCard):
    name = "monopole"


class RoadBuilding(DevCard):
    name = "road building"


class YearOfPlenty(DevCard):
    name = "year of pleanty"


class DevStack:
    def __init__(self):
        self.deck = []
        for i in range(14):
            self.deck += [KnightCard()]
        for i in range(5):
            self.deck+= [VictoryPointCard()]
        for i in range(2):
            self.deck += [Monopole()]
        for i in range(2):
            self.deck += [RoadBuilding()]
        for i in range(2):
            self.deck += [YearOfPlenty()]
        shuffle(self.deck)

    def get(self):
        card = self.deck.pop()
        return card

    def has_cards(self):
        if len(self.deck) != 0:
            return True
        return False
