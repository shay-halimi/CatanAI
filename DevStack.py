# from collections import deque
from random import shuffle


class DevCard:
    name = "DevCard"
    ok_to_use = False

    def get_name(self):
        return self.name

    def is_valid(self):
        return self.ok_to_use


class KnightCard(DevCard):
    name = "knight"


class VictoryPointCard(DevCard):
    name = "victory points"
    ok_to_use = True


class Monopole(DevCard):
    name = "monopole"


class RoadBuilding(DevCard):
    name = "road builder"


class YearOfProsper(DevCard):
    name = "year of prosper"


class DevStack:
    def __init__(self):
        self.deck = []
        for i in range(14):
            self.deck += [KnightCard()]
        for i in range(5):
            self.deck += [VictoryPointCard()]
        for i in range(2):
            self.deck += [Monopole()]
        for i in range(2):
            self.deck += [RoadBuilding()]
        for i in range(2):
            self.deck += [YearOfProsper()]
        shuffle(self.deck)

    def get(self):
        if self.deck:
            card = self.deck.pop()
            return card
        return None

    def return_card(self, card):
        self.deck.append(card)

    def has_cards(self):
        if len(self.deck) != 0:
            return True
        return False
