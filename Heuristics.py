from Actions import Action
from Board import Board
from Board import Terrain
from Log import StatisticsLogger
from Resources import Resource
from Auxilary import r2s
import json
from typing import List
from random import uniform
from Hand import Hand
from Hand import SETTLEMENT_PRICE
from Hand import CITY_PRICE
from Hand import DEV_PRICE
from Hand import ROAD_PRICE


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
        ratio = self.st_logger.get_statistic(essentials, regulars) # type: float
        return ratio

    def actions_to_point(self, action: Action):
        essentials, regulars = action.create_keys()
        actions = self.st_logger.get_actions_to_point(essentials, regulars)
        return 1/ actions + self.get_statistic(action)


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
    print('points : ' + str(hand.points))
    for resource in Resource:
        if resource != Resource.DESSERT:
            print(r2s(resource) + ' : ' + str(hand.resources[resource]))
    for v in hand.cards.values():
        if v:
            print(v[0].name + ' : ' + str(len(v)))
    if hand.index != hand.board.longest_road_owner:
        road_value = 2 - 0.3 * (hand.board.longest_road_size + 1 - hand.longest_road)
        if road_value > 0:
            print('road value : ' + str(road_value))
    if hand.index != hand.board.largest_army_owner:
        army_value = 2 - 0.5 * (hand.board.largest_army_size - hand.largest_army)
        if army_value > 0:
            print('armay value : ' + str(army_value))


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
    action.evaluation_on()
    undo_info = action.do_action()
    value = hand_stat(action.hand)
    action.undo(undo_info)
    action.evaluation_off()
    return value
