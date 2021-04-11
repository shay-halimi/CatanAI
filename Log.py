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


def save_game():
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
