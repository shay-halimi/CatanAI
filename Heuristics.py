from Actions import Action
from Board import Board
from Board import Terrain
from Log import StatisticsLogger
from Resources import Resource
from Auxilary import r2s
from typing import List
from Hand import Hand, ROAD_PRICE, SETTLEMENT_PRICE, CITY_PRICE, DEV_PRICE
from Actions import ThrowCards, BuildRoad
from Printer import Printer
from time import perf_counter

import math


class SimpleHeuristic:
    def __init__(self, id, board: Board):
        self.id = id
        self.board = board
        self.hand = board.hands[id]

    def need_resource(self, resource, amount, trade):
        do_trade = 0
        if self.hand.resources[resource] < amount:
            if trade.dst is resource:
                do_trade += 1
        if trade.src is resource:
            if self.hand.resources[resource] and self.hand.resources[resource] - trade.give < amount:
                do_trade -= 1
        return do_trade

    def accept_trade(self, trade):
        do_trade = 0
        if self.hand.settlement_pieces:
            do_trade += self.need_resource(Resource.WOOD, 1, trade)
            do_trade += self.need_resource(Resource.CLAY, 1, trade)
            if self.hand.get_lands():
                do_trade += self.need_resource(Resource.SHEEP, 1, trade)
                do_trade += self.need_resource(Resource.WHEAT, 1, trade)
        elif self.hand.city_pieces:
            do_trade += self.need_resource(Resource.WHEAT, 2, trade)
            do_trade += self.need_resource(Resource.IRON, 3, trade)
        return do_trade > 0

    def terrain_production_value(self, terrain: Terrain):
        pass


class StatisticsHeuristic:
    def __init__(self, statistic_logger: StatisticsLogger):
        self.st_logger = statistic_logger

    def get_statistic(self, action: Action):
        essentials, regulars = action.create_keys()
        ratio = self.st_logger.get_statistic(essentials, regulars)  # type: float
        return ratio

    def actions_to_point(self, action: Action):
        essentials, regulars = action.create_keys()
        actions = self.st_logger.get_actions_to_point(essentials, regulars)
        return 1 / actions + self.get_statistic(action)


def best_action(actions: List[Action]):
    ba = actions.pop() if actions else None
    while actions:
        a = actions.pop()
        if a.heuristic > ba.heuristic:
            ba = a
    return ba


def greatest_crossroad(crossroads):
    max_cr = {"cr": None, "sum": 0}
    for cr in crossroads:
        if cr.val["sum"] > max_cr["sum"]:
            max_cr["sum"] = cr.val["sum"]
            max_cr["cr"] = cr
    return max_cr["cr"]


def show_score_analysis(hand: Hand):
    Printer.printer('points : ' + str(hand.points))
    for resource in Resource:
        if resource != Resource.DESSERT:
            Printer.printer(r2s(resource) + ' : ' + str(hand.resources[resource]))
    for v in hand.cards.values():
        if v:
            Printer.printer(v[0].name + ' : ' + str(len(v)))
    if hand.index != hand.board.longest_road_owner:
        road_value = 2 - 0.3 * (hand.board.longest_road_size + 1 - hand.longest_road)
        if road_value > 0:
            Printer.printer('road value : ' + str(road_value))
    if hand.index != hand.board.largest_army_owner:
        army_value = 2 - 0.5 * (hand.board.largest_army_size - hand.largest_army)
        if army_value > 0:
            Printer.printer('armay value : ' + str(army_value))


def able_to_buy_score(resources: dict, price, value):
    score = 0
    before = resources.copy()
    while True:
        now = before.copy()
        for resource in price:
            if now[resource] >= price[resource]:
                now[resource] -= price[resource]
            else:
                return score, before
        score += value
        before = now.copy()


def hand_stat(hand: Hand):
    stat = hand.points
    for resource in Resource:
        if resource != Resource.DESSERT:
            stat += hand.resources[resource] * 0.12
    for v in hand.cards.values():
        stat += len(v) * 0.4
        stat += hand.unknown_dev_cards * 0.4
    if hand.index != hand.board.longest_road_owner:
        road_value = 2 - 0.3 * (hand.board.longest_road_size + 1 - hand.longest_road)
        if road_value > 0:
            stat += road_value
    if hand.index != hand.board.largest_army_owner:
        army_value = 2 - 0.5 * (hand.board.largest_army_size - hand.largest_army)
        if army_value > 0:
            stat += army_value
    score, resources = able_to_buy_score(hand.resources, SETTLEMENT_PRICE, 0.48)
    stat += score
    score, resources = able_to_buy_score(resources, CITY_PRICE, 0.3)
    stat += score
    score, resources = able_to_buy_score(resources, ROAD_PRICE, 0.36)
    stat += score
    score, resources = able_to_buy_score(resources, DEV_PRICE, 0.34)
    stat += score
    return stat


def hand_heuristic(action: Action):
    name = action.name
    tic = perf_counter()
    action.evaluation_on()
    undo_info = action.do_action()
    value = hand_stat(action.hand)
    action.undo(undo_info)
    action.evaluation_off()
    toc = perf_counter()
    time = toc - tic
    action.add_computation_time(time)
    return value


# ---- snow's heuristic ---- #


# this function given an action sends the action to its appropriate function that compute it function incrementally
def compute_heuristic_basic(action):
    if type(action).__name__ == "DoNothing":
        return compute_heuristic_do_nothing(action)
    if type(action).__name__ == "UseKnight":
        return compute_heuristic_use_knight(action)
    if type(action).__name__ == "UseMonopole":
        return compute_heuristic_use_monopole(action)
    if type(action).__name__ == "UseYearOfPlenty":
        return compute_heuristic_use_year_of_plenty(action)
    if type(action).__name__ == "UseBuildRoads":
        return compute_heuristic_use_build_roads(action)
    if type(action).__name__ == "UseVictoryPoint":
        return compute_heuristic_use_victory_point(action)
    if type(action).__name__ == "BuildSettlement":
        return compute_heuristic_build_settlement(action)
    if type(action).__name__ == "BuildFirstSettlement":
        return compute_heuristic_build_first_settlement(action)
    if type(action).__name__ == "BuildSecondSettlement":
        return compute_heuristic_build_second_settlement(action)
    if type(action).__name__ == "BuildCity":
        return compute_heuristic_build_city(action)
    if type(action).__name__ == "BuildRoad":
        return compute_heuristic_build_road(action)
    if type(action).__name__ == "BuildFreeRoad":
        return compute_heuristic_build_free_road(action)
    if type(action).__name__ == "Trade":
        return compute_heuristic_trade(action)
    if type(action).__name__ == "BuyDevCard":
        return compute_heuristic_buy_dev_card()
    if type(action).__name__ == "ThrowCards":
        return compute_heuristic_throw_cards(action)
    assert False  # we don't want to reach this point


def compute_heuristic_throw_cards(action):
    heuristic_increment = 0
    for card in ThrowCards.get_cards(action.cards):
        heuristic_increment -= action.hand.parameters.get_resource_value[card]


def compute_heuristic_buy_dev_card(action):
    return action.hand.heuristic + action.hand.parameters.dev_card_value


def compute_heuristic_trade(action):
    return action.hand.heuristic


# TO-DO we can compute here a much more complicated heuristic based on distance from other players distance from other city
# and reasources in the way that the road is pointing
def compute_heuristic_build_free_road(action):
    return action.hand.heuristic


def compute_heuristic_build_road(action):
    hand = action.hand
    hand.pay(ROAD_PRICE)
    action.create_road()
    return


def compute_heuristic_build_city(action):
    hand = action.hand
    old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
    old_production = hand.production
    legals = action.crossroad.tmp_build(action.hand.index)
    heuristic_increment = len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
    for resource in hand.production:
        heuristic_increment += (hand.production[resource] - old_production[resource]) * \
                               hand.parameters.resource_value[resource]
    action.crossroad.unbuild(action.hand.index, legals)
    return heuristic_increment


# todo
def compute_heuristic_build_first_settlement(action):
    pass


def compute_heuristic_build_second_settlement(action):
    pass


def compute_heuristic_build_settlement(action):
    hand = action.hand
    old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
    old_production = hand.production
    legals = action.crossroad.tmp_build(action.hand.index)
    heuristic_increment = len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
    for resource in hand.production:
        heuristic_increment += (hand.production[resource] - old_production[resource]) * \
                               hand.parameters.resource_value[resource]
    action.crossroad.unbuild(action.hand.index, legals)
    return heuristic_increment


def compute_heuristic_do_nothing(action):
    return action.hand.heuristic


def compute_heuristic_use_knight(action):
    action.hand
    # resource = action.use_knight()
    # #TODO wrong, heuristic does not update on itself
    # new_heuristic = action.hand.heuristic
    # action.undo_use_knight(resource, action.terrain)
    # return new_heuristic


def compute_heuristic_use_monopole(action):
    selected_resource_quantity = 0
    for hand in action.hand.board.hands:
        selected_resource_quantity += hand.resources[action.resource]
    return action.hand.parameters.resource_value[action.resource] * selected_resource_quantity


def compute_heuristic_use_year_of_plenty(action):
    return action.hand.parameters.resource_value[action.resource1] + \
           action.hand.parameters.resource_value[action.resource2]


def compute_heuristic_use_build_roads(action):
    heuristic_increment = 0
    old_road_length = action.hand.parameters.longest_road_value
    build_road1 = BuildRoad(action.hand, action.heuristic_method, action.road1)
    build_road2 = BuildRoad(action.hand, action.heuristic_method, action.road2)
    build_road1.tmp_do()
    build_road2.tmp_do()
    if action.hand.board.longest_road_owner != action.hand.index:
        heuristic_increment += (action.hand.board.longest_road_owner == action.hand.index) * 5
    heuristic_increment += action.hand.parameters.longest_road_value - old_road_length
    hand_heuristic = action.hand.heuristic
    build_road1.undo()
    build_road2.undo()
    return heuristic_increment


# we could adjust here the heuristic values according to the size of values we want i.e in [0,1]
def compute_heuristic_use_victory_point(action):
    if len(action.hand.cards["victory points"]) + action.hand.points >= 10:
        return math.inf
    else:
        return -100
