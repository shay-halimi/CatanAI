from Board import Road
from Board import Crossroad
from Hand import Hand
from Log import Log
from Resources import SETTLEMENT_PRICE
from Resources import ROAD_PRICE
from Resources import CITY_PRICE
from Resources import DEV_PRICE
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
    def __init__(self, hand, heuristic_method, road1: Road, road2: Road):
        super().__init__(hand, heuristic_method)
        self.road1 = road1
        self.road2 = road2
        self.name = 'use build roads'

    def do_action(self):
        super().do_action()
        self.build_2_roads()

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

    def build_2_roads(self):
        hand = self.hand
        road1 = self.road1
        road2 = self.road2
        player = hand.index
        for card in hand.cards["road building"]:
            if card.is_valid():
                if road1.is_legal(player) and road2.is_legal(player):
                    self.heuristic += hand.compute_2_roads_heuristic(road1, road2)
                    road1.build(hand.index)
                    road2.build(hand.index)
                    hand.cards["road building"].remove(card)
                    return True
        return False


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
        self.buy_settlement()

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.hand.can_pay(SETTLEMENT_PRICE)

    def buy_settlement(self):
        hand = self.hand
        old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        old_production = hand.production
        hand.pay(SETTLEMENT_PRICE)
        self.create_settlement()
        # prioritize having a variety of resource produce
        hand.heuristic += len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        for resource in hand.production:
            hand.heuristic += (hand.production[resource] - old_production[resource]) * hand.resource_value[resource]

        hand.update_resource_values()
        hand.settlements_log += [self.crossroad]

    def create_settlement(self):
        hand = self.hand
        self.crossroad.connected[hand.index] = True
        hand.settlement_pieces -= 1
        hand.points += 1
        for resource in Resource:
            if resource is not Resource.DESSERT:
                hand.production_all += self.crossroad.val[resource] / 36
        self.crossroad.build(hand.index)
        hand.set_distances()
        if self.crossroad.port is not None:
            hand.ports.add(self.crossroad.port)


class BuildFirstSettlement(BuildSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build first settlement'

    def do_action(self):
        self.create_settlement()
        self.log_action()

    def is_legal(self):
        return True


class BuildSecondSettlement(BuildSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build second settlement'

    def do_action(self):
        self.create_settlement()
        self.crossroad.produce(self.hand.index)
        self.log_action()

    def is_legal(self):
        return True


class BuildCity(Action):
    def __init__(self, hand, heuristic_method, crossroad: Crossroad):
        super().__init__(hand, heuristic_method)
        self.crossroad = crossroad
        self.name = 'build city'

    def do_action(self):
        self.hand.print_resources()
        print("player : " + self.name + " supposed to be city here : " + self.name)
        self.buy_city()
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

    def buy_city(self):
        hand = self.hand
        old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        old_production = hand.production
        hand.pay(CITY_PRICE)
        self.create_city()
        self.heuristic += len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        for resource in hand.production:
            self.heuristic += (hand.production[resource] - old_production[resource]) * hand.resource_value[resource]

        hand.update_resource_values()
        hand.cities += [self.crossroad]

    def create_city(self):
        hand = self.hand
        hand.settlement_pieces += 1
        hand.city_pieces -= 1
        hand.points += 1
        self.crossroad.build(hand.index)
        hand.set_distances()


class BuildRoad(Action):
    def __init__(self, hand, heuristic_method, road):
        super().__init__(hand, heuristic_method)
        self.road = road
        self.name = 'build road'

    def do_action(self):
        super().do_action()
        self.buy_road()

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

    def buy_road(self):
        hand = self.hand
        hand.pay(ROAD_PRICE)
        self.create_road()

        was_longest_road = hand.index == hand.board.longest_road_owner
        former_longest_road_owner = hand.board.longest_road_owner
        if former_longest_road_owner is None:
            hand.heuristic += int(hand.board.longest_road_owner == hand.index)
            return
        hand.heuristic += hand.index == (hand.board.longest_road_owner ^ was_longest_road) * hand.longest_road_value
        return

    def create_road(self):
        self.hand.road_pieces -= 1
        self.road.build(self.hand.index)
        self.hand.set_distances()


class BuildFreeRoad(BuildRoad):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method, road)
        self.name = 'build free road'

    def do_action(self):
        self.create_road()
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
        self.buy_development_card()

    def compute_heuristic(self):
        return self.hand.heuristic + self.hand.dev_card_value

    def buy_development_card(self):
        hand = self.hand
        stack = self.hand.board.devStack
        hand.pay(DEV_PRICE)
        card = stack.get()
        hand.cards[card.name] += [card]
