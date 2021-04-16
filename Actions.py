from Board import Road
from Hand import Hand
from Log import Log
from Resources import SETTLEMENT_PRICE
from Resources import ROAD_PRICE
from Resources import CITY_PRICE
from Auxilary import r2s
from Resources import Resource
from abc import ABC
from random import uniform
import math


class Action(ABC):
    def __init__(self, hand, heuristic_method):
        self.hand = hand  # type: Hand
        self.heuristic_method = heuristic_method
        self.heuristic = uniform(0, 1) if self.heuristic_method is None else self.heuristic_method(self)
        self.log = self.hand.board.log  # type: Log
        self.name = 'action'

    def do_action(self):
        self.hand.print_resources()
        print("player : " + self.name + " " + self.name)
        self.log_action()

    def compute_heuristic(self):
        pass

    def log_action(self):
        return {'name': self.name, 'player': self.hand.index}


class DoNothing(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = 'do nothing'

    def do_action(self):
        pass

    def compute_heuristic(self):
        return self.hand.heuristic


class UseKnight(Action):
    def __init__(self, hand, heuristic_method, terrain, dst):
        super().__init__(hand, heuristic_method)
        self.terrain = terrain
        self.dst = dst
        self.name = 'use knight'

    def do_action(self):
        super().do_action()
        self.hand.use_knight(self.terrain, self.dst)

    def compute_heuristic(self):
        resource = self.hand.use_knight(self.terrain, self.dst)
        new_heuristic = self.hand.heuristic
        self.hand.undo_use_knight(resource, self.terrain, self.dst)
        return new_heuristic


class UseMonopole(Action):
    def __init__(self, player, heuristic_method, resource):
        super().__init__(player, heuristic_method)
        self.resource = resource
        self.name = 'use monopole'

    def do_action(self):
        super().do_action()
        self.hand.use_monopole(self.resource)

    def compute_heuristic(self):
        selected_resource_quantity = 0
        for hand in self.hand.board.hands:
            selected_resource_quantity += hand.resources[self.resource]
        return self.hand.heuristic + (
                self.hand.resource_value[self.resource] * selected_resource_quantity)


class UseYearOfPlenty(Action):
    def __init__(self, hand, heuristic_method, resource1, resource2):
        super().__init__(hand, heuristic_method)
        self.resource1 = resource1
        self.resource2 = resource2
        self.name = 'use year of plenty'

    def do_action(self):
        super().do_action()
        self.hand.use_year_of_plenty(self.resource1, self.resource2)

    def compute_heuristic(self):
        return self.hand.resource_value[self.resource1] + self.hand.resource_value[self.resource1]


class UseBuildRoads(Action):
    def __init__(self, hand, heuristic_method, road1, road2):
        super().__init__(hand, heuristic_method)
        self.road1 = road1
        self.road2 = road2
        self.name = 'use build roads'

    def do_action(self):
        super().do_action()
        self.hand.build_2_roads(self.road1, self.road2)

    def compute_heuristic(self):
        heuristic_increment = 0
        old_road_length = self.hand.longest_road_value
        if self.hand.board.longest_road_owner != self.hand.index:
            self.hand.tmp_buy_road(self.road1)
            self.hand.tmp_buy_road(self.road2)
            heuristic_increment += (self.hand.board.longest_road_owner == self.hand.index) * 5
        else:
            self.hand.tmp_buy_road(self.road1)
            self.hand.tmp_buy_road(self.road2)
        heuristic_increment += self.hand.longest_road_value - old_road_length
        self.hand.undo_buy_road(self.road2)
        self.hand.undo_buy_road(self.road1)
        return heuristic_increment + self.hand.heuristic


class UseVictoryPoint(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = "use victory_point"

    def do_action(self):
        super().do_action()
        self.hand.use_victory_point()

    def compute_heuristic(self):
        if len(list(filter(lambda x: x.ok_to_use, self.hand.cards["victory points"]))) + self.hand.points >= 10:
            return math.inf
        else:
            return -math.inf


class BuildSettlement(Action):
    def __init__(self, hand, heuristic_method, crossroad):
        self.crossroad = crossroad
        super().__init__(hand, heuristic_method)
        self.name = 'build settlement'

    def do_action(self):
        super().do_action()
        self.hand.buy_settlement(self.crossroad)

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.hand.can_pay(SETTLEMENT_PRICE)


class BuildFirstSettlement(BuildSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build first settlement'

    def do_action(self):
        self.hand.create_settlement(self.crossroad)
        self.log_action()

    def is_legal(self):
        return True


class BuildSecondSettlement(BuildSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build second settlement'

    def do_action(self):
        self.hand.create_settlement(self.crossroad)
        self.crossroad.produce(self.hand.index)
        self.log_action()

    def is_legal(self):
        return True


class BuildCity(Action):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method)
        self.crossroad = crossroad
        self.name = 'build city'

    def do_action(self):
        self.hand.print_resources()
        print("player : " + self.name + " supposed to be city here : " + self.name)
        self.hand.buy_city(self.crossroad)
        self.log_action()

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.hand.can_pay(CITY_PRICE)


class BuildRoad(Action):
    def __init__(self, hand, heuristic_method, road):
        super().__init__(hand, heuristic_method)
        self.road = road
        self.name = 'build road'

    def do_action(self):
        super().do_action()
        buy_road(self)

    # todo
    def compute_heuristic(self):
        return 0.2

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'location': self.road.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        if self.hand.can_pay(ROAD_PRICE):
            return True
        else:
            return False


class BuildFreeRoad(BuildRoad):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method, road)
        self.name = 'build free road'

    def do_action(self):
        self.hand.create_road(self.road)
        self.log_action()

    def is_legal(self):
        return True


class Trade(Action):
    def __init__(self, hand, heuristic_method, src, exchange_rate, dst, take):
        super().__init__(hand, heuristic_method)
        self.src = src
        self.dst = dst
        self.take = take
        self.give = take * exchange_rate
        self.name = 'trade'

    def do_action(self):
        super().do_action()
        self.hand.trade(self)

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'source': r2s(self.src),
            'destination': r2s(self.dst),
            'take': self.take,
            'give': self.give
        }
        self.log.action(log)

    def is_legal(self):
        return self.hand.can_pay({self.src: self.give})


class BuyDevCard(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = 'buy devCard'

    def do_action(self):
        super().do_action()
        self.hand.buy_development_card(self.hand.board.devStack)

    def compute_heuristic(self):
        return self.hand.heuristic + self.hand.dev_card_value


def buy_road(action: BuildRoad):
    hand = action.hand
    hand.pay(ROAD_PRICE)
    create_road(action.hand, action.road)

    was_longest_road = hand.index == hand.board.longest_road_owner
    former_longest_road_owner = hand.board.longest_road_owner
    if former_longest_road_owner is None:
        hand.heuristic += int(hand.board.longest_road_owner == hand.index)
        return
    hand.heuristic += hand.index == (hand.board.longest_road_owner ^ was_longest_road) * hand.longest_road_value
    return


def create_road(hand: Hand, road: Road):
    hand.road_pieces -= 1
    road.build(hand.index)
    hand.set_distances()


def buy_settlement(self, cr: Crossroad):
    old_production_variety = len(list(filter(lambda x: x.value != 0, self.production)))
    old_production = self.production
    self.pay(SETTLEMENT_PRICE)
    self.create_settlement(cr)
    # prioritize having a variety of resource produce
    self.heuristic += len(list(filter(lambda x: x.value != 0, self.production))) - old_production_variety
    for resource in self.production:
        self.heuristic += (self.production[resource] - old_production[resource]) * self.resource_value[resource]

    self.update_resource_values()
    self.settlements_log += [cr]


def buy_city(self, cr: Crossroad):
    old_production_variety = len(list(filter(lambda x: x.value != 0, self.production)))
    old_production = self.production
    self.pay(CITY_PRICE)
    self.create_city(cr)
    self.heuristic += len(list(filter(lambda x: x.value != 0, self.production))) - old_production_variety
    for resource in self.production:
        self.heuristic += (self.production[resource] - old_production[resource]) * self.resource_value[resource]

    self.update_resource_values()
    self.cities += [cr]


def buy_development_card(self, stack: DevStack):
    self.resources[Resource.IRON] -= 1
    self.resources[Resource.WHEAT] -= 1
    self.resources[Resource.SHEEP] -= 1
    print(self.cards)
    print(stack.get().name)
    card = stack.get()
    self.cards[card.name] += [card]
