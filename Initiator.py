from Time import Time
from Game import Game
from Board import Board
from Player import Player
from Player import Dork
from API import API
from Log import StatisticsLogger
from Log import Log
from Printer import Printer
import json

API_ON = True
NAMES = ['shay', 'snow', 'shaked', 'odeya']
AI = [Dork, Dork, Dork, Dork]
PLAYERS = 4
RUNS = 1000
LOAD_GAME = False
PATH = "saved_games/game182.json"
PRINTER_ON = True
PRINTER_STDOUT = True
PRINTER_OUTFILE = 'outfile.txt'
# the machines that can print
# 0 - default machine   DEFAULT_MACHINE
# 2 - what happened in the game (actions, dice, a player won the longest road)  GAME_RUN_MACHINE
PERMITTED_MACHINES = [False, False, False]


def load_board(board: Board, log):
    board.load_map(log)


def load_game(path):
    with open(path) as json_file:
        game = json.load(json_file)
        board = game['board']
        rounds = game['rounds']
        return board, rounds


def main():
    if not PRINTER_ON:
        Printer.turn_off()
    else:
        Printer.set_permitted_machines(PERMITTED_MACHINES)
        if not PRINTER_STDOUT:
            Printer.set_outfile(PRINTER_OUTFILE)
    names = NAMES[0:PLAYERS]
    runs = 1 if LOAD_GAME else RUNS
    for i in range(runs):
        print('game number : ' + str(i + 1))
        time = Time(PLAYERS)
        statistic_logger = StatisticsLogger()
        log = Log(PLAYERS, time)
        api = API(API_ON, names, time)
        board = Board(api, PLAYERS, log, statistic_logger)
        if LOAD_GAME:
            if not API_ON:
                api.turn_on()
            board_log, rounds_log = load_game(PATH)
            board.load_map(board_log)
        else:
            board.shuffle_map()
        board.log_board()
        players = []  # type: list[Player]
        for i in range(PLAYERS):
            player = AI[i](i, board)
            players += [player]
        game = Game(api, players, board, time, PLAYERS)
        if LOAD_GAME:
            # noinspection PyUnboundLocalVariable
            game.load_game(rounds_log)
        else:
            game.play_game()
    if PRINTER_ON and not PRINTER_STDOUT:
        Printer.close_outfile()


print("Hello Initiator")
main()
