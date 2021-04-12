import json
from Resources import Resource
from Auxilary import r2s

game = {'round': []}
rounds = []
this_turn = {'round': 0, 'turn': 0, 'stats': [], 'actions': []}
game_finish = {'round': None, 'winning player': None, 'winning resource': None, 'losing resources': []}
games_stats = []


def end_game(rnd, win_player, hands):
    global games_stats
    global game_finish
    game_finish['round'] = rnd
    game_finish['winning player'] = win_player
    print()
    print(hands[win_player].production)
    game_finish['winning resource'] = max(hands[win_player].production, key=hands[win_player].production.get)
    for hand in hands:
        if hand.index != win_player:
            print(hand.production)
            game_finish['losing resources'].append(max(hand.production, key=hand.production.get))
    games_stats.append([game_finish])
    print(game_finish)
    return games_stats


def next_turn(rnd, turn, hands):
    global rounds
    if turn == 0:
        game['round'].append(rounds)
        rounds = []
    global this_turn
    this_turn = {'round': rnd, 'turn': turn, 'stats': [], 'actions': []}
    for h in hands:
        this_turn['stats'].append({
            'name': h.name,
            'points': h.points,
            'total number of resources': h.get_resources_number(),
            'wood': h.resources[Resource.WOOD],
            'clay': h.resources[Resource.CLAY],
            'wheat': h.resources[Resource.WHEAT],
            'sheep': h.resources[Resource.SHEEP],
            'iron': h.resources[Resource.IRON],
            'largest army': h.largest_army,
            'longest road': h.longest_road,
            'victory points': len(h.cards["victory points"]),
            'knight': len(h.cards["knight"]),
            'monopole': len(h.cards["monopole"]),
            'road builder': len(h.cards["road builder"]),
            'year of prosper': len(h.cards["year of prosper"]),
        })
    rounds.append(this_turn)


def add_trade(trade):
    action = {'name': trade.name, 'source type': r2s(trade.src), 'give': trade.give, 'destination type': r2s(trade.dst),
              'take': trade.take}
    global this_turn
    this_turn['actions'].append(action)


def build_road(road):
    action = {'name': road.name, 'location': road.road.api_location}
    global this_turn
    this_turn['actions'].append(action)


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


def save_game(hands):
    with open("game.json", 'w') as outfile:
        json.dump(game, outfile)

    # build_statistics()


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
    st['production'] = {}
    for resource in Resource:
        if resource is not Resource.DESSERT:
            st[r2s(resource)] = {}
    for settlement in data:
        t = settlement['time']
        production = settlement['production']
        win = 1 if settlement['points'] > 9 else 0
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
        statistics = {'settlement': aux_build_statistics(data['settlement']),
                      'city': aux_build_statistics(data['city'])}

    with open('statistics.json', 'w') as outfile:
        json.dump(statistics, outfile)


class Log:
    def __init__(self, players):
        self.round = 0
        self.turn = 0
        self.players = players
        self.start_log = {'actions': []}
        self.turn_log = {'turn': 0, 'actions': []}
        self.round_log = {'round': 0, 'turns': []}
        self.game_log = {'number of players': players, 'rounds': []}
        with open("saved_games/manager.json") as json_file:
            manager = json.load(json_file)
        self.game_log_name = "saved_games/game" + str(manager['games saved'] + 1) + ".json"
        manager['games saved'] += 1
        with open("saved_games/manager.json", 'w') as outfile:
            json.dump(manager, outfile)

    def end_turn(self):
        self.round_log['turns'] += [self.turn_log]
        self.turn_log = {'turn': self.turn, 'actions': []}
        if self.turn == self.players - 1:
            self.turn = 0
            self.round += 1
            self.game_log['rounds'] += [self.round_log]
            self.round_log = {'round': self.round, 'turns': []}
        else:
            self.turn += 1

    def dice(self, dice):
        self.turn_log['dice'] = dice

    def action(self, action_log):
        self.turn_log['actions'] += [action_log]

    def end_game(self):
        self.game_log['start'] = self.start_log
        with open(self.game_log_name, 'w') as outfile:
            json.dump(self.game_log, outfile)

    def start_game(self, index, crossroad_log, road_log):
        self.start_log['actions'] += [{'index': index, 'crossroad': crossroad_log, 'road': road_log}]
