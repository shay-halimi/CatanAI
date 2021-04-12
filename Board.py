from Resources import Resource
from DevStack import DevStack
import random
import Dice
import API
import Log
import math
from Auxilary import r2s

# ---- global variables ---- #

DESSERT = 7
INFINITY = 100
ROAD_PRICE = {Resource.WOOD: 1, Resource.CLAY: 1}
SETTLEMENT_PRICE = {Resource.WOOD: 1, Resource.CLAY: 1, Resource.WHEAT: 1, Resource.SHEEP: 1}
CITY_PRICE = {Resource.WHEAT: 2, Resource.IRON: 3}
DEV_PRICE = {Resource.SHEEP: 1, Resource.WHEAT: 1, Resource.IRON: 1}


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


# ---- classes ---- #


class Terrain:
    def __init__(self, num):
        self.resource = None
        self.num = num
        self.crossroads = []
        self.has_bandit = False
        self.board = None

    def __str__(self):
        return "(" + str(self.num) + "," + str(self.resource) + ")"

    def set_resource(self, resource):
        self.resource = resource

    def produce(self):
        if not self.has_bandit:
            for cr in self.crossroads:
                if cr.ownership is not None and self.resource is not Resource.DESSERT:
                    self.board.hands[cr.ownership - 1].resources[self.resource] += cr.building

    def can_put_bandit(self):
        return not self.has_bandit

    def put_bandit(self):
        if self.can_put_bandit():
            self.board.bandit_location.has_bandit = False
            self.has_bandit = True
            steal_stack = []
            for cr in self.crossroads:
                if cr.ownership is not None:
                    steal_stack += [cr.ownership]
            return steal_stack


class Crossroad:
    def __init__(self, board):
        # logistic
        self.location = None
        self.api_location = None
        self.board = board
        self.terrains = []
        self.neighbors = []
        # rules
        self.connected = [False] * self.board.players
        self.legal = True
        # heuristic
        self.val = {"sum": 0, Resource.WOOD: 0, Resource.CLAY: 0, Resource.WHEAT: 0, Resource.SHEEP: 0,
                    Resource.IRON: 0}
        self.longest_road = [0] * self.board.players
        self.distance = [INFINITY, INFINITY, INFINITY, INFINITY]
        self.fertility_dist = 0
        # game
        self.ownership = None
        self.building = 0
        self.port = None

    def build(self, player):
        if self.ownership is None:
            self.ownership = player
            for n in self.neighbors:
                n.crossroad.legal = False
        if self.ownership == player and self.building < 2:
            self.building += 1
            self.fertility_dist = INFINITY
            API.print_crossroad(self)

    def produce(self, player):
        for t in self.terrains:
            if t.resource != Resource.DESSERT:
                self.board.hands[player].resources[t.resource] += 1

    # link the crossroad with its neighbor edges
    def add_neighbor(self, road, crossroad):
        self.neighbors += [Neighbor(crossroad, road)]

    def trade_specific(self, num, r_type):
        hand = self.board.hands[self.ownership]
        if hand.resources[self.port] >= 2 * num:
            hand.resources[r_type] += num
            hand.resources[self.port] -= 2 * num
            return True
        return False

    def trade_general(self, num, r_type):
        hand = self.board.hands[self.ownership]
        if hand.resources[r_type["give"]] >= 3 * num:
            hand.resources[r_type["take"]] += num
            hand.resources[r_type["give"]] -= 3 * num
            return True
        return False

    def trade(self, num, r_type):
        if self.port is None:
            return False
        elif self.port is Resource.DESSERT:
            return self.trade_general(num, r_type)
        else:
            return self.trade_specific(num, r_type)

    def set_heuristic_value(self):
        for t in self.terrains:
            if t.resource != Resource.DESSERT:
                heu_val = 6 - abs(7 - t.num)
                self.val["sum"] += heu_val
                self.val[t.resource] += heu_val

    @staticmethod
    def greatest_crossroad(crossroads):
        max_cr = {"cr": None, "sum": 0}
        for cr in crossroads:
            if cr.val["sum"] > max_cr["sum"]:
                max_cr["sum"] = cr.val["sum"]
                max_cr["cr"] = cr
        return max_cr["cr"]


class Road:
    def __init__(self, board, owner=None):
        self.owner = owner
        self.api_location = [0, 0, 0, 0]
        self.neighbors = []
        self.board = board
        self.temp_build_info = {}

    def upgrade_longest_road(self, player):
        i = player
        v = self.neighbors[0].longest_road
        u = self.neighbors[1].longest_road
        temp = v[i]
        if v[i] == 0:
            temp = u[i] + 1
        if u[i] == 0:
            u[i] = v[i] + 1
        v[i] = temp
        if v[i] > self.board.hands[i].longest_road:
            self.board.hands[i].longest_road = v[i]
        if u[i] > self.board.hands[i].longest_road:
            self.board.hands[i].longest_road = u[i]
        if self.board.hands[i].longest_road > self.board.longest_road_size:
            self.board.longest_road_size = self.board.hands[i].longest_road
            if self.board.longest_road_owner is not None:
                self.board.hands[self.board.longest_road_owner].points -= 2
            self.board.longest_road_owner = player
            self.board.hands[player].points += 2

    def is_connected(self, player):
        if self.neighbors[0].connected[player] or self.neighbors[1].connected[player]:
            return True
        return False

    def is_legal(self, player):
        if self.owner is None and (self.is_connected(player)):
            return True
        return False

    def temp_build(self, player):
        if self.is_legal(player):
            self.owner = player
            self.temp_build_info["connected0"] = self.neighbors[0].connected[player]
            self.temp_build_info["connected1"] = self.neighbors[1].connected[player]
            self.neighbors[0].connected[player] = True
            self.neighbors[1].connected[player] = True
            self.temp_build_info["longest_road_size"] = self.board.longest_road_size
            self.temp_build_info["longest road owner"] = self.board.longest_road_owner
            self.upgrade_longest_road(player)
            return True
        return False

    def undo_build(self):
        player = self.owner
        self.owner = None
        self.neighbors[0].connected[player] = self.temp_build_info["connected0"]
        self.neighbors[1].connected[player] = self.temp_build_info["connected1"]
        self.board.longest_road_size = self.temp_build_info["longest_road_size"]
        self.board.longest_road_owner = self.temp_build_info["longest road owner"]

    def build(self, player):
        if self.is_legal(player):
            self.owner = player
            for i in range(2):
                if not self.neighbors[i].connected[player]:
                    self.board.hands[player].lands_log += [self.neighbors[i]]
                    self.neighbors[i].connected[player] = True
            self.upgrade_longest_road(player)
            API.print_road(self)
            return True
        return False

    def get_location(self):
        return str(self.neighbors[0].location) + " " + str(self.neighbors[1].location)


class Neighbor:
    def __init__(self, cr: Crossroad, road: Road):
        self.crossroad = cr
        self.road = road

    def can_go(self, player):
        return self.road.owner is None or self.road.owner == player

    def my_road(self, player):
        return self.road.owner == player

    def get_owner(self):
        return self.crossroad.ownership





class Board:
    def __init__(self, players):
        self.players = players
        self.devStack = DevStack()
        self.dice = Dice.Dice()

        self.map = [[Terrain(10), Terrain(2), Terrain(9)],
                    [Terrain(12), Terrain(6), Terrain(4), Terrain(10)],
                    [Terrain(9), Terrain(11), Terrain(DESSERT), Terrain(3), Terrain(8)],
                    [Terrain(8), Terrain(3), Terrain(4), Terrain(5)],
                    [Terrain(5), Terrain(6), Terrain(11)]]

        # create 2d array of crossroads
        self.crossroads = []
        for i in range(12):
            line = []
            for j in range(cr_line_len[i]):
                cr = Crossroad(self)
                cr.location = (i, j)
                line.append(cr)
            self.crossroads.append(line)

        """
        # add crossroad neighbors to each crossroad
        for i, line in enumerate(self.crossroads):
            for j, cr in enumerate(line):
                if i % 2 == 0:
                    self.add_neighbor_cr(cr, i - 1, j)
                    self.add_neighbor_cr(cr, i + 1, j)
                    if i < 6:
                        self.add_neighbor_cr(cr, i + 1, j + 1)
                    else:
                        self.add_neighbor_cr(cr, i + 1, j - 1)
                else:
                    if i < 6:
                        self.add_neighbor_cr(cr, i - 1, j - 1)
                    else:
                        self.add_neighbor_cr(cr, i - 1, j + 1)
                    self.add_neighbor_cr(cr, i - 1, j)
                    self.add_neighbor_cr(cr, i + 1, j)
        """

        # build ports
        self.crossroads[0][0].port = Resource.WOOD
        self.crossroads[1][0].port = Resource.WOOD
        self.crossroads[0][1].port = Resource.DESSERT
        self.crossroads[1][2].port = Resource.DESSERT
        self.crossroads[2][3].port = Resource.DESSERT
        self.crossroads[3][4].port = Resource.DESSERT
        self.crossroads[3][0].port = Resource.SHEEP
        self.crossroads[4][0].port = Resource.SHEEP
        self.crossroads[5][5].port = Resource.DESSERT
        self.crossroads[6][5].port = Resource.DESSERT
        self.crossroads[7][0].port = Resource.WHEAT
        self.crossroads[8][0].port = Resource.WHEAT
        self.crossroads[8][4].port = Resource.IRON
        self.crossroads[9][3].port = Resource.IRON
        self.crossroads[10][0].port = Resource.CLAY
        self.crossroads[11][0].port = Resource.CLAY
        self.crossroads[10][2].port = Resource.DESSERT
        self.crossroads[11][1].port = Resource.DESSERT

        # shuffle the terrain on the board and link the crossroads to them
        resource_stack = [Resource.DESSERT] + [Resource.IRON] * 3 + [Resource.CLAY] * 3 + [Resource.WOOD] * 4 + [
            Resource.WHEAT] * 4 + [Resource.SHEEP] * 4
        i = 0
        for line in self.map:
            j = 0
            for terrain in line:
                terrain.board = self
                index = random.randrange(0, len(resource_stack))
                resource = resource_stack.pop(index)
                if resource == Resource.DESSERT:
                    self.map[2][2].num = terrain.num
                    terrain.num = 7
                    terrain.has_bandit = True
                    self.bandit_location = terrain
                self.dice.number_to_terrain[terrain.num].append((i, j))
                terrain.set_resource(resource)
                terrain.crossroads += [self.crossroads[2 * i][j]]
                terrain.crossroads += [self.crossroads[2 * i + 1][j]]
                terrain.crossroads += [self.crossroads[2 * i + 1][j + 1]]
                terrain.crossroads += [self.crossroads[2 * i + 2][j]]
                terrain.crossroads += [self.crossroads[2 * i + 2][j + 1]]
                terrain.crossroads += [self.crossroads[2 * i + 3][j]]
                j += 1
            i += 1

        # link the terrains to their crossroads
        for line in self.map:
            for t in line:
                for cr in t.crossroads:
                    cr.terrains += [t]

        # set the heuristic values of the crossroads
        for line in self.crossroads:
            for cr in line:
                cr.set_heuristic_value()

        # create the roads
        self.roads = []
        length = 3
        step = 1
        mid = 0
        for i in range(11):
            line = []
            if i % 2:
                for j in range(length + 1):
                    line.append(Road(self))
                length += step * (1 - mid)
            else:
                for j in range(2 * length):
                    line.append(Road(self))
                length += step * mid
            if i == 4:
                step = 0
            if i == 5:
                step = -1
                mid = 1
            self.roads.append(line)

        # link cross roads to roads
        self.add_neighbors_to_roads()

        # create hands
        self.hands = []
        for n in range(players):
            self.hands += [Hand(n, self)]

        # longest road stats
        self.longest_road_size = 4
        self.longest_road_owner = None

        # largest army stats
        self.largest_army_size = 2
        self.largest_army_owner = None

        # create the API
        API.start_api(self)

    def end_game(self, rnd, win_player):
        return Log.end_game(rnd, win_player, self.hands)

    def get_max_points(self):
        max_points = max(self.hands)
        return max_points

    # very convoluted function to link each road with its vertices crossroads and vice versa
    def add_neighbors_to_roads(self):
        i = 0
        xor = False
        for line in self.roads:
            up = 0
            down = 0
            if i == 5:
                xor = True
            for road in line:
                cr1 = self.crossroads[i][up]
                road.neighbors += [cr1]
                cr2 = self.crossroads[i + 1][down]
                road.neighbors += [cr2]
                cr1.add_neighbor(road, cr2)
                cr2.add_neighbor(road, cr1)
                if i % 2:
                    up += 1
                    down += 1
                else:
                    if (up == down) != xor:
                        down += 1
                    else:
                        up += 1
            i += 1

    def get_two_legal_roads(self, player):
        legal = []
        for line1 in self.roads:
            for road1 in line1:
                if road1.is_legal(player):
                    road1.temp_build(player)
                    for line2 in self.roads:
                        for road2 in line2:
                            if road2.is_legal(player):
                                legal += [(road1, road2)]
        return legal

    def next_turn(self, turn, rnd):
        API.next_turn(self, turn, rnd, self.hands)
        Log.next_turn(rnd, turn, self.hands)

    def end_game(self):
        Log.save_game(self.hands)


    def update_longest_road(self, player):
        former = self.longest_road_owner
        if former is not None:
            self.hands[former].points -= 2
        self.hands[player].points += 2
        self.longest_road_size += 1

    # ---- get legal moves ---- #

    def get_settlements(self, player):
        legal = []
        for line in self.crossroads:
            for cr in line:
                if cr.ownership is player and cr.building == 1:
                    legal += [cr]
        return legal

    def get_legal_crossroads_start(self):
        legal = []
        for line in self.crossroads:
            for cr in line:
                if cr.legal and cr.ownership is None:
                    legal += [cr]
        return legal

    def get_lands(self, player):
        return self.hands[player].get_lands()

    def get_legal_roads(self, player):
        legal = []
        for line in self.roads:
            for road in line:
                if road.is_legal(player):
                    legal += [road]
        return legal



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
        self.settlements = []
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
        heuristic_increment=0
        old_road_length=self.longest_road_value
        if  self.board.longest_road_owner != self.index:
            self.tmp_buy_road(road1)
            self.tmp_buy_road(road2)
            heuristic_increment += (self.board.longest_road_owner == self.index)*5
        else:
            self.tmp_buy_road(road1)
            self.tmp_buy_road(road2)
        heuristic_increment += (self.longest_road_value-old_road_length)*self.road_value
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

    def buy_road(self, road):
        was_longest_road = self.index == self.board.longest_road_owner
        former_longest_road_owner = self.board.longest_road_owner
        self.pay(ROAD_PRICE)
        self.create_road(road)
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
        self.settlements += [cr]

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
        if self.can_buy_development_card() and stack.has_cards():
            self.resources[Resource.IRON] -= 1
            self.resources[Resource.WHEAT] -= 1
            self.resources[Resource.SHEEP] -= 1
            print(self.cards)
            print(stack.get().name)
            card = stack.get()
            if card is None:
                # this is supposed to never happen in normal play time
                print("no card in the deck")
                assert False
                return False
            self.cards[card.name] += [card]
            return True
        return False

    # ---- ---- trade ---- ---- #

    def trade(self, trade):
        self.resources[trade.src] -= trade.give
        self.resources[trade.dst] += trade.take
        Log.add_trade(trade)

    # ---- ---- use a development card ---- ---- #

    def build_2_roads(self, road1, road2):
        for card in self.cards["road building"]:
            if card.is_valid():
                if road1.is_legal() and road2.is_legal():
                    self.heuristic += self.compute_2_roads_heuristic(road1,road2)
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
                    for hand in self.board.hands:
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
    def undo_use_knight(self,resource: Resource, terrain: Terrain,dst):
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
                cr.fertility_dist = INFINITY
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

    def create_road(self, road: Road):
        self.road_pieces -= 1
        road.build(self.index)
        self.set_distances()

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


# ---- test functions ---- #


def test_crossroads(crossroads):
    for line in crossroads:
        for cr in line:
            cr.ownership = random.randrange(0, 5)
            cr.building = random.randrange(1, 3)


def test_roads(roads):
    for line in roads:
        for road in line:
            road.owner = random.randrange(0, 5)


# ---- main ---- #


def main():
    print("Hello Board")
    # board = Board(3)
    # test_roads(board.roads)
    # test_crossroads(board.crossroads)
    # API.game_test(board)


main()
