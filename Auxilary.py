from Resources import Resource


def r2s(resource: Resource):
    if resource is Resource.WOOD:
        return "wood"
    elif resource is Resource.CLAY:
        return  "clay"
    elif resource is Resource.SHEEP:
        return "sheep"
    elif resource is Resource.WHEAT:
        return "wheat"
    elif resource is Resource.IRON:
        return "iron"
    else:
        return "NONE"
