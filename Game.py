from Player import Player
from Player import Dork
from Player import LogToAction
from Board import Board
from Log import Log
import API
from Resources import Resource
import math
from random import randint
import json


class Game:

    def __init__(self, players, board_log=None):
        self.round = 0
        self.turn = 0
        self.players = self.create_players(players)
        self.board = self.create_board(players, board_log)
        self.log = Log(players)
        # create the API
        API.start_api(self.board)

    def start_game(self):
        for i in range(len(self.players)):
            self.log.turn_log['resources'] = {'wood': self.players[i].hand.resources[Resource.WOOD],
                                              'clay': self.players[i].hand.resources[Resource.CLAY],
                                              'sheep': self.players[i].hand.resources[Resource.SHEEP],
                                              'wheat': self.players[i].hand.resources[Resource.WHEAT],
                                              'iron': self.players[i].hand.resources[Resource.IRON]}
            if self.players[i].is_computer:
                self.players[i].computer_1st_settlement()
            else:
                pass
            self.next_turn()
        for i in range(len(self.players) - 1, -1, -1):
            self.log.turn_log['resources'] = {'wood': self.players[i].hand.resources[Resource.WOOD],
                                              'clay': self.players[i].hand.resources[Resource.CLAY],
                                              'sheep': self.players[i].hand.resources[Resource.SHEEP],
                                              'wheat': self.players[i].hand.resources[Resource.WHEAT],
                                              'iron': self.players[i].hand.resources[Resource.IRON]}
            if self.players[i].is_computer:
                self.players[i].computer_2nd_settlement()
            else:
                pass
            self.next_turn()

    def play_game(self):
        self.start_game()
        while max(list(map(lambda x: x.points, self.board.hands))) < 10:
            if self.round > 200:
                print("to many rounds")
                return
            self.play_round()
            print(self.round)
            for hand in self.board.hands:
                for typeCard in hand.cards.values():
                    if typeCard:
                        for card in typeCard:
                            card.ok_to_use = True
        for hand in self.board.hands:
            if hand.points >= 10:
                # TODO need to call Log.finish_game
                print("player number " + str(hand.index) + " is the winner")
                self.log.end_game()

    def play_round(self):
        for player in self.players:
            self.play_turn(player)
            if max(list(map(lambda x: x.points, self.board.hands))) >= 10:
                break
            self.next_turn()

    def play_turn(self, player):
        self.log.turn_log['resources'] = {'wood': player.hand.resources[Resource.WOOD],
                                          'clay': player.hand.resources[Resource.CLAY],
                                          'sheep': player.hand.resources[Resource.SHEEP],
                                          'wheat': player.hand.resources[Resource.WHEAT],
                                          'iron': player.hand.resources[Resource.IRON]}
        self.throw_dice()
        if self.players[player.index].is_computer:
            while player.compute_turn():
                pass

    def next_turn(self):
        self.log.end_turn()
        self.turn += 1
        if self.turn == len(self.players):
            self.turn = 0
            self.round += 1
        self.board.next_turn(self.turn, self.round)

    def throw_dice(self):
        for i, j in self.board.dice.throw():
            self.board.map[i][j].produce()
            self.log.dice(self.board.dice.sum)
        if self.board.dice.sum == 7:
            self.throw_cards()

    def throw_cards(self):
        for player in self.players:
            num_cards = sum(player.hand.resources.values())
            if num_cards > 7:
                player.throw_my_cards(math.floor(num_cards / 2))

    def load_game(self, rounds):
        for r, round in enumerate(rounds):
            for t, turn in enumerate(round['turns']):
                print("\n\n\n round : " + str(round['round']) + " | turn : " + str(turn['turn']))
                if 'dice' in turn:
                    print("dice : " + str(turn['dice']))
                    self.load_dice(turn['dice'])
                print("resources : " + str(self.players[t].hand.resources))
                for i, action in enumerate(turn['actions']):
                    print(action)
                    player = self.players[action['player']]
                    a = LogToAction(self.board, player, action)
                    b = a.get_action()
                    if not b.is_legal():
                        print("name : " + b.name + " | round : " + str(r) + " | turn : " + str(i))
                        return
                    b.do_action()
                self.board.next_turn(t, r)

    def load_dice(self, num):
        for i, j in self.board.dice.load(num):
            self.board.map[i][j].produce()
            self.log.dice(self.board.dice.sum)
        if self.board.dice.sum == 7:
            self.throw_cards()

    def create_board(self, players, board_log=None):
        board = Board(players, self.log)
        if board_log:
            self.board.load_map(board_log)
        else:
            self.board.shuffle_map()
        # log the board
        self.board.log_board()
        return board

    def create_players(self, num):
        players = []
        r = randint(0, num)
        for i in range(num):
            if i == r:
                player = Dork(i, self.board)
            else:
                player = Player(i, self.board)
            self.players += [player]
        return players


# ---- main ---- #


def load_game(path):
    with open(path) as json_file:
        game = json.load(json_file)
        board = game['board']
        rounds = game['rounds']
    turn_off = False
    if API.api_off:
        turn_off = True
        API.turn_api_on()
    game = Game(3, board)
    game.load_game(rounds)
    if turn_off:
        API.turn_api_off()


def play_game(num):
    for i in range(num):
        game = Game(3)
        game.play_game()


def main():
    # play_game(1)
    load_game("saved_games/game124.json")


print("Hello Game")
main()
