from enum import Enum


# Todo: add resources (without) + lands (with dessert)
class Resource(Enum):
    WHEAT = 1
    SHEEP = 2
    CLAY = 3
    WOOD = 4
    IRON = 5
    DESSERT = 6


ROAD_PRICE = {Resource.WOOD: 1, Resource.CLAY: 1}
SETTLEMENT_PRICE = {Resource.WOOD: 1, Resource.CLAY: 1, Resource.WHEAT: 1, Resource.SHEEP: 1}
CITY_PRICE = {Resource.WHEAT: 2, Resource.IRON: 3}
DEV_PRICE = {Resource.SHEEP: 1, Resource.WHEAT: 1, Resource.IRON: 1}
