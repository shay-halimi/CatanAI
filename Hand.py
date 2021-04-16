from Board import Crossroad
from Board import Terrain
from Board import Road
from DevStack import DevStack
from Resources import Resource
from Resources import ROAD_PRICE
from Resources import SETTLEMENT_PRICE
from Resources import CITY_PRICE
from Resources import DEV_PRICE
from Auxilary import r2s
import math
import random


class Hand:
    def __init__(self, index, board):
        self.index = index
        self.name = None
        self.points = 0
        # ---- hand ---- #
        self.resources = {Resource.WOOD: 0, Resource.IRON: 0, Resource.WHEAT: 0, Resource.SHEEP: 0, Resource.CLAY: 0}
        self.cards = {"knight": [], "victory points": [], "monopole": [], "road builder": [], "year of prosper": []}
        self.road_pieces = 15
        self.settlement_pieces = 5
        self.city_pieces = 4
        # ---- board --- #
        self.board = board
        self.ports = set()
        self.lands_log = []
        self.settlements_log = []
        self.cities = []
        # ---- achievements and stats ---- #
        self.longest_road, self.largest_army = 0, 0
        self.heuristic = 0
        self.production = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.WHEAT: 0, Resource.IRON: 0,
                           Resource.SHEEP: 0}
        self.production_all = 0
        # ---- these are values that we can manipulate according to success ---- #
        self.longest_road_value = 5
        self.biggest_army_value = 4.5
        self.road_value = 0.2
        self.resource_value = {Resource.CLAY: 1, Resource.WOOD: 1, Resource.WHEAT: 1, Resource.IRON: 1,
                               Resource.SHEEP: 1}
        self.dev_card_value = 0.5

    # ---- get information ---- #

    def compute_2_roads_heuristic(self, road1, road2):
        heuristic_increment = 0
        old_road_length = self.longest_road_value
        if self.board.longest_road_owner != self.index:
            self.tmp_buy_road(road1)
            self.tmp_buy_road(road2)
            heuristic_increment += (self.board.longest_road_owner == self.index) * 5
        else:
            self.tmp_buy_road(road1)
            self.tmp_buy_road(road2)
        heuristic_increment += (self.longest_road_value - old_road_length) * self.road_value
        self.undo_buy_road(road2)
        self.undo_buy_road(road1)
        return heuristic_increment

    def get_resources_number(self):
        resource_sum = 0
        for r in self.resources.values():
            resource_sum += r
        return resource_sum

    def get_cards_number(self):
        resource_sum = 0
        for c in self.cards:
            resource_sum += len(c)
        return resource_sum

    def get_lands(self):
        lands = []
        for line in self.board.crossroads:
            for cr in line:
                if cr.connected[self.index] and cr.building == 0 and cr.legal:
                    lands += [cr]
        return lands

    # check if an action can be taken ---- #

    def can_buy_road(self):
        return self.can_pay(ROAD_PRICE) and self.road_pieces

    def can_buy_settlement(self):
        return self.can_pay(SETTLEMENT_PRICE) and self.settlement_pieces

    def can_buy_city(self):
        return self.can_pay(CITY_PRICE) and self.city_pieces

    def can_buy_development_card(self):
        return self.can_pay(DEV_PRICE) and self.board.devStack

    def can_trade(self, src: Resource, amount):
        if src in self.ports:
            return self.resources[src] >= amount * 2, 2
        if Resource.DESSERT in self.ports:
            return self.resources[src] >= amount * 3, 3
        return self.resources[src] >= amount * 4, 4

    # ---- take an action ---- #

    # ---- ---- buy ---- ---- #

    def buy_road(self, build_road):
        self.pay(ROAD_PRICE)
        self.create_road(build_road.road)

        was_longest_road = self.index == self.board.longest_road_owner
        former_longest_road_owner = self.board.longest_road_owner
        if former_longest_road_owner is None:
            self.heuristic += int(self.board.longest_road_owner == self.index)
            return
        self.heuristic += self.index == (self.board.longest_road_owner ^ was_longest_road) * self.longest_road_value
        return

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

    # ---- ---- trade ---- ---- #

    def trade(self, trade):
        self.resources[trade.src] -= trade.give
        self.resources[trade.dst] += trade.take

    # ---- ---- use a development card ---- ---- #

    def build_2_roads(self, road1, road2):
        for card in self.cards["road building"]:
            if card.is_valid():
                if road1.is_legal() and road2.is_legal():
                    self.heuristic += self.compute_2_roads_heuristic(road1, road2)
                    road1.build(self.index)
                    road2.build(self.index)
                    self.cards["road building"].remove(card)
                    return True
        return False

    def use_year_of_plenty(self, resource1, resource2):
        for card in self.cards["year of plenty"]:
            if card.is_valid():
                if resource1 != Resource.DESSERT and resource2 != Resource.DESSERT:
                    self.resources[resource1] += 1
                    self.resources[resource2] += 1
                    self.cards["year of plenty"].remove(card)
                    return True
        return False

    def use_monopole(self, resource):
        for card in self.cards["monopole"]:
            if card.is_valid():
                if resource != Resource.DESSERT:
                    for hand in self.board.players:
                        if hand.index != self.index:
                            self.resources[resource] += hand.resources[resource]
                            hand.resources[resource] = 0
                    return True
        return False

    def use_victory_point(self):
        for card in self.cards["victory point"]:
            if card.is_valid():
                self.points += 1
                self.heuristic -= 100
                if self.points >= 10:
                    self.heuristic += math.inf
                return True

        return False

    # terrain = where to put the bandit
    # dst = from who to steal
    def use_knight(self, terrain: Terrain, dst):
        for knight in self.cards["knight"]:
            if knight.is_valid():
                if terrain.put_bandit():
                    self.cards["knight"].remove(knight)
                    return self.steal(dst)
        return False

    # todo test it
    def undo_use_knight(self, resource: Resource, terrain: Terrain, dst):
        assert terrain is not None
        terrain.put_bandit()
        if resource is not None:
            self.resources[resource] -= 1
            dst.resources[resource] += 1

    # ---- take a temporary action ---- #

    def tmp_buy_road(self, road):
        if self.can_buy_road() and road.is_legal():
            self.resources[Resource.WOOD] -= 1
            self.resources[Resource.CLAY] -= 1
            road.temp_build(self.index)
            return True
        return False

    # ---- undo an action ---- #

    def undo_buy_road(self, road):
        self.resources[Resource.WOOD] += 1
        self.resources[Resource.CLAY] += 1
        road.undo_build(self.index)

    # ---- auxiliary functions ---- #

    def steal(self, dst):
        if dst.resources_num == 0:
            return False
        index = random.randrange(len(dst.resources_num))
        for resource in dst.resources.keys():
            if dst[resource] >= index:
                self.resources[resource] += 1
                dst[resource] -= 1
                return resource
            else:
                index -= dst[resource]
        return True

    def set_distances(self):
        stack = []
        stack_fert = []
        for line in self.board.crossroads:
            for cr in line:
                cr.fertility_dist = math.inf
                if cr.ownership is not None:
                    cr.distance[cr.ownership] = 0
                    stack.extend(x.crossroad for x in cr.neighbors if x.crossroad not in stack)
                else:
                    if cr.legal:
                        cr.fertility_dist = 0
        while stack:
            cr = stack.pop()
            for n in cr.neighbors:
                ncr = n.crossroad
                for i in range(self.board.players):
                    if cr.distance[i] > ncr.distance[i] + 1:
                        cr.distance[i] = ncr.distance[i] + 1
                        stack.extend(x.crossroad for x in cr.neighbors if x.crossroad not in stack)
        while stack_fert:
            cr = stack_fert.pop()
            for n in cr.neighbors:
                ncr = n.crossroad
                if cr.fertility_dist > ncr.fertility_dist + 1:
                    cr.fertility_dist = ncr.fertility_dist + 1
                    stack_fert.extend(x.crossroad for x in cr.neighbors if x.crossroad not in stack)

    def create_settlement(self, cr: Crossroad):
        cr.connected[self.index] = True
        self.settlement_pieces -= 1
        self.points += 1
        for resource in Resource:
            if resource is not Resource.DESSERT:
                self.production_all += cr.val[resource] / 36
        cr.build(self.index)
        self.set_distances()
        if cr.port is not None:
            self.ports.add(cr.port)

    def create_city(self, cr: Crossroad):
        self.settlement_pieces += 1
        self.city_pieces -= 1
        self.points += 1
        cr.build(self.index)
        self.set_distances()

    def can_pay(self, price):
        for resource in price:
            if self.resources[resource] < price[resource]:
                return False
        return True

    def pay(self, price):
        for resource in price:
            self.resources[resource] -= price[resource]

    # ---- test functions ---- #

    def print_resources(self):
        print("resources of player : " + self.name)
        for resource in self.resources:
            print(r2s(resource) + " : " + str(self.resources[resource]) + "|||", end="")
        print()

    def update_resource_values(self):
        pass

    class Heuristic:
        def __init__(self):
            self.production = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.WHEAT: 0, Resource.IRON: 0,
                               Resource.SHEEP: 0}
            self.production_all = 0
            self.resource_value = {Resource.CLAY: 1, Resource.WOOD: 1, Resource.WHEAT: 1, Resource.IRON: 1,
                                   Resource.SHEEP: 1}
            self.value = 0
            self.resources_gained = 0
