from Actions import Action
from Board import Board
from Board import Terrain
from Resources import Resource
from Auxilary import r2s
import json
from random import uniform


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
    with open('statistics.json') as json_file:
        statistics = json.load(json_file)

    def settlement_value(self, build_settlement):
        book = self.statistics['settlement']['production']
        time = len(build_settlement.hand.settlements_log)
        production = build_settlement.crossroad.val['sum']
        key = str((time, production))
        if key in book:
            st = book[key]
        else:
            return uniform(0, 1)
        settlement_log = self.statistics['settlement']
        events = settlement_log['total events']
        wins = settlement_log['total wins']
        loses = events - wins
        statistic = Statistic(st['event'], st['win'], wins, loses)
        for resource in Resource:
            if resource is not Resource.DESSERT:
                book = self.statistics['settlement'][r2s(resource)]
                production = build_settlement.crossroad.val[resource]
                key = str((time, production))
                if key in book:
                    st = book[key]
                else:
                    return uniform(0, 1)
                statistic.merge(Statistic(st['event'], st['win'], wins, loses))
        return statistic.win_ratio


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


def best_action(actions: list[Action]):
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
