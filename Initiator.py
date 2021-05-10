from Time import Time
from Game import Game
from Board import Board
from Player import Dork
from API import API

API_ON = False
NAMES = ['shay', 'snow', 'shaked', 'odeya']
PLAYERS = 4
RUNS = 1


def main():
    names = NAMES[0:PLAYERS]
    for i in range(RUNS):
        time = Time(PLAYERS)
        game = Game(time, PLAYERS, names)
        game.play_game()


print("Hello Initiator")
main()
