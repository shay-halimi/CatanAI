from Resources import Resource


def r2s(resource: Resource):
    if resource is Resource.WOOD:
        return "wood"
    elif resource is Resource.CLAY:
        return "clay"
    elif resource is Resource.SHEEP:
        return "sheep"
    elif resource is Resource.WHEAT:
        return "wheat"
    elif resource is Resource.IRON:
        return "iron"
    else:
        return "NONE"


def s2r(str):
    if str == "wood":
        return Resource.WOOD
    elif str == "clay":
        return Resource.CLAY
    elif str == "sheep":
        return Resource.SHEEP
    elif str == "wheat":
        return Resource.WHEAT
    elif str == "iron":
        return Resource.IRON
    else:
        return Resource.DESSERT
