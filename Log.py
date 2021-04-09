import json
from Resources import Resource

game = {'round': []}
curr_rnd = []


def next_turn(rnd, turn, hands):
    if turn == 0:
        global curr_rnd
        game['round'].append(curr_rnd)
        curr_rnd = []
    this_turn = {'round': rnd, 'turn': turn, 'stats': []}
    for h in hands:
        this_turn['stats'].append({
            'name': h.name,
            'points': h.points,
            'total number of resources': h.get_resources_number(),
            'wood': h.resources[Resource.WOOD],
            'clay': h.resources[Resource.WOOD],
            'wheat': h.resources[Resource.WOOD],
            'sheep': h.resources[Resource.WOOD],
            'iron': h.resources[Resource.WOOD],
            'largest army': h.largest_army,
            'longest road': h.longest_road,
            'victory points': len(h.cards["victory points"]),
            'knight': len(h.cards["knight"]),
            'monopole': len(h.cards["monopole"]),
            'road builder': len(h.cards["road builder"]),
            'year of prosper': len(h.cards["year of prosper"])
        })
    curr_rnd.append(this_turn)


def save_game():
    with open("game.json", 'w') as outfile:
        json.dump(game, outfile)
