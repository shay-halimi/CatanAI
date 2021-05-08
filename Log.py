import json
from random import uniform


class Log:
    def __init__(self, players):
        self.round = 0
        self.turn = 0
        self.players = players

        self.turn_log = {'turn': 0, 'actions': []}
        self.round_log = {'round': 0, 'turns': []}
        self.game_log = {'number of players': players, 'rounds': []}
        self.game_log_name = self.create_file_name()

        self.statistic = {}

    def next_turn(self):
        self.round_log['turns'] += [self.turn_log]
        if self.turn == self.players - 1:
            self.turn = 0
            self.round += 1
            self.game_log['rounds'] += [self.round_log]
            self.round_log = {'round': self.round, 'turns': []}
        else:
            self.turn += 1
        self.turn_log = {'turn': self.turn, 'actions': []}

    def dice(self, dice):
        self.turn_log['dice'] = dice

    def action(self, action_log):
        self.turn_log['actions'] += [action_log]

    def end_game(self):
        with open(self.game_log_name, 'w') as outfile:
            json.dump(self.game_log, outfile)
        self.track_development(1)
        self.track_development(10)
        self.track_development(100)

    def track_development(self, res):
        stop = res
        res = str(res)
        with open('tracking_development.json') as json_file:
            tracker = json.load(json_file)
            if res not in tracker['resolution']:
                tracker['resolution'][res] = {'counter': 0, 'sum': 0, 'games': []}
            counter = tracker['resolution'][res]['counter']
            sum = tracker['resolution'][res]['sum']
            counter += 1
            sum += self.round
            if counter >= stop:
                tracker['resolution'][res]['games'] += [sum / counter]
                counter = 0
                sum = 0
            tracker['resolution'][res]['counter'] = counter
            tracker['resolution'][res]['sum'] = sum
        with open('tracking_development.json', 'w') as outfile:
            json.dump(tracker, outfile)

    def board(self, board_log):
        self.game_log['board'] = board_log

    @staticmethod
    def create_file_name():
        with open("saved_games/manager.json") as json_file:
            manager = json.load(json_file)
        name = "saved_games/game" + str(manager['games saved'] + 1) + ".json"
        manager['games saved'] += 1
        with open("saved_games/manager.json", 'w') as outfile:
            json.dump(manager, outfile)
        return name


class StatisticsLogger:
    def __init__(self):
        self.actions = []
        with open("statistics.json") as json_file:
            self.statistics = json.load(json_file)
        self.actions_to_point = {}

    def save_action(self, index, e_keys, r_keys):
        if index not in self.actions_to_point:
            self.actions_to_point[index] = []
        self.actions += [(index, e_keys, r_keys)]
        self.actions_to_point[index] += [(e_keys, r_keys)]

    def got_point(self, index):
        for i, action in enumerate(self.actions_to_point[index][::-1]):
            e_keys, r_keys = action
            pointer = self.statistics['actions']
            for key in e_keys:
                key = str(key)
                if key not in pointer:
                    pointer[key] = {'events': 0, 'wins': 0}
                if 'actions to point' not in pointer[key]:
                    pointer[key]['actions to point'] = {}
                if str(i + 1) not in pointer[key]['actions to point']:
                    pointer[key]['actions to point'][str(i + 1)] = 0
                pointer[key]['actions to point'][str(i + 1)] += 1
                pointer = pointer[key]
            for key in r_keys:
                key = str(key)
                if key not in pointer:
                    pointer[key] = {'events': 0, 'wins': 0}
                if 'actions to point' not in pointer[key]:
                    pointer[key]['actions to point'] = {}
                if str(i + 1) not in pointer[key]['actions to point']:
                    pointer[key]['actions to point'][str(i + 1)] = 0
                pointer[key]['actions to point'][str(i + 1)] += 1
        self.actions_to_point[index] = []

    def end_game(self, winner):
        for action in self.actions:
            index, e_keys, r_keys = action
            win = 1 if winner == index else 0
            pointer = self.statistics['actions']
            for key in e_keys:
                key = str(key)
                if key in pointer:
                    pointer[key]['events'] += 1
                    pointer[key]['wins'] += win
                else:
                    pointer[key] = {'events': 1, 'wins': win}
                pointer = pointer[key]
            for key in r_keys:
                if key in pointer:
                    pointer[key]['events'] += 1
                    pointer[key]['wins'] += win
                else:
                    pointer[key] = {'events': 1, 'wins': win}
        with open('statistics.json', 'w') as out_file:
            json.dump(self.statistics, out_file)

    def get_statistic(self, essentials, regulars):
        pointer = self.statistics['actions']
        for key in essentials:
            if key in pointer:
                pointer = pointer[key]
            else:
                return uniform(0, 0.66)
        statistics = []
        for key in regulars:
            total_events = pointer['events']
            total_wins = pointer['wins']
            events = pointer[key]['events']
            wins = pointer[key]['wins']
            statistics += [Statistic(events, wins, total_wins, total_events - total_wins)]
        st = statistics_merge(statistics)   # type: Statistic
        events = st.event
        wins = st.win
        return wins / events

    def get_actions_to_point(self, essentials, regulars):
        pointer = self.statistics['actions']
        for key in essentials:
            if key in pointer:
                pointer = pointer[key]
            else:
                return 4
        sum_actions = 0
        sum_actions_to_point = 0
        for k, v in pointer['actions to point'].items:
            sum_actions += v
            sum_actions_to_point += k * v
        for key in regulars:
            for k, v in pointer[key]['actions to point'].items:
                sum_actions += v
                sum_actions_to_point += k * v
        return sum_actions_to_point / sum_actions


def statistics_merge(statistics):
    if not statistics:
        return uniform(0, 0.66)
    else:
        st = statistics.pop()   # type: Statistic
        while statistics:
            st.merge(statistics.pop())
    return st


class Statistic:
    def __init__(self, event, win, total_win, total_lose):
        self.total_win = total_win
        self.total_lose = total_lose
        self.event = event
        self.win = win
        self.lose = event - win
        self.win_ratio = self.win / self.total_win

    # Todo: check correctness with professor
    def merge(self, statistic):
        self.win = self.win * statistic.win / self.total_win
        self.lose = self.lose * statistic.lose / self.total_lose
        self.event = self.win + self.lose
        self.win_ratio = self.win / self.event

