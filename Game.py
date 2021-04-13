from Board import Board
import math
from Player import Player
from Player import Dork
from random import randint
from Log import Log


class Game:

    def __init__(self, players):
        self.round = 0
        self.turn = 0
        self.log = Log(players)
        self.board = Board(players, self.log)
        self.players = []
        r = randint(0, players)
        for i in range(players):
            if i == r:
                player = Dork(i, self.board)
            else:
                player = Player(i, self.board)
            self.players += [player]

    def start_game(self):
        for i in range(len(self.players)):
            if self.players[i].is_computer:
                self.players[i].computer_1st_settlement()
            else:
                pass
            self.next_turn()
        for i in range(len(self.players) - 1, -1, -1):
            if self.players[i].is_computer:
                self.players[i].computer_2nd_settlement()
            else:
                pass
            self.next_turn()

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
                player.throw_my_cards(math.floor(num_cards/2))

    def next_turn(self):
        self.log.end_turn()
        self.turn += 1
        if self.turn == len(self.players):
            self.turn = 0
            self.round += 1
        self.board.next_turn(self.turn, self.round)

    def play_round(self):
        for player in self.players:
            self.play_turn(player)
            if max(list(map(lambda x: x.points, self.board.hands))) >= 10:
                break
            self.next_turn()

    def play_turn(self, player):
        self.throw_dice()
        if self.players[player.index].is_computer:
            while player.compute_turn():
                pass

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
                print("player number "+str(hand.index)+" is the winner")
                self.log.end_game()
                self.board.end_game()


# ---- main ---- #


def main():
    game = Game(3)
    game.play_game()


print("Hello Game")
main()
