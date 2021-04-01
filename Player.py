from Resources import Resource
from Board import Board
from Board import Crossroad


class Action:
    name = 'action'
    heuristic = 0


class use_knight(Action):
    name = 'use knight'

    def __init__(self, terrain):
        self.terrain = terrain


class use_monopole(Action):
    name = 'use monopole'

    def __init__(self, resource):
        self.resource = resource


class use_year_of_plenty(Action):
    name = 'use year of plenty'

    def __init__(self, resource1, resource2):
        self.resource1 = resource1
        self.resource2 = resource2


class use_build_roads(Action):
    name = 'use build roads'

    def __init__(self, road1, road2):
        self.road1 = road1
        self.road2 = road2


class use_victory_point(Action):
    name = "use victory_point"


class build_settlement(Action):
    name = 'build settlement'

    def __init__(self, crossroad):
        self.crossroad = crossroad


class build_city(Action):
    name = 'build city'

    def __init__(self, crossroad):
        self.crossroad = crossroad


class build_road(Action):
    name = 'build road'

    def __init__(self, road):
        self.road = road


class trade(Action):
    name = 'trade'

    def __init__(self, give, take):
        self.give = give
        self.take = take


class buy_dev_card(Action):
    name = 'buy devCard'


class Player:
    def __init__(self, index, board: Board, name=None, is_computer=True):
        self.index = index
        if name is None:
            self.name = "Player" + str(index)
        else:
            self.name = name
        self.is_computer = is_computer
        self.board = board
        self.hand = board.hands[index]
        self.hand.name = self.name

    def get_legal_moves(self):
        # TODO add legal moves by type. i.e move bandit need to come with all the locations you can move
        legal_moves = []
        # finding legal moves from devCards
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["knight"]))) > 0:
            # need to check if the cards
            for terrain in self.board.map:
                if terrain == self.board.bandit_location: continue
                legal_moves += [use_knight(terrain)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["monopole"]))) > 0:
            for i in range(1, 6):
                legal_moves += [use_monopole(Resource[i])]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["road building"]))) > 0:
            for road1 in self.board.get_legal_roads(self.index):
                # TODO we need to copy the board and add road1 to the map and than get legal roads
                for road2 in self.board.get_legal_roads(self.index):
                    legal_moves += [use_build_roads(road1, road2)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["year of plenty"]))) > 0:
            # need to check if the cards
            for i in range(1,6):
                for j in range(1,6):
                    legal_moves += [use_year_of_plenty(Resource[i], Resource[j])]
        if self.board.hands[self.index].can_buy_road:
            for road in self.board.get_legal_roads(self.index):
                legal_moves += [build_road(road)]
        if self.board.hands[self.index].can_buy_settlement:
            for crossword in self.board.get_legal_crossroads():
                legal_moves += [build_settlement(crossword)]
        if self.board.hands[self.index].can_buy_city:
            pass
            #TODO finish here legal_moves += [build_city(crossword)]
        if self.board.hands[self.index].can_buy_Devcard:
            legal_moves += [buy_dev_card()]
        return legal_moves

    def buy_devops(self):
        return self.hand.buy_development_card()

    def buy_settlement(self, cr):
        return self.hand.buy_settlement(cr)

    def buy_city(self, cr):
        return self.hand.buy_city(cr)

    def buy_road(self, road):
        return self.hand.buy_road(road)

    def use_knight(self, terrain, dst):
        self.hand.use_knight(terrain, dst)

    #########################################################################
    # AI player functions
    #########################################################################
    def computer_1st_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start(self.index)
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        return cr, cr.neighbors[0].road

    def computer_2nd_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start(self.index)
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        return cr, cr.neighbors[0].road
