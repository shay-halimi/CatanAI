import json
from Resources import Resource
from Auxilary import r2s

game = {'round': []}
rounds = []
this_turn = {'round': 0, 'turn': 0, 'stats': [], 'actions': []}
game_finish = {'round': None, 'winning player': None, 'winning resource': None, 'losing resources': []}
games_stats = []


def information_to_json(hands):
    information = {'settlement': [], 'settlements number': 0}
    for hand in hands:
        for index, settlement in enumerate(hand.settlements_log):
            settlement_info = {'time': index, 'points': hand.points, 'production': settlement.val['sum']}
            for resource in Resource:
                if resource is not Resource.DESSERT:
                    settlement_info[r2s(resource)] = settlement.val[resource]
            information['settlement'] += [settlement_info]
            information['settlements number'] += 1
    return information


def update_history(hands):
    with open('history.json') as json_file:
        history = json.load(json_file)
        history['sample_size'] += len(hands)
        for hand in hands:
            if hand.points > 9:
                if hand.name is "Dork":
                    history["dork"] += 1
                else:
                    history["alpha"] += 1
    with open("history.json", 'w') as outfile:
        json.dump(history, outfile)


def build_data(hands):
    with open('data.json') as json_file:
        information = information_to_json(hands)
        data = json.load(json_file)
        data['settlement'] += information['settlement']
        data['settlements number'] += information['settlements number']
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


def aux_build_statistics(data):
    st = dict()
    st['total events'] = 0
    st['total wins'] = 0
    st['production'] = {}
    for resource in Resource:
        if resource is not Resource.DESSERT:
            st[r2s(resource)] = {}
    for settlement in data:
        t = settlement['time']
        production = settlement['production']
        win = 1 if settlement['points'] > 9 else 0
        st['total events'] += 1
        st['total wins'] += win
        if str((t, production)) in st['production']:
            st['production'][str((t, production))]['win'] += win
            st['production'][str((t, production))]['event'] += 1
        else:
            st['production'][str((t, production))] = {'win': win, 'event': 1}
        for resource in Resource:
            if resource is not Resource.DESSERT:
                if str((t, settlement[r2s(resource)])) in st[r2s(resource)]:
                    st[r2s(resource)][str((t, settlement[r2s(resource)]))]['win'] += win
                    st[r2s(resource)][str((t, settlement[r2s(resource)]))]['event'] += 1
                else:
                    st[r2s(resource)][str((t, settlement[r2s(resource)]))] = {'event': 1, 'win': win}
    return st


def build_statistics():
    with open('data.json') as json_file:
        data = json.load(json_file)
        statistics = {'settlement': aux_build_statistics(data['settlement'])}

    with open('statistics.json', 'w') as outfile:
        json.dump(statistics, outfile)


class Log:
    def __init__(self, players):
        build_statistics()
        self.round = 0
        self.turn = 0
        self.players = players

        self.turn_log = {'turn': 0, 'actions': []}
        self.round_log = {'round': 0, 'turns': []}
        self.game_log = {'number of players': players, 'rounds': []}
        self.game_log_name = self.create_file_name()

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
