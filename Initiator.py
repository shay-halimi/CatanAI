from Game import Game
from Board import Board
from Player import Dork
from API import API

API_ON = False
NAMES = ['shay', 'snow', 'shaked', 'odeya']
PLAYERS = 4
RUNS = 1


def main():
    for i in range(RUNS):
        names = NAMES[0:PLAYERS]
        game = Game(PLAYERS, names)
        game.play_game()


print("Hello Initiator")
main()
