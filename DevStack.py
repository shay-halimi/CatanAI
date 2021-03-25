# from collections import deque
from random import shuffle


class DevStack:
    deck = ["knight", "knight", "knight", "knight", "knight", "knight", "knight", "knight", "knight", "knight", "knight", "knight"
        , "knight", "knight", "win_point", "win_point", "win_point", "win_point", "win_point", "monopole", "monopole",
        "2_free_roads", "2_free_roads", "2_free_resources", "2_free_resources"]

    def __init__(self):
        # TODO : make it work
        shuffle(self.deck)
        pass

    def get(self):
        card=self.deck.pop()
        return card

