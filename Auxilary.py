from Resources import Resource


def r2s(resource: Resource):
    if resource is Resource.WOOD:
        return "wood"
    elif resource is Resource.CLAY:
        return "clay"
    elif resource is Resource.SHEEP:
        return "sheep"
    elif resource is Resource.WHEAT:
        return "wheat"
    elif resource is Resource.IRON:
        return "iron"
    else:
        return "NONE"


def s2r(str):
    if str == "wood":
        return Resource.WOOD
    elif str == "clay":
        return Resource.CLAY
    elif str == "sheep":
        return Resource.SHEEP
    elif str == "wheat":
        return Resource.WHEAT
    elif str == "iron":
        return Resource.IRON
    else:
        return Resource.DESSERT


def resource_log(hand):
    return {'wood': hand.resources[Resource.WOOD],
            'clay': hand.resources[Resource.CLAY],
            'sheep': hand.resources[Resource.SHEEP],
            'wheat': hand.resources[Resource.WHEAT],
            'iron': hand.resources[Resource.IRON]}


def next_turn(players, round, turn) -> (int, int):
    if turn == players - 1:
        turn = 0
        round += 1
        return round, turn
    else:
        turn += 1
        return round, turn


# how many crossroads are in a line
def init_cr_line_len():
    line_len = []
    num_of_crossroads = 3
    step = 1
    for i in range(12):
        line_len += [num_of_crossroads]
        if i % 2 == 0:
            num_of_crossroads += step
        if i == 5:
            step = -1
    return line_len


cr_line_len = init_cr_line_len()
