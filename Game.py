from Board import Board
import Dice
from Player import Player
import DevStack


class Game:
    def __init__(self, n_players=3):
        self.map = Board()
        self.players = Player()[n_players]
        self.devStack = DevStack()

    def start_game(self):
        for i in len(self.players):
            settlement_is_valid = False
            while not settlement_is_valid:
                print("Player", i, "In Which location do you want to build your 1st settlement?")
                loc_coords = input()
                # TODO need to check that coord are valid i.e. within the board and not within less than 2 edges
                #  frrom other settelment
                settlement_is_valid = True
                # TODO need to add the settelment to the map
            road_is_valid = False
            while not road_is_valid:
                print("Player", i, "In Which location do you want to build your road?")
                road_coords = input()
                # TODO need to check if road location is valid and even let the player choose only 1 from 3 choices
                # TODO need to add road to the map
                road_is_valid = True
        for i in range(len(self.players), 0, -1):
            while not settlement_is_valid:
                print("Player", i, "In Which location do you want to build your 2nd settlement?")
                loc_coords = input()
                # TODO need to check that coord are valid i.e. within the board and not within less than 2 edges
                #  frrom other settelment
                settlement_is_valid = True
                # TODO need to add the settelment to the map
                # TODO need to add resources to the players according to the settlement's location
            road_is_valid = False
            while not road_is_valid:
                print("Player", i, "In Which location do you want to build your road?")
                road_coords = input()
                # TODO need to check if road location is valid and even let the player choose only 1 from 3 choices
                # TODO need to add road to the map
                road_is_valid = True
