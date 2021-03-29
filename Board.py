from Resources import Resource
import random
import Dice

DESSERT = 7


class Terrain:
    def __init__(self, num):
        self.resource = None
        self.num = num
        self.crossroads = []

    def __str__(self):
        return "(" + str(self.num) + "," + str(self.resource) + ")"

    def set_resource(self, resource):
        self.resource = resource

    def produce(self):
        pass  # Todo: produce should call a "give resource" function to every structure in her presence.


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


# Todo: add special case to ports
class Crossroad:
    def __init__(self):
        self.ownership = None
        self.building = None
        self.location = None
        self.api_location = None
        self.neighbors = []
        self.legal = True
        self.connected = {}
        self.roads = []

    def aux_build(self, player):
        if self.ownership is None:
            self.ownership = player
            for n in self.neighbors:
                n.legal = False
        if self.ownership == player and self.building < 2:
            self.building += 1
            return True
        return False

    def build(self, player):
        if self.legal and self.connected[player]:
            return self.aux_build(player)

    def build_start(self, player):
        if self.legal:
            return self.aux_build(player)

    def add_road(self, road):
        self.roads += [road]


class Road:
    def __init__(self, owner=0):
        self.owner = owner
        self.api_location = [0, 0, 0, 0]
        self.neighbors = []

    def build(self, player):
        if self.owner == 0 and (self.neighbors[0].connected[player] or self.neighbors[1].connected[player]):
            self.owner = player
            self.neighbors[0].connected[player] = True
            self.neighbors[1].connected[player] = True
            return True
        return False


class Board:
    def __init__(self):

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
                cr = Crossroad()
                cr.location = (i, j)
                line.append(cr)
            self.crossroads.append(line)

        # add cross road neighbors to each cross road
        for i in range(len(self.crossroads)):
            j = 0
            for cr in self.crossroads[i]:
                if i % 2 == 0:
                    self.add_neighbor_cr(cr, i - 1, j)
                    self.add_neighbor_cr(cr, i + 1, j)
                    self.add_neighbor_cr(cr, i + 1, j + 1)
                else:
                    self.add_neighbor_cr(cr, i - 1, j - 1)
                    self.add_neighbor_cr(cr, i - 1, j)
                    self.add_neighbor_cr(cr, i + 1, j)
                j += 1

        # shuffle the terrain on the board and link the cross roads to them
        resource_stack = [Resource.DESSERT] + [Resource.IRON] * 3 + [Resource.CLAY] * 3 + [Resource.WOOD] * 4 + [
            Resource.WHEAT] * 4 + [Resource.SHEEP] * 4
        i = 0
        for line in self.map:
            j = 0
            for terrain in line:
                index = random.randrange(0, len(resource_stack))
                resource = resource_stack.pop(index)
                if resource == Resource.DESSERT:
                    self.map[2][2].num = terrain.num
                    terrain.num = 7
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

        # create the roads
        self.roads = []
        length = 3
        step = 1
        mid = 0
        for i in range(11):
            line = []
            if i % 2:
                for j in range(length + 1):
                    line.append(Road())
                length += step * (1 - mid)
            else:
                for j in range(2 * length):
                    r = Road()
                    r.neighbors += []
                    line.append(r)
                length += step * mid
            if i == 4:
                step = 0
            if i == 5:
                step = -1
                mid = 1
            self.roads.append(line)

        # link cross roads to roads
        self.add_neighbors_to_roads()

    def add_neighbor_cr(self, cr, i, j):
        if 0 <= i < 12 and 0 <= j < cr_line_len[i]:
            cr.neighbors += [self.crossroads[i][j]]

    # very convoluted function to link each road with its vertices cross roads and vice versa
    def add_neighbors_to_roads(self):
        i = 0
        xor = False
        for line in self.roads:
            up = 0
            down = 0
            if i == 5:
                xor = True
            for road in line:
                cr = self.crossroads[i][up]
                cr.add_road(road)
                road.neighbors += [cr]
                cr = self.crossroads[i + 1][down]
                cr.add_road(road)
                road.neighbors += [cr]
                if i % 2:
                    up += 1
                    down += 1
                else:
                    if (up == down) != xor:
                        down += 1
                    else:
                        up += 1
            i += 1

    # ToDo : make sure the place is legal
    def get_legal_crossroads(self):
        legal = []
        for i in range(12):
            for j in range(len(self.crossroads[i])):
                legal += [(i, j)]
        return legal


def test_crossroads(crossroads):
    for line in crossroads:
        for cr in line:
            cr.ownership = random.randrange(0, 5)
            cr.building = random.randrange(1, 3)


def test_roads(roads):
    for line in roads:
        for road in line:
            road.owner = random.randrange(0, 5)
