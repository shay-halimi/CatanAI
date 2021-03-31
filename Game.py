from Board import Board
import Dice
from Player import Player
import DevStack


class Game:
    def buy_dev_card(self, player):
        if player.buy_devops():
            player.devCards.append(self.devStack.get())

    def __init__(self, players):
        self.board = Board(players)
        self.players = []
        for i in range(players):
            player = Player(i, self.board)
            self.players += [player]

    def start_game(self):
        for i in range(len(self.players)):
            if self.players[i].is_computer:
                crossroad, road = self.players[i].computer_1st_settlement()
                crossroad.build_first(i)
                crossroad.connected[i] =True
                road.build(i)
            else:
                pass
        for i in range(len(self.players) - 1, -1, -1):
            if self.players[i].is_computer:
                crossroad, road = self.players[i].computer_1st_settlement()
                crossroad.build_first(i)
                crossroad.connected[i] = True
                road.build(i)
            else:
                pass

    def throw_dice(self):
        for i, j in self.board.dice.throw():
            self.board.map[i][j].produce()

    def play_round(self):
        for player in range(len(self.players)):
            self.play_turn(player)
            if max(list(map(lambda x: x.points, self.board.hands))) >= 10:
                break

    def compute_turn(self, player):
        pass

    def play_turn(self, player):
        if self.players[player].is_computer:
            Game.compute_turn(self, player)

    def play_game(self):
        num_players = input("how many players are playing?")
        game = Game(num_players)
        game.start_game()
        while max(list(map(lambda x: x.points, game.board.hands))) < 10:
            game.play_round()


# ---- main ---- #


def main():
    game = Game(3)
    game.start_game()


print("Hello Game")
main()
