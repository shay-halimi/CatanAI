from Board import Board
import Dice
from Player import Player
import DevStack


class Game:
    def buy_dev_card(self, player):
        if player.buy_devops():
            player.devCards.append(self.devStack.get())

    def __init__(self, n_players=3):
        self.map = Board()
        self.players = []
        for i in range(n_players):
            self.players += [Player(i)]
        self.devStack = DevStack.DevStack()

    # ToDo (shay) : link to API
    def start_game(self):
        for i in range(len(self.players)):
            settlement_is_valid = False
            while not settlement_is_valid:
                # ToDo: implement for cp agents as well
                print("Player", i, "In Which location do you want to build your 1st settlement?")
                loc_coords = input()
                # TODO need to check that coord are valid i.e. within the board and not within less than 2 edges
                #  from other settlement
                # ToDo (shay) : update the choice in Board (map).
                settlement_is_valid = True
                # TODO need to add the settelment to the map
            road_is_valid = False
            while not road_is_valid:
                # ToDo: implement for cp agents as well
                print("Player", i, "In Which location do you want to build your road?")
                road_coords = input()
                # ToDo (shay) : update the choice in Board (map).
                # TODO need to check if road location is valid and even let the player choose only 1 from 3 choices
                # TODO need to add road to the map
                road_is_valid = True
        for i in range(len(self.players)-1, -1, -1):
            settlement_is_valid = False
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
