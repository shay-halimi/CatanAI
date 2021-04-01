from Resources import Resource
from DevStack import DevStack
import random
import Dice
import API
import Log

# ---- global variables ---- #

DESSERT = 7


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

    def produce(self, hands):
        if not self.has_bandit:
            for cr in self.crossroads:
                if cr.ownership != 0 and self.resource is not Resource.DESSERT:
                    hands[cr.ownership - 1].resources[self.resource] += cr.building

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
        self.distance = [{}] * board.players
        # game
        self.ownership = None
        self.building = 0
        self.port = None

    def initial_distances(self, player):
        for line in self.board.crossroads:
            for cr in line:
                self.distance[player][cr] = 30

    def set_distances(self, player):
        self.initial_distances(player)
        stack = []
        self.distance[player][self] = 0
        for n in self.neighbors:
            cr = n.crossroad
            stack += [cr]
        while stack:
            cr = stack.pop()
            push_neighbors = False
            for n in cr.neighbors:
                if n.my_road(player):
                    self.distance[player][cr] = 0
                    push_neighbors = True
                    break
                if n.can_go() and self.distance[player][cr] > self.distance[player][n.crossroad] + 1:
                    self.distance[player][cr] = self.distance[player][n.crossroad] + 1
                    push_neighbors = True
            if push_neighbors and (cr.ownership is None or cr.ownership == player):
                for n in cr.neighbors:
                    stack += [n.crossroad]

    def aux_build(self, player):
        if self.ownership is None:
            self.ownership = player
            for n in self.neighbors:
                n.crossroad.legal = False
        if self.ownership == player and self.building < 2:
            self.building += 1
            API.print_crossroad(self)
            return True
        return False

    def build(self, player):
        if self.legal and self.connected[player]:
            return self.aux_build(player)

    def build_first(self, player):
        if self.legal:
            return self.aux_build(player)

    def build_second(self, player, hands):
        if self.legal:
            rtn = self.aux_build(player)
            for t in self.terrains:
                if t.resource != Resource.DESSERT:
                    hands[player].resources[t.resource] += 1
            return rtn

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
            self.board.longest_road_size = player.longest_road
            self.board.longest_road_owner = player

    def is_connected(self, player):
        if self.neighbors[0].connected[player] or self.neighbors[1].connected[player]:
            return True
        return False

    def is_legal(self, player):
        if self.owner is None and (self.is_connected(player)):
            return True
        return False

    def build(self, player):
        if self.is_legal(player):
            self.owner = player
            self.neighbors[0].connected[player] = True
            self.neighbors[1].connected[player] = True
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

        # add crossroad api location to each crossroad
        API.set_crossroads_locations(self.crossroads)

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

    def add_neighbor_cr(self, cr, i, j):
        if 0 <= i < 12 and 0 <= j < cr_line_len[i]:
            cr.neighbors += [Neighbor(self.crossroads[i][j])]

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

    def get_legal_crossroads_start(self, player):
        legal = []
        for line in self.crossroads:
            for cr in line:
                if cr.legal and cr.ownership is None:
                    legal += [cr]
        return legal

    def get_legal_crossroads(self, player):
        legal = []
        for line in self.crossroads:
            for cr in line:
                if cr.legal and cr.connected[player] and (cr.ownership is None or cr.ownership == player):
                    legal += [cr]
        return legal

    def get_legal_roads(self, player):
        legal = []
        for line in self.roads:
            for road in line:
                if road.is_legal(player):
                    legal += [road]

    def next_turn(self, turn, rnd):
        API.next_turn(self, turn, rnd, self.hands)
        Log.next_turn(rnd, turn, self.hands)
        Log.save_game()


class Hand:
    def __init__(self, index, board):
        self.resources = {Resource.WOOD: 0, Resource.IRON: 0, Resource.WHEAT: 0, Resource.SHEEP: 0, Resource.CLAY: 0}
        self.cards = {"knight": [], "victory points": [], "monopole": [], "road builder": [], "year of prosper": []}
        self.longest_road, self.largest_army = 0, 0
        self.points = 0
        self.board = board
        self.index = index
        self.name = None

    def get_resources_number(self):
        sum = 0
        for r in self.resources.values():
            sum += r
        return sum

    def get_cards_number(self):
        sum = 0
        for c in self.cards:
            sum += len(c)
        return sum

    def can_buy_road(self):
        return self.resources[Resource.WOOD] >= 1 and self.resources[Resource.CLAY] >= 1

    def buy_road(self, road):
        if self.can_buy_road() and road.is_legal():
            self.resources[Resource.WOOD] -= 1
            self.resources[Resource.CLAY] -= 1
            road.build(self.index)
            return True
        return False

    def build_2_roads(self, road1, road2):
        for card in self.cards["road building"]:
            if card.is_valid():
                if road1.is_legal() and road2.is_legal():
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
                return True
        return False

    def can_buy_settlement(self):
        return self.resources[Resource.WOOD] >= 1 and self.resources[Resource.CLAY] >= 1 and self.resources[
            Resource.WHEAT] >= 1 and self.resources[Resource.SHEEP] >= 1

    def buy_settlement(self, cr: Crossroad):
        if self.can_buy_settlement() and cr.legal and cr.connected[self.index]:
            self.resources[Resource.WOOD] -= 1
            self.resources[Resource.CLAY] -= 1
            self.resources[Resource.WHEAT] -= 1
            self.resources[Resource.SHEEP] -= 1
            cr.build(self.index)
            return True
        return False

    def can_buy_city(self):
        return self.resources[Resource.WHEAT] >= 2 and self.resources[Resource.IRON] >= 3

    def buy_city(self, cr: Crossroad):
        if self.can_buy_city() and cr.ownership == self.index and cr.building == 1:
            self.resources[Resource.WHEAT] -= 2
            self.resources[Resource.IRON] -= 3

    def can_buy_development_card(self):
        return self.resources[Resource.SHEEP] >= 1 and self.resources[Resource.IRON] >= 1 and self.resources[
            Resource.WHEAT] >= 1

    def buy_development_card(self, stack: DevStack):
        if self.can_buy_development_card() and stack.has_cards():
            self.resources[Resource.IRON] -= 1
            self.resources[Resource.WHEAT] -= 1
            self.resources[Resource.SHEEP] -= 1
            self.cards[stack.get().get_name()] += 1
            return True
        return False

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

    def use_knight(self, terrain: Terrain, dst):
        for knight in self.cards["knight"]:
            if knight.is_valid():
                if terrain.put_bandit():
                    self.cards["knight"].remove(knight)
                    return self.steal(dst)
        return False


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
