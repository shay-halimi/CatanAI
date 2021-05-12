from Board import Road
from Board import Crossroad
from Board import Terrain
from Board import Board
from Hand import Hand
from Log import Log
from Log import StatisticsLogger
from Resources import SETTLEMENT_PRICE
from Resources import ROAD_PRICE
from Resources import CITY_PRICE
from Resources import DEV_PRICE
from API import API
from Auxilary import r2s
from Resources import Resource
from DevStack import KnightCard
from DevStack import Monopole
from DevStack import YearOfProsper
from DevStack import VictoryPointCard
from DevStack import RoadBuilding
from DevStack import DevStack
from abc import ABC
import math
from random import randrange
from random import uniform
from Printer import Printer

api: API


class Action(ABC):
    def __init__(self, hand: Hand, heuristic_method):
        self.evaluation_state = False
        self.hand = hand
        self.board = hand.board  # type: Board
        self.hands = self.board.hands  # type: list[Hand]
        self.index = hand.index
        self.points = self.hand.points  # how many points the player has before the action get executed
        self.heuristic_method = heuristic_method
        # self.heuristic = hand.heuristic if self.heuristic_method is None else self.heuristic_method(self)
        self.name = 'action'
        self.heuristic = uniform(0, 1) if heuristic_method is None else heuristic_method(self)
        self.log = self.hand.board.log  # type: Log
        self.statistics_logger = self.hand.board.statistics_logger  # type: StatisticsLogger

    def evaluation_on(self):
        self.evaluation_state = True

    def evaluation_off(self):
        self.evaluation_state = False

    # do action return necessary information for undo
    def do_action(self):
        if not self.evaluation_state:
            Printer.printer('index : ' + str(self.index) + ' | action : ' + self.name)
        return None

    def log_action(self):
        # ToDo: build statistic based on the name of the player (on Dork, Guru, or NNPlayer)
        history_log = {'name': self.name, 'player': self.hand.index}
        self.log.action(history_log)

    def tmp_do(self):
        pass

    def undo(self, info):
        pass

    def shared_aftermath(self):
        if not self.evaluation_state:
            api.print_action(self.name)
            api.print_resources(self.hand.index, self.hand.resources)
            api.save_file()
            api.delete_action()
            self.log_action()
            essentials, regulars = self.create_keys()
            self.statistics_logger.save_action(self.hand.index, essentials, regulars)
            if self.hand.points > self.points:
                self.statistics_logger.got_point(self.hand.index)

    def create_keys(self):
        essentials = [self.name, 'points : ' + str(self.points), 'player : ' + str(self.hand.name)]
        return essentials, []


class DoNothing(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = 'do nothing'

    # ToDo: check correctness
    def do_action(self):
        pass

    def create_keys(self):
        keys = super().create_keys()
        # ToDo: DoNothing should get next best action heuristic score in __init__ as key
        return keys


class UseDevCard(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = 'use development card'


class UseKnight(UseDevCard):
    def __init__(self, hand, heuristic_method, terrain, dst):
        self.terrain = terrain
        self.dst = dst
        super().__init__(hand, heuristic_method)
        self.name = 'use knight'

    def do_action(self):
        terrain = self.hand.board.bandit_location
        super().do_action()
        resource = self.use_knight()
        self.shared_aftermath()
        return terrain, self.dst, self.hand.index, resource

    # terrain = where to put the bandit
    # dst = from who to steal
    def use_knight(self):
        hand = self.hand
        terrain = self.terrain
        for knight in hand.cards["knight"]:
            if knight.is_valid():
                terrain.put_bandit()
                hand.cards["knight"].remove(knight)
                steal = self.steal()
                return steal

    # todo test it
    def undo(self, undo_info):
        terrain, destination, source, resource = undo_info  # type: (Terrain, int, int, Resource)
        terrain.put_bandit()
        self.hands[destination].add_resources(resource, 1)
        self.hands[source].subtract_resources(resource, 1)
        card = KnightCard()
        card.ok_to_use = True
        self.hand.add_card(card)

    def steal(self):
        dst = self.hand.board.hands[self.dst]
        resources = dst.get_resources_number()
        if resources == 0:
            return None
        index = randrange(resources) + 1
        for resource in dst.resources.keys():
            if dst.resources[resource] >= index:
                self.hand.resources[resource] += 1
                dst.resources[resource] -= 1
                return resource
            else:
                index -= dst.resources[resource]

    def create_keys(self):
        essentials, regulars = super(UseKnight, self).create_keys()
        n_i, p_i = self.hand.board.bandit_location.bandit_value(self.hand.index)
        n_f, p_f = self.terrain.bandit_value(self.hand.index)
        regulars += ['unlock my production : ' + str(n_i - n_f), 'lock there production : ' + str(p_f - p_i)]
        return essentials, regulars


class UseMonopole(UseDevCard):
    def __init__(self, player, heuristic_method, resource):
        assert resource != Resource.DESSERT
        self.resource = resource
        super().__init__(player, heuristic_method)
        self.name = 'use monopole'

    def do_action(self):
        super().do_action()
        amounts = self.use_monopole()
        # ToDo : give a more meaningful type
        self.shared_aftermath()
        return amounts, self.resource

    def undo(self, info):
        amounts, resource = info
        for hand in self.hands:
            hand.add_resources(resource, amounts[hand.index])
            self.hand.subtract_resources(resource, amounts[hand.index])
        card = Monopole()
        card.ok_to_use = True
        self.hand.add_card(card)

    def use_monopole(self):
        amounts = []
        for index, card in enumerate(self.hand.cards["monopole"]):
            if card.is_valid():
                self.hand.cards["monopole"].pop(index)
                for hand in self.hand.board.hands:
                    if hand.index != self.hand.index:
                        amount = hand.resources[self.resource]
                        amounts += [amount]
                        self.hand.resources[self.resource] += amount
                        hand.resources[self.resource] = 0
                    else:
                        amounts += [0]
        return amounts

    def create_keys(self):
        essentials, regulars = super().create_keys()
        take = 0
        for hand in self.hand.board.hands:
            if hand != self.hand:
                take += hand.resources[self.resource]
        regulars += ['cards i get : ' + str(take)]
        return essentials, regulars


class UseYearOfPlenty(UseDevCard):
    def __init__(self, hand, heuristic_method, resource1, resource2):
        self.resource1 = resource1
        self.resource2 = resource2
        super().__init__(hand, heuristic_method)
        self.name = 'use year of plenty'

    def do_action(self):
        super().do_action()
        self.use_year_of_plenty()
        self.shared_aftermath()
        return self.resource1, self.resource2, self.hand.index

    def undo(self, info):
        r1, r2, index = info
        hand = self.hands[index]
        hand.add_resources(r1, 1)
        hand.add_resources(r2, 1)
        card = YearOfProsper()
        card.ok_to_use = True
        self.hand.add_card(card)

    def use_year_of_plenty(self):
        for card in self.hand.cards["year of prosper"]:
            if card.is_valid():
                self.hand.add_resources(self.resource1, 1)
                self.hand.add_resources(self.resource2, 1)
                self.hand.cards["year of prosper"].remove(card)


class UseBuildRoads(UseDevCard):
    def __init__(self, hand, heuristic_method, road1: Road, road2: Road):
        self.road1 = road1
        self.road2 = road2
        super().__init__(hand, heuristic_method)
        self.name = 'use build roads'

    def do_action(self):
        super().do_action()
        info = self.build_2_roads()
        self.shared_aftermath()
        return info

    def undo(self, info):
        r1, r1i, r2, r2i = info  # type: Road, tuple, Road, tuple
        r1.undo_build(r1i)
        r2.undo_build(r2i)
        card = RoadBuilding()
        card.ok_to_use = True
        self.hand.add_card(card)

    def build_2_roads(self):
        hand = self.hand  # type: Hand
        road1 = self.road1  # type: Road
        road2 = self.road2  # type: Road
        cards = hand.cards["road builder"]
        for index, card in enumerate(cards):
            if card.ok_to_use:
                self.hand.cards["road builder"].pop(index)
                info1 = road1.build(hand.index)
                info2 = road2.build(hand.index)
                return [road1, info1, road2, info2]


class UseVictoryPoint(UseDevCard):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = "use victory_point"

    def do_action(self):
        super().do_action()
        self.use_victory_point()
        self.shared_aftermath()
        return self.index

    def undo(self, info):
        card = VictoryPointCard()
        card.ok_to_use = True
        self.hand.add_card(card)
        self.hand.subtract_point()

    def use_victory_point(self):
        hand = self.hand
        hand.points += 1
        hand.cards['victory points'].pop()
        hand.heuristic -= 1.05
        if hand.points >= 10:
            hand.heuristic += math.inf


class BuildSettlement(Action):
    def __init__(self, hand, heuristic_method, crossroad: Crossroad):
        self.crossroad = crossroad
        super().__init__(hand, heuristic_method)
        self.name = 'build settlement'

    def do_action(self):
        super().do_action()
        undo_info = self.buy_settlement()
        self.action_aftermath()
        return undo_info

    def undo(self, info):
        build_info = info
        self.crossroad.undo_build(self.index, build_info)
        self.hand.receive(SETTLEMENT_PRICE)
        self.hand.subtract_point()
        self.hand.settlements_log.pop()

    def action_aftermath(self):
        if not self.evaluation_state:
            i, j = self.crossroad.location
            api.print_action(self.name)
            api.print_settlement(self.hand.index, i, j)
            api.point_on_crossroad(i, j)
        self.shared_aftermath()

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
        # old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        # old_production = hand.production
        hand.pay(SETTLEMENT_PRICE)
        undo_info = self.create_settlement()
        # prioritize having a variety of resource produce
        # ToDo: heuristic should not be affected by the action but by the argument heuristic_function
        # self.heuristic += len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        # for resource in hand.production:
        #    self.heuristic += (hand.production[resource] - old_production[resource]) * hand.parameters.resource_value[
        #        resource]
        hand.settlements_log += [self.crossroad]
        return undo_info

    def create_settlement(self):
        hand = self.hand
        self.crossroad.connected[hand.index] = True
        hand.settlement_pieces -= 1
        hand.add_point()
        undo_info = self.crossroad.build(hand)
        hand.set_distances()
        if self.crossroad.port is not None:
            hand.ports.add(self.crossroad.port)
        return undo_info

    def create_keys(self):
        essentials, regulars = super().create_keys()
        regulars += ['all production : ' + str(self.crossroad.val['sum'])]
        for resource in Resource:
            if resource != Resource.DESSERT:
                regulars += [r2s(resource) + ' : ' + str(self.crossroad.val[resource])]
        return essentials, regulars


class BuildFirstSettlement(BuildSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build first settlement'

    def do_action(self):
        build_info = self.create_settlement()
        self.hand.settlements_log += [self.crossroad]
        self.action_aftermath()
        return build_info

    def undo(self, info):
        build_info = info
        self.crossroad.undo_build(self.index, build_info)
        self.hand.subtract_point()
        self.hand.settlements_log.pop()

    def is_legal(self):
        return True


class BuildSecondSettlement(BuildFirstSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build second settlement'

    def do_action(self):
        build_info = self.create_settlement()
        self.crossroad.produce(self.index)
        self.hand.settlements_log += [self.crossroad]
        self.action_aftermath()
        return build_info

    def undo(self, info):
        build_info = info
        self.crossroad.undo_produce(self.index)
        self.crossroad.undo_build(self.index, build_info)
        self.hand.subtract_point()
        self.hand.settlements_log.pop()


class BuildCity(Action):
    def __init__(self, hand, heuristic_method, crossroad: Crossroad):
        self.crossroad = crossroad
        super().__init__(hand, heuristic_method)
        self.name = 'build city'

    def do_action(self):
        build_info = self.buy_city()
        self.action_aftermath()
        return build_info

    def undo(self, info):
        build_info = info
        self.crossroad.undo_build(self.index, build_info)
        self.hand.receive(CITY_PRICE)
        self.hand.subtract_point()
        self.hand.cities.pop()

    def action_aftermath(self):
        if not self.evaluation_state:
            i, j = self.crossroad.location
            api.print_action(self.name)
            api.print_city(self.hand.index, i, j)
            api.point_on_crossroad(i, j)
        self.shared_aftermath()

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
        # ToDo: heuristic should not be affected from action but from the argument heuristic_function
        # old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        # old_production = hand.production
        hand.pay(CITY_PRICE)
        build_info = self.create_city()
        # self.heuristic += len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        # for resource in hand.production:
        #    self.heuristic += (hand.production[resource] - old_production[resource]) * hand.parameters.resource_value[
        #        resource]
        hand.cities += [self.crossroad]
        return build_info

    def create_city(self):
        hand = self.hand
        hand.settlement_pieces += 1
        hand.city_pieces -= 1
        hand.add_point()
        build_info = self.crossroad.build(hand)
        hand.set_distances()
        return build_info

    def create_keys(self):
        essentials, regulars = super().create_keys()
        regulars += ['all production : ' + str(self.crossroad.val['sum'])]
        for resource in Resource:
            if resource != Resource.DESSERT:
                regulars += [r2s(resource) + ' : ' + str(self.crossroad.val[resource])]
        return essentials, regulars


class BuildRoad(Action):
    def __init__(self, hand, heuristic_method, road: Road):
        self.road = road
        super().__init__(hand, heuristic_method)
        self.name = 'build road'

    def do_action(self):
        super().do_action()
        info = self.buy_road()
        self.action_aftermath()
        return info

    def action_aftermath(self):
        if not self.evaluation_state:
            api.print_action(self.name)
            api.write_a_note(str(self.check_longest_road()))
            i0, j0 = self.road.neighbors[0].location
            i1, j1 = self.road.neighbors[1].location
            api.print_road(self.hand.index, i0, j0, i1, j1)
            api.point_on_road(i0, j0, i1, j1)
        self.shared_aftermath()

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
        info = self.create_road()
        return info

    # ---- undo an action ---- #

    def undo(self, info):
        self.hand.receive(ROAD_PRICE)
        self.road.undo_build(info)

    def create_road(self):
        self.hand.road_pieces -= 1
        info = self.road.build(self.hand.index)
        self.hand.set_distances()
        return info

    def travel_left(self, cr: Crossroad, roads, right):
        end = True
        longest_road = roads
        for n in cr.neighbors:
            if n.road.owner == self.hand.index and n.road.traveled is not True:
                end = False
                n.road.traveled = True
                current_road = self.travel_left(n.crossroad, roads + 1, right)
                n.road.traveled = False
                if longest_road < current_road:
                    longest_road = current_road
        if end:
            return roads + self.travel_right(right, 0) + 1
        else:
            return longest_road

    def travel_right(self, cr: Crossroad, roads):
        longest_right_road = roads
        for n in cr.neighbors:
            if n.road.owner == self.hand.index and n.road.traveled is not True:
                n.road.traveled = True
                right_road = self.travel_right(n.crossroad, roads + 1)
                n.road.traveled = False
                if longest_right_road < right_road:
                    longest_right_road = right_road
        return longest_right_road

    def check_longest_road(self):
        left, right = self.road.neighbors  # type: Crossroad
        self.road.traveled = True
        longest_road = self.travel_left(left, 0, right)
        self.road.traveled = False
        return longest_road


class BuildFreeRoad(BuildRoad):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method, road)
        self.name = 'build free road'

    def do_action(self):
        info = self.create_road()
        self.action_aftermath()
        return info

    def undo(self, info):
        self.road.undo_build(info)

    def is_legal(self):
        return True


class Trade(Action):
    def __init__(self, hand, heuristic_method, src, exchange_rate, dst, take):
        self.exchange_rate = exchange_rate
        self.src = src
        self.dst = dst
        self.take = take
        self.give = take * exchange_rate
        super().__init__(hand, heuristic_method)
        self.name = 'trade'

    def do_action(self):
        super().do_action()
        self.trade()
        if not self.evaluation_state:
            api.trade(self.hand.board.players, self.hand.index, self.src, self.dst, self.give, self.take)
        self.shared_aftermath()
        return self.src, self.give, self.dst, self.take

    def undo(self, info):
        source, give, destination, take = info
        hand = self.hand
        hand.add_resources(source, give)
        hand.subtract_resources(destination, take)

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

    def trade(self):
        self.hand.subtract_resources(self.src, self.give)
        self.hand.add_resources(self.dst, self.take)

    def create_keys(self):
        essentials, regulars = super().create_keys()
        regulars += ['exchange rate : ' + str(self.exchange_rate)]
        return essentials, regulars


class BuyDevCard(Action):
    def __init__(self, hand, heuristic_method):
        self.stack = hand.board.devStack  # type: DevStack
        super().__init__(hand, heuristic_method)
        self.name = 'buy devCard'

    def do_action(self):
        super().do_action()
        self.buy_development_card()
        return None

    def undo(self, info):
        hand = self.hand
        hand.receive(DEV_PRICE)
        hand.unknown_dev_cards -= 1

    def buy_development_card(self):
        hand = self.hand
        hand.pay(DEV_PRICE)
        if self.evaluation_state:
            hand.unknown_dev_cards += 1
        else:
            stack = self.stack
            card = stack.get()
            hand.cards[card.name] += [card]


class ThrowCards(Action):
    def __init__(self, hand: Hand, heuristic, cards):
        self.cards = cards
        super().__init__(hand, heuristic)
        self.name = "throw cards"

    def do_action(self):
        for resource in self.cards:
            self.hand.resources[resource] -= self.cards[resource]
        return None

    def undo(self, info):
        for resource in self.cards:
            self.hand.add_resources(resource, 1)
