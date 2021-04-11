import json
from Resources import Resource
from Auxilary import r2s

game = {'round': []}
rounds = []
this_turn = {'round': 0, 'turn': 0, 'stats': [], 'actions': []}
game_finish = {'round': None, 'winning player': None, 'winning resource': None, 'losing resources': []}
games_stats = []


def end_game(rnd, win_player, hands):
    global game_finish
    game_finish['round'] = rnd
    game_finish['winning player'] = win_player
    game_finish['winning resource'] = max(hands[win_player].production, key=hands[win_player].production.get)
    for hand in hands:
        if hand.index != win_player:
            game_finish['losing resources'].append(max(hand.production, key=hand.production.get))


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
            'year of prosper': len(h.cards["year of prosper"])
        })
    rounds.append(this_turn)


def add_trade(trade):
    action = {'name': trade.name, 'source type': r2s(trade.src), 'give': trade.give, 'destination type': r2s(trade.dst),
              'take': trade.take}
    global this_turn
    this_turn['actions'].append(action)


def information_to_json(hands):
    information = {'settlement': [], 'settlements number': 0}
    for hand in hands:
        for index, settlement in enumerate(hand.settlements):
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
    with open("actions.json", 'w') as outfile:
        actions = []
        for rnd in game['round']:
            for turn in rnd:
                for action in turn['actions']:
                    zip = {'round': turn['round'], 'turn': turn['turn'], 'action': action}
                    actions += [zip]
        json.dump(actions, outfile)
    with open('data.json') as json_file:
        information = information_to_json(hands)
        data = json.load(json_file)
        data['settlement'] += information['settlement']
        data['settlements number'] += information['settlements number']
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    build_statistics()
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


def build_statistics():
    with open('data.json') as json_file:
        data = json.load(json_file)
        statistics = {'settlement': {}}
        st = dict()
        st['production'] = {}
        for resource in Resource:
            if resource is not Resource.DESSERT:
                st[r2s(resource)] = {}
        for settlement in data['settlement']:
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
        statistics['settlement'] = st
    with open('statistics.json', 'w') as outfile:
        json.dump(statistics, outfile)
