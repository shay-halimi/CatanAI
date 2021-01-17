from Resources import Resource
import random

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


# Todo: add special case to ports
class Crossroad:
    def __init__(self):
        self.ownership = None
        self.building = None
        self.api_location = None


class Road:
    def __init__(self, owner=0):
        self.owner = owner


class Board:
    def __init__(self):

        self.map = [[Terrain(10), Terrain(2), Terrain(9)],
                    [Terrain(12), Terrain(6), Terrain(4), Terrain(10)],
                    [Terrain(9), Terrain(11), Terrain(DESSERT), Terrain(3), Terrain(8)],
                    [Terrain(8), Terrain(3), Terrain(4), Terrain(5)],
                    [Terrain(5), Terrain(6), Terrain(11)]]

        self.crossroads = []
        num_of_crossroads = 3
        odd = True
        step = 1
        for i in range(12):
            line = []
            for j in range(num_of_crossroads):
                line.append(Crossroad())
            self.crossroads.append(line)
            if odd:
                num_of_crossroads += step
            if i == 5:
                step = -1
            odd = 1 - odd
        for line in self.crossroads:
            print(len(line))

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
                terrain.set_resource(resource)
                terrain.crossroads += [self.crossroads[2 * i][j]]
                terrain.crossroads += [self.crossroads[2 * i + 1][j]]
                terrain.crossroads += [self.crossroads[2 * i + 1][j + 1]]
                terrain.crossroads += [self.crossroads[2 * i + 2][j]]
                terrain.crossroads += [self.crossroads[2 * i + 2][j + 1]]
                terrain.crossroads += [self.crossroads[2 * i + 3][j]]
                j += 1
            i += 1

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
                        line.append(Road())
                    length += step * mid
                if i == 4:
                    step = 0
                if i == 5:
                    step = -1
                    mid = 1
                self.roads.append(line)


def test_terrain():
    terrain = Terrain(3)
    print(terrain)
    print("PASS") if str(terrain) == "(3,None)" else print("FAILED")
    terrain.set_resource(Resource.IRON)
    print(terrain)
    print("PASS") if str(terrain) == "(3,Resource.IRON)" else print("FAILED")


def test_board():
    print("This is a random map:")
    board = Board()
    print(str(board))


def test_crossroads(crossroads):
    for line in crossroads:
        for cr in line:
            cr.ownership = random.randrange(0, 5)


test_terrain()
test_board()
