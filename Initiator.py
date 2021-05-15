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
from time import perf_counter

API_ON = False
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
# 0 - default machine
# 1 - time tracking
PERMITTED_MACHINES = [False, True]
TRACK_TIME = True


def load_board(board: Board, log):
    board.load_map(log)


def load_game(path):
    with open(path) as json_file:
        game = json.load(json_file)
        board = game['board']
        rounds = game['rounds']
        return board, rounds


def main():
    with open('time_tracking.json', 'w') as outfile:
        json.dump({}, outfile)
    if not PRINTER_ON:
        Printer.turn_off()
    else:
        Printer.set_permitted_machines(PERMITTED_MACHINES)
        if not PRINTER_STDOUT:
            Printer.set_outfile(PRINTER_OUTFILE)
    names = NAMES[0:PLAYERS]
    runs = 1 if LOAD_GAME else RUNS
    for i in range(runs):
        tic = perf_counter()
        Printer.use_machine(1)
        print('game number : ' + str(i + 1))
        Printer.ret_to_def_machine()
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
        rounds = 0
        if LOAD_GAME:
            # noinspection PyUnboundLocalVariable
            rounds = game.load_game(rounds_log)
        else:
            rounds = game.play_game()
        toc = perf_counter()
        seconds = toc - tic
        if TRACK_TIME:
            with open('time_tracking.json') as json_file:
                tracker = json.load(json_file)
                key = str(rounds)
                if key not in tracker:
                    tracker[key] = {'average': 0, 'events': 0, 'total time': 0}
                tracker[key]['events'] += 1
                tracker[key]['total time'] += seconds
                tracker[key]['average'] = tracker[key]['total time'] / tracker[key]['events']
                with open('time_tracking.json', 'w') as outfile:
                    json.dump(tracker, outfile)
        if PERMITTED_MACHINES[1]:
            Printer.use_machine(1)
            Printer.printer('#########################')
            Printer.printer('time to run the entire game : ' + str(seconds))
            Printer.printer('total rounds : ' + str(rounds))
            Printer.printer('#########################\n')
            Printer.ret_to_def_machine()

    if PRINTER_ON and not PRINTER_STDOUT:
        Printer.close_outfile()


print("Hello Initiator")
main()
