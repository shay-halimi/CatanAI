from Resources import Resource
from Resources import ROAD_PRICE
from Resources import SETTLEMENT_PRICE
from Resources import CITY_PRICE
from Resources import DEV_PRICE
from DevStack import DevCard
import math


class Parameters:
    def __init__(self):
        self.longest_road_value = 5
        self.biggest_army_value = 4.5
        self.road_value = 0.2
        self.resource_value = {Resource.CLAY: 1, Resource.WOOD: 1, Resource.SHEEP: 1, Resource.WHEAT: 1,
                               Resource.IRON: 1}
        self.dev_card_value = 0.5


ROAD_PIECES = 15
SETTLEMENT_PIECES = 5
CITY_PIECES = 4


class Hand:
    def __init__(self, index, board):
        self.index = index
        self.name = None
        self.points = 0
        # ---- hand ---- #
        self.resources = {Resource.WOOD: 0, Resource.IRON: 0, Resource.WHEAT: 0, Resource.SHEEP: 0, Resource.CLAY: 0}
        self.cards = {"knight": [], "victory points": [], "monopole": [], "road builder": [],
                      "year of prosper": []}  # type: dict[str: list[DevCard]]
        self.road_pieces = ROAD_PIECES
        self.settlement_pieces = SETTLEMENT_PIECES
        self.city_pieces = CITY_PIECES
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
        self.unknown_dev_cards = 0
        # ---- these are values that we can manipulate according to success ---- #
        self.parameters = Parameters()

    # ---- get information ---- #

    def get_roads_amount(self):
        return ROAD_PIECES - self.road_pieces

    def get_settlements_amount(self):
        return SETTLEMENT_PIECES - self.settlement_pieces

    def get_cities_amount(self):
        return CITY_PIECES - self.city_pieces

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
        return self.can_pay(DEV_PRICE) and self.board.devStack and self.board.devStack.has_cards()

    def can_trade(self, src: Resource, amount):
        if src in self.ports:
            return self.resources[src] >= amount * 2, 2
        if Resource.DESSERT in self.ports:
            return self.resources[src] >= amount * 3, 3
        return self.resources[src] >= amount * 4, 4

    # ---- auxiliary functions ---- #

    def __str__(self):
        paragraph = '----------------------------\n'
        paragraph += 'hand : \n'
        paragraph += 'index : ' + str(self.index) + '\n'
        paragraph += 'name : ' + str(self.name) + '\n'
        paragraph += 'points : ' + str(self.points) + '\n'
        paragraph += 'roads : ' + str(self.get_roads_amount()) + '\n'
        paragraph += 'settlements : ' + str(self.get_settlements_amount()) + '\n'
        paragraph += 'cities : ' + str(self.get_cities_amount()) + '\n'
        paragraph += 'production : ' + str(self.production_all) + '\n'
        paragraph += 'wood : ' + str(self.resources[Resource.WOOD]) + '\n'
        paragraph += 'clay : ' + str(self.resources[Resource.CLAY]) + '\n'
        paragraph += 'wheat : ' + str(self.resources[Resource.WHEAT]) + '\n'
        paragraph += 'sheep : ' + str(self.resources[Resource.SHEEP]) + '\n'
        paragraph += 'iron : ' + str(self.resources[Resource.IRON]) + '\n'
        paragraph += 'victory points : ' + str(len(self.cards['victory points'])) + '\n'
        paragraph += 'knight : ' + str(len(self.cards['knight'])) + '\n'
        paragraph += 'monopole : ' + str(len(self.cards['monopole'])) + '\n'
        paragraph += 'road builder : ' + str(len(self.cards['road builder'])) + '\n'
        paragraph += 'year of prosper : ' + str(len(self.cards['year of prosper'])) + '\n'
        paragraph += 'longest road : ' + str(self.longest_road) + '\n'
        paragraph += 'heuristic : ' + str(self.heuristic) + '\n'
        return paragraph

    def add_resources(self, resource: Resource, amount):
        if resource is not None:
            self.resources[resource] += amount

    def subtract_resources(self, resource: Resource, amount):
        if resource is not None:
            self.resources[resource] -= amount

    def add_card(self, card: DevCard):
        name = card.get_name()
        self.cards[name] += [card]

    def add_point(self):
        self.points += 1

    def subtract_point(self):
        self.points -= 1

    def set_distances(self):
        stack = []
        stack_fertility = []
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
        while stack_fertility:
            cr = stack_fertility.pop()
            for n in cr.neighbors:
                ncr = n.crossroad
                if cr.fertility_dist > ncr.fertility_dist + 1:
                    cr.fertility_dist = ncr.fertility_dist + 1
                    stack_fertility.extend(x.crossroad for x in cr.neighbors if x.crossroad not in stack)

    def can_pay(self, price):
        for resource in price:
            if self.resources[resource] < price[resource]:
                return False
        return True

    def pay(self, price):
        for resource in price:
            self.resources[resource] -= price[resource]

    def receive(self, price):
        for resource in price:
            self.resources[resource] += price[resource]
