from Hand import Hand
from Resources import Resource
from DevStack import DevStack
import random
import Dice
from Log import StatisticsLogger
from Auxilary import r2s
from Auxilary import s2r
from Auxilary import cr_line_len

# ---- global variables ---- #

DESSERT = 7
INFINITY = 100


# ---- classes ---- #


class Terrain:
    def __init__(self, num):
        self.resource = None
        self.num = num
        self.crossroads = []
        self.has_bandit = False
        self.board = None
        self.location = None

    def get_crossroads(self):
        return self.crossroads

    def __str__(self):
        return "(" + str(self.num) + "," + str(self.resource) + ")"

    def set_resource(self, resource):
        self.resource = resource

    def produce(self):
        if not self.has_bandit and self.resource is not Resource.DESSERT:
            for cr in self.crossroads:
                if cr.ownership is not None:
                    self.board.hands[cr.ownership].resources[self.resource] += cr.building

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

    def get_log(self):
        log = {
            'resource': r2s(self.resource),
            'number': self.num
        }
        return log

    def bandit_value(self, index):
        negative_value = 0  # how much index player earn on the terrain
        positive_value = 0  # how much the rest of the players earn on the terrain
        for cr in self.crossroads:
            if cr.ownership == index:
                negative_value += cr.building * (6 - abs(7 - self.num))
            elif cr.ownership is not None:
                positive_value += cr.building * (6 - abs(7 - self.num))
        return negative_value, positive_value


class Crossroad:
    def __init__(self, board):
        # logistic
        self.location = None
        self.api_location = None
        self.board = board
        self.terrains = []  # type: list[Terrain]
        self.neighbors = []  # type: list[Neighbor]
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

    def get_ownership(self):
        return self.ownership

    def add_production(self, hand: Hand):
        for resource in Resource:
            if resource is not Resource.DESSERT:
                hand.production_all += self.val[resource] / 36
                hand.production[resource] += self.val[resource] / 36

    def build(self, hand: Hand):
        legals = []
        if self.ownership is None:
            self.ownership = hand.index
            for n in self.neighbors:
                legals += [n.crossroad.legal]
                n.crossroad.legal = False
        if self.ownership == hand.index and self.building < 2:
            self.building += 1
            self.fertility_dist = INFINITY
            self.add_production(hand)
        return legals

    def undo_build(self, player, legals):
        assert self.ownership == player
        if self.building == 1:
            self.ownership = None
            for n in range(len(self.neighbors)):
                self.neighbors[n].crossroad.legal = legals[n]
        self.building -= 1

    def produce(self, player):
        hand = self.board.hands[player]
        for t in self.terrains:
            if t.resource != Resource.DESSERT:
                hand.add_resources(t.resource, 1)

    def undo_produce(self, player):
        hand = self.board.hands[player]
        for t in self.terrains:
            if t.resource != Resource.DESSERT:
                hand.subtract_resources(t.resource, 1)

    # link the crossroad with its neighbor edges
    def add_neighbor(self, road, crossroad):
        self.neighbors += [Neighbor(crossroad, road)]

    def trade_specific(self, num, r_type):
        hand = self.board.players[self.ownership]
        if hand.resources[self.port] >= 2 * num:
            hand.resources[r_type] += num
            hand.resources[self.port] -= 2 * num
            return True
        return False

    def trade_general(self, num, r_type):
        hand = self.board.players[self.ownership]
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

    def statistic_log(self):
        log = {
            "owner": self.ownership,
            "points": 0,
            "time": len(self.board.players[self.ownership].settlement_log),
            "production": self.val['sum'],
            "wheat": self.val[Resource.WHEAT],
            "sheep": self.val[Resource.SHEEP],
            "clay": self.val[Resource.CLAY],
            "wood": self.val[Resource.WOOD],
            "iron": self.val[Resource.IRON],
            "port": None if self.port is None else r2s(self.port)
        }
        return log

    def location_log(self):
        log = {
            "location x": self.location[0],
            "location y": self.location[1]
        }
        return log

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
        self.traveled = False

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
                lro = self.board.hands[self.board.longest_road_owner]   # type: Hand
                lro.subtract_point()
                lro.subtract_point()
            self.board.longest_road_owner = player
            hand = self.board.hands[player] # type: Hand
            hand.add_point()
            hand.add_point()

    def is_connected(self, player):
        if self.neighbors[0].connected[player] or self.neighbors[1].connected[player]:
            return True
        return False

    def is_legal(self, player):
        if self.owner is None and (self.is_connected(player)):
            return True
        return False

    def undo_build(self, info):
        c1, c2, lrs, lro = info
        player = self.owner
        self.owner = None
        n1, n2 = self.neighbors  # type: Crossroad, Crossroad
        n1.connected[player] = c1
        n2.connected[player] = c2
        self.board.longest_road_size = lrs
        self.board.longest_road_owner = lro

    def build(self, player):
        self.owner = player
        n1, n2 = self.neighbors
        hand = self.board.hands[player]
        hand.lands_log += [n1, n2]
        c1, c2 = n1.connected[player], n2.connected[player]
        n1.connected[player], n2.connected[player] = True, True
        self.upgrade_longest_road(player)
        lrs, lro = self.board.longest_road_size, self.board.longest_road_owner
        return c1, c2, lrs, lro

    def get_location(self):
        return str(self.neighbors[0].location) + " " + str(self.neighbors[1].location)

    def location_log(self):
        log = {
            "u": self.neighbors[0].location_log(),
            "v": self.neighbors[1].location_log()
        }
        return log


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
    def __init__(self, players, log):
        self.statistics_logger = StatisticsLogger()
        self.log = log
        self.players = players
        self.devStack = DevStack()
        self.dice = Dice.Dice()

        self.map = [[Terrain(10), Terrain(2), Terrain(9)],
                    [Terrain(12), Terrain(6), Terrain(4), Terrain(10)],
                    [Terrain(9), Terrain(11), Terrain(DESSERT), Terrain(3), Terrain(8)],
                    [Terrain(8), Terrain(3), Terrain(4), Terrain(5)],
                    [Terrain(5), Terrain(6), Terrain(11)]]

        self.bandit_location = None

        # create 2d array of crossroads
        self.crossroads = []  # type: list[list[Crossroad]]
        for i in range(12):
            line = []
            for j in range(cr_line_len[i]):
                cr = Crossroad(self)
                cr.location = (i, j)
                line.append(cr)
            self.crossroads.append(line)

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

        # link the terrains to their crossroads and vice versa and give them link to board
        for i, line in enumerate(self.map):
            for j, terrain in enumerate(line):
                terrain.location = (i, j)
                terrain.board = self
                top = 0 if i < 3 else 1
                terrain.crossroads += [self.crossroads[2 * i][j + top]]
                terrain.crossroads += [self.crossroads[2 * i + 1][j]]
                terrain.crossroads += [self.crossroads[2 * i + 1][j + 1]]
                terrain.crossroads += [self.crossroads[2 * i + 2][j]]
                terrain.crossroads += [self.crossroads[2 * i + 2][j + 1]]
                bottom = 1 if i < 2 else 0
                terrain.crossroads += [self.crossroads[2 * i + 3][j + bottom]]
                for cr in terrain.crossroads:
                    cr.terrains += [terrain]

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
        self.hands: list[Hand] = []
        for n in range(players):
            self.hands += [Hand(n, self)]

        self.api = None

        # longest road stats
        self.longest_road_size = 4
        self.longest_road_owner = None

        # largest army stats
        self.largest_army_size = 2
        self.largest_army_owner = None

    def shuffle_map(self):
        # shuffle the terrain on the board and link the crossroads to them
        resource_stack = [Resource.DESSERT] + [Resource.IRON] * 3 + [Resource.CLAY] * 3 + [Resource.WOOD] * 4 + [
            Resource.WHEAT] * 4 + [Resource.SHEEP] * 4
        for i, line in enumerate(self.map):
            for j, terrain in enumerate(line):
                index = random.randrange(0, len(resource_stack))
                resource = resource_stack.pop(index)
                if resource == Resource.DESSERT:
                    self.map[2][2].num = terrain.num
                    terrain.num = 7
                    terrain.has_bandit = True
                    self.bandit_location = terrain
                self.dice.number_to_terrain[terrain.num].append((i, j))
                terrain.set_resource(resource)
        # set the heuristic values of the crossroads
        for line in self.crossroads:
            for cr in line:
                cr.set_heuristic_value()

    def load_map(self, board_log):
        while board_log:
            terrain = board_log.pop()
            i, j = terrain['i'], terrain['j']
            number = terrain['number']
            resource = s2r(terrain['resource'])
            self.map[i][j].num = number
            self.map[i][j].set_resource(resource)
            if resource == Resource.DESSERT:
                self.map[i][j].has_bandit = True
                self.bandit_location = self.map[i][j]
            self.dice.number_to_terrain[self.map[i][j].num].append((i, j))
        # set the heuristic values of the crossroads
        for line in self.crossroads:
            for cr in line:
                cr.set_heuristic_value()

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

    def log_board(self):
        log = []
        for i, line in enumerate(self.map):
            for j, t in enumerate(line):
                t_log = t.get_log()
                t_log['i'] = i
                t_log['j'] = j
                log += [t_log]
        self.log.board(log)

    # ---- game development ---- #

    def next_turn(self, turn, rnd, dice=None):
        # Todo: delete comment
        # API.next_turn(self, turn, rnd, self.hands, dice)
        pass

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

    def get_two_legal_roads(self, hand: Hand):
        legal = []
        for line1 in self.roads:
            for road1 in line1:
                if road1.is_legal(hand.index):
                    info1 = road1.build(hand.index)
                    for line2 in self.roads:
                        for road2 in line2:
                            if road2.is_legal(hand.index):
                                legal += [(road1, road2)]
                    road1.undo_build(info1)
        return legal

    def get_names(self):
        names = []
        for h in self.hands:
            names += [h.name]
        return names

    def get_dice(self):
        return self.dice.dice1.number, self.dice.dice2.number


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
