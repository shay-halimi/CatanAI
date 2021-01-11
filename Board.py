from Resources import Resource
import random

INVALID = 0
DESSERT = 7


class Terrain:
    def __init__(self, num=INVALID):
        self.resource = None
        self.num = num
        self.crossroads = []

    def __str__(self):
        return "(" + str(self.num) + "," + str(self.resource) + ")"

    def print_top_crossroads(self):
        print("terrain : " + str(self) + " has " + str(len(self.crossroads)) + "crossroads")
        nums = ""
        for i in range(0,3):
            nums += f"{str(self.crossroads[i].ownership):^10}"
        return nums

    def print_bot_crossroads(self):
        nums = ""
        for i in range(3,6):
            nums += f"{str(self.crossroads[i].ownership):^10}"
        return nums

    def set_resource(self, resource):
        self.resource = resource

    def produce(self):
        pass  # Todo: produce shoul call a "give resource" function to every structure in her presence.


# Todo: add special case to ports
class Crossroad:
    def __init__(self):
        self.ownership = None
        self.building = None


def initiate_crossroads_for_test(crossroads_map):
    i = 0
    for line in crossroads_map:
        for crossroad in line:
            crossroad.ownership = i
            i += 1


class Board:
    def __init__(self):
        self.map = [[Terrain(), Terrain(), Terrain(10), Terrain(2), Terrain(9)],
                    [Terrain(), Terrain(12), Terrain(6), Terrain(4), Terrain(10)],
                    [Terrain(9), Terrain(11), Terrain(DESSERT), Terrain(3), Terrain(8)],
                    [Terrain(8), Terrain(3), Terrain(4), Terrain(5), Terrain()],
                    [Terrain(5), Terrain(6), Terrain(11), Terrain(), Terrain()]]
        self.crossroads = []
        for i in range(6):
            line = []
            for j in range(12):
                line.append(Crossroad())
            self.crossroads.append(line)
        initiate_crossroads_for_test(self.crossroads)
        resource_stack = [Resource.DESSERT] + [Resource.IRON] * 3 + [Resource.CLAY] * 3 + [Resource.WOOD] * 4 + [
            Resource.WHEAT] * 4 + [Resource.SHEEP] * 4
        i = 0
        for line in self.map:
            j = 0
            for terrain in line:
                if terrain.num:
                    index = random.randrange(0, len(resource_stack))
                    resource = resource_stack.pop(index)
                    terrain.set_resource(resource)
                    terrain.crossroads += [self.crossroads[i][2 * j + 1]]
                    terrain.crossroads += [self.crossroads[i][2 * j + 2]]
                    terrain.crossroads += [self.crossroads[i][2 * j + 3]]
                    terrain.crossroads += [self.crossroads[i + 1][2 * j]]
                    terrain.crossroads += [self.crossroads[i + 1][2 * j + 1]]
                    terrain.crossroads += [self.crossroads[i + 1][2 * j + 2]]
                j += 1
            i += 1

    def __str__(self):
        map_str = ""
        for line in self.map:
            for terrain in line:
                if terrain.num:
                    map_str += terrain.print_top_crossroads()
                else:
                    s = ""
                    map_str += f"{s:^30}"
            map_str += "\n"
            for terrain in line:
                map_str += f"{str(terrain):^30}"
            map_str += "\n"
            for terrain in line:
                if terrain.num:
                    map_str += terrain.print_bot_crossroads()
                else:
                    s = ""
                    map_str += f"{s:^30}"
            map_str += "\n"
        return map_str


def test_terrain():
    terrain = Terrain()
    print(terrain)
    print("PASS") if str(terrain) == "(0,None)" else print("FAILED")
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


test_terrain()
test_board()
