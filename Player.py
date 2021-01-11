import DevStack
from Resources import Resource

class player:
    resources = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.SHEEP: 0, Resource.IRON: 0, Resource.WHEAT: 0}
    devCards = DevStack()

    def __init__(self,index,name=None):
        self.index=index
        self.name=name
        self.resources={Resource.CLAY : 0 , Resource.WOOD : 0, Resource.SHEEP: 0, Resource.IRON : 0, Resource.WHEAT:0}
        self.devCards = []
    def add_resources(resource,number):
        player.resources[resource]+=number
    def buy_devops:
        if(Resource.SHEEP<1 or Resource.IRON<1 or Resource.WHEAT<1):
            print("Not enough resources")
            return
        player.resources[Resource.SHEEP]-=1
        player.resources[Resource.IRON] -= 1
        player.resources[Resource.WHEAT] -=1
        player.devCards.append(Game.devStack.get())

