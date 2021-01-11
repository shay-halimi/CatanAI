from Resources import Resource
import random


INVALID = 0
BANDIT = 7


class Terrain:
    def __init__(self, num=INVALID):
        self.resource = None
        self.num = num

    def __str__(self):
        return "("+str(self.num)+","+str(self.resource)+")"

    def set_resource(self, resource):
        self.resource = resource


class Map:
    def __init__(self):
        self.map = [[Terrain(),Terrain(),Terrain(10),Terrain(2),Terrain(9)],
                    [Terrain(),Terrain(12),Terrain(6),Terrain(4),Terrain(10)],
                    [Terrain(9),Terrain(11),Terrain(BANDIT),Terrain(3),Terrain(8)],
                    [Terrain(8),Terrain(3),Terrain(4),Terrain(5),Terrain()],
                    [Terrain(5),Terrain(6),Terrain(11),Terrain(),Terrain()]]
        resource_stack = [Resource.DESSERT] + [Resource.IRON]*3 + [Resource.CLAY]*3 + [Resource.WOOD]*4 + [Resource.WHEAT]*4 + [Resource.SHEEP]*4
        for line in self.map:
            for terrain in line:
                if terrain.num:
                    index = random.randrange(0, len(resource_stack))
                    resource = resource_stack.pop(index)
                    terrain.set_resource(resource)

    def __str__(self):
        map_str = ""
        for line in self.map:
            for terrain in line:
                map_str += f"{str(terrain):^30}"
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


test_terrain()
map = Map()
print(str(map))