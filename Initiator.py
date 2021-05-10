from Time import Time
from Game import Game
from Board import Board
from Player import Dork
from API import API
from Log import StatisticsLogger
from Log import Log

API_ON = False
NAMES = ['shay', 'snow', 'shaked', 'odeya']
PLAYERS = 4
RUNS = 1


def main():
    names = NAMES[0:PLAYERS]
    for i in range(RUNS):
        time = Time(PLAYERS)
        statistic_logger = StatisticsLogger()
        log = Log(PLAYERS)
        board = Board(PLAYERS, log)
        game = Game(time, PLAYERS, names)
        game.play_game()


print("Hello Initiator")
main()
