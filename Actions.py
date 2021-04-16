from Board import SETTLEMENT_PRICE
from Board import ROAD_PRICE
from Board import CITY_PRICE
from Auxilary import r2s
from Resources import Resource
from abc import ABC
from random import uniform
import math


class Action(ABC):
    def __init__(self, player, heuristic_method):
        self.player = player
        self.heuristic_method = heuristic_method
        self.heuristic = uniform(0, 1) if self.heuristic_method is None else self.heuristic_method(self)
        self.log = self.player.log
        self.name = 'action'

    def do_action(self):
        self.player.hand.print_resources()
        print("player : " + self.player.name + " " + self.name)
        self.log_action()

    def compute_heuristic(self):
        pass

    def log_action(self):
        return {'name': self.name, 'player': self.player.index}


class DoNothing(Action):
    def __init__(self, player, heuristic_method):
        super().__init__(player, heuristic_method)
        self.name = 'do nothing'

    def do_action(self):
        pass

    def compute_heuristic(self):
        return self.player.hand.heuristic


class UseKnight(Action):
    def __init__(self, player, heuristic_method, terrain, dst):
        super().__init__(player, heuristic_method)
        self.terrain = terrain
        self.dst = dst
        self.name = 'use knight'

    def do_action(self):
        super().do_action()
        self.player.hand.use_knight(self.terrain, self.dst)

    def compute_heuristic(self):
        resource = self.player.hand.use_knight(self.terrain, self.dst)
        new_heuristic = self.player.hand.heuristic
        self.player.hand.undo_use_knight(resource, self.terrain, self.dst)
        return new_heuristic


class UseMonopole(Action):
    def __init__(self, player, heuristic_method, resource):
        super().__init__(player, heuristic_method)
        self.resource = resource
        self.name = 'use monopole'

    def do_action(self):
        super().do_action()
        self.player.hand.use_monopole(self.resource)

    def compute_heuristic(self):
        selected_resource_quantity = 0
        for hand in self.player.board.hands:
            selected_resource_quantity += hand.resources[self.resource]
        return self.player.hand.heuristic + (
                self.player.hand.resource_value[self.resource] * selected_resource_quantity)


class UseYearOfPlenty(Action):
    def __init__(self, player, heuristic_method, resource1, resource2):
        super().__init__(player, heuristic_method)
        self.resource1 = resource1
        self.resource2 = resource2
        self.name = 'use year of plenty'

    def do_action(self):
        super().do_action()
        self.player.hand.use_year_of_plenty(self.resource1, self.resource2)

    def compute_heuristic(self):
        player = self.player
        return player.hand.resource_value[self.resource1] + player.hand.resource_value[self.resource1]


class UseBuildRoads(Action):
    def __init__(self, player, heuristic_method, road1, road2):
        super().__init__(player, heuristic_method)
        self.road1 = road1
        self.road2 = road2
        self.name = 'use build roads'

    def do_action(self):
        super().do_action()
        self.player.hand.build_2_roads(self.road1, self.road2)

    def compute_heuristic(self):
        heuristic_increment = 0
        player = self.player
        old_road_length = player.longest_road_value
        if player.board.longest_road_owner != player.index:
            player.tmp_buy_road(self.road1)
            player.tmp_buy_road(self.road2)
            heuristic_increment += (player.board.longest_road_owner == player.index) * 5
        else:
            player.hand.tmp_buy_road(self.road1)
            self.player.hand.tmp_buy_road(self.road2)
        heuristic_increment += player.longest_road_value - old_road_length
        player.hand.undo_buy_road(self.road2)
        player.hand.undo_buy_road(self.road1)
        return heuristic_increment + player.hand.heuristic


class UseVictoryPoint(Action):
    def __init__(self, player, heuristic_method):
        super().__init__(player, heuristic_method)
        self.name = "use victory_point"

    def do_action(self):
        super().do_action()
        self.player.hand.use_victory_point()

    def compute_heuristic(self):
        player = self.player
        if len(list(filter(lambda x: x.ok_to_use, player.hand.cards["victory points"]))) + player.hand.points >= 10:
            return math.inf
        else:
            return -math.inf


class BuildSettlement(Action):
    def __init__(self, player, heuristic_method, crossroad):
        self.crossroad = crossroad
        super().__init__(player, heuristic_method)
        self.name = 'build settlement'

    def do_action(self):
        super().do_action()
        self.player.hand.buy_settlement(self.crossroad)

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.player.index,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.player.hand.can_pay(SETTLEMENT_PRICE)


class BuildFirstSettlement(BuildSettlement):
    def __init__(self, player, heuristic_method, crossroad):
        super().__init__(player, heuristic_method, crossroad)
        self.name = 'build first settlement'

    def do_action(self):
        self.player.hand.create_settlement(self.crossroad)
        self.log_action()

    def is_legal(self):
        return True


class BuildSecondSettlement(BuildSettlement):
    def __init__(self, player, heuristic_method, crossroad):
        super().__init__(player, heuristic_method, crossroad)
        self.name = 'build second settlement'

    def do_action(self):
        self.player.hand.create_settlement(self.crossroad)
        self.crossroad.produce(self.player.index)
        self.log_action()

    def is_legal(self):
        return True


class BuildCity(Action):
    def __init__(self, player, heuristic_method, crossroad):
        super().__init__(player, heuristic_method)
        self.crossroad = crossroad
        self.name = 'build city'

    def do_action(self):
        self.player.hand.print_resources()
        print("player : " + self.player.name + " supposed to be city here : " + self.name)
        self.player.hand.buy_city(self.crossroad)
        self.log_action()

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.player.index,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.player.hand.can_pay(CITY_PRICE)


class BuildRoad(Action):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method)
        self.road = road
        self.name = 'build road'

    def do_action(self):
        super().do_action()
        self.player.hand.buy_road(self)

    # todo
    def compute_heuristic(self):
        return 0.2

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.player.index,
            'location': self.road.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        if self.player.hand.can_pay(ROAD_PRICE):
            return True
        else:
            return False


class BuildFreeRoad(BuildRoad):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method, road)
        self.name = 'build free road'

    def do_action(self):
        self.player.hand.create_road(self.road)
        self.log_action()

    def is_legal(self):
        return True


class Trade(Action):
    def __init__(self, player, heuristic_method, src, exchange_rate, dst, take):
        super().__init__(player, heuristic_method)
        self.src = src
        self.dst = dst
        self.take = take
        self.give = take * exchange_rate
        self.name = 'trade'

    def do_action(self):
        super().do_action()
        self.player.hand.trade(self)

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.player.index,
            'source': r2s(self.src),
            'destination': r2s(self.dst),
            'take': self.take,
            'give': self.give
        }
        self.log.action(log)

    def is_legal(self):
        return self.player.hand.can_pay({self.src: self.give})


class BuyDevCard(Action):
    def __init__(self, player, heuristic_method):
        super().__init__(player, heuristic_method)
        self.name = 'buy devCard'

    def do_action(self):
        super().do_action()
        self.player.hand.buy_development_card(self.player.board.devStack)

    def compute_heuristic(self):
        player = self.player
        return player.hand.heuristic + player.hand.dev_card_value
