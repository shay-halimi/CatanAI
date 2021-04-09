from abc import ABC, abstractmethod
from Resources import Resource
from Board import Board
from Board import Crossroad
from random import randint


class Action(ABC):
    def __init__(self):
        self.name = 'action'
        self.heuristic = 0

    @abstractmethod
    def do_action(self, player):
        pass


class UseKnight(Action):
    name = 'use knight'

    def __init__(self, terrain, dst):
        super().__init__()
        self.terrain = terrain
        self.dst = dst

    def do_action(self, player):
        print(self)
        player.hand.use_knight(self.terrain, self.dst)


class UseMonopole(Action):
    name = 'use monopole'

    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    def do_action(self, player):
        print(self)
        self.hand.use_monopole(self.resource)


class UseYearOfPlenty(Action):
    name = 'use year of plenty'

    def __init__(self, resource1, resource2):
        super().__init__()
        self.resource1 = resource1
        self.resource2 = resource2

    def do_action(self, player):
        print(self)
        player.hand.use_year_of_plenty(self.resource1, self.resource2)


class UseBuildRoads(Action):
    name = 'use build roads'

    def __init__(self, road1, road2):
        super().__init__()
        self.road1 = road1
        self.road2 = road2

    def do_action(self, player):
        print(self)
        player.hand.build_2_roads(self.road1, self.road2)


class UseVictoryPoint(Action):
    name = "use victory_point"

    def do_action(self, player):
        print(self)
        player.hand.use_victory_point()


class BuildSettlement(Action):
    name = 'build settlement'

    def __init__(self, crossroad):
        super().__init__()
        self.crossroad = crossroad

    def do_action(self, player):
        print(self)
        player.hand.buy_settlement(self.crossroad)


class BuildCity(Action):
    name = 'build city'

    def __init__(self, crossroad):
        super().__init__()
        self.crossroad = crossroad

    def do_action(self, player):
        print(self)
        player.hand.buy_city(self.crossroad)


class BuildRoad(Action):
    name = 'build road'

    def __init__(self, road):
        super().__init__()
        self.road = road

    def do_action(self, player):
        print(self)
        player.hand.buy_road(self.road)


class Trade(Action):
    name = 'trade'

    def __init__(self, src, dst, amount):
        super().__init__()
        self.src = src
        self.dst = dst
        self.amount = amount

    def do_action(self, player):
        player.hand.trade(self.src, self.dst)
        pass


class BuyDevCard(Action):
    name = 'buy devCard'

    def do_action(self, player):
        player.hand.buy_development_card(player.board.devStack)


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
        legal_moves = []
        # finding legal moves from devCards
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["knight"]))) > 0:
            # need to check if the cards
            for terrain in self.board.map:
                for player in self.board.players:
                    if terrain == self.board.bandit_location: continue
                    for p in range(self.board.players):
                        if p is not self.index:
                            legal_moves += [UseKnight(terrain, p)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["monopole"]))) > 0:
            for i in range(1, 6):
                legal_moves += [UseMonopole(Resource[i])]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["road builder"]))) > 0:
            for [road1, road2] in self.board.get_two_legal_roads(self.index):
                legal_moves += [UseBuildRoads(road1, road2)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["year of prosper"]))) > 0:
            # need to check if the cards
            for i in range(1, 6):
                for j in range(1, 6):
                    legal_moves += [UseYearOfPlenty(Resource[i], Resource[j])]
        if self.board.hands[self.index].can_buy_road():
            for road in self.board.get_legal_roads(self.index):
                legal_moves += [BuildRoad(road)]
        if self.board.hands[self.index].can_buy_settlement():
            for crossword in self.board.get_legal_crossroads(self.index):
                legal_moves += [BuildSettlement(crossword)]
        if self.board.hands[self.index].can_buy_city():
            # todo get settlements
            pass
        if self.board.hands[self.index].can_buy_development_card():
            legal_moves += [BuyDevCard()]
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

    def do_action(self, action):
        pass

    #########################################################################
    # AI player functions
    #########################################################################
    def computer_1st_settlement(self, player):
        legal_crossroads = self.board.get_legal_crossroads_start(player)
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        return cr, cr.neighbors[0].road

    def computer_2nd_settlement(self, player):
        legal_crossroads = self.board.get_legal_crossroads_start(player)
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        return cr, cr.neighbors[0].road

    def computer_random_action(self):
        legal_moves = self.get_legal_moves()
        if legal_moves:
            random_index = randint(0, len(legal_moves) - 1)
            legal_moves[random_index].do_action(self)
        return

    def simple_choice(self):
        actions = self.get_legal_moves()
        for a in actions:
            if isinstance(a, BuildSettlement):
                a.do_action(self)
                return
        for a in actions:
            if isinstance(a, BuildCity):
                a.do_action(self)
        if not self.hand.get_lands():
            for a in actions:
                if isinstance(a, BuildRoad):
                    a.do_action(self)
        if False:
            for a in actions:
                if isinstance(a, Trade):
                    a.do_action(self)

    def compute_turn(self):
        self.simple_choice()
