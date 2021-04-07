from abc import ABC, abstractmethod
from Resources import Resource
from Board import Board
from Board import Crossroad
from random import randint


class Action(ABC):
    name = 'action'
    heuristic = 0

    @abstractmethod
    def do_action(self, player):
        pass


class use_knight(Action):
    name = 'use knight'

    def __init__(self, terrain, dst):
        self.terrain = terrain
        self.dst = dst

    def do_action(self, player):
        print(self)
        player.hand.use_knight(self.terrain, self.dst)


class use_monopole(Action):
    name = 'use monopole'

    def __init__(self, resource):
        self.resource = resource

    def do_action(self, player):
        print(self)
        player.hand.use_monopole(self.resource)


class use_year_of_plenty(Action):
    name = 'use year of plenty'

    def __init__(self, resource1, resource2):
        self.resource1 = resource1
        self.resource2 = resource2

    def do_action(self, player):
        print(self)
        player.hand.use_year_of_plenty(self.resource1, self.resource2)


class use_build_roads(Action):
    name = 'use build roads'

    def __init__(self, road1, road2):
        self.road1 = road1
        self.road2 = road2

    def do_action(self, player):
        print(self)
        player.hand.build_2_roads(self.road1, self.road2)


class use_victory_point(Action):
    name = "use victory_point"

    def do_action(self, player):
        print(self)
        player.hand.use_victory_point()


class build_settlement(Action):
    name = 'build settlement'

    def __init__(self, crossroad):
        self.crossroad = crossroad

    def do_action(self, player):
        print(self)
        player.hand.buy_settlement(self.crossroad)


class build_city(Action):
    name = 'build city'

    def __init__(self, crossroad):
        self.crossroad = crossroad

    def do_action(self, player):
        print(self)
        player.hand.buy_city(self.crossroad)


class build_road(Action):
    name = 'build road'

    def __init__(self, road):
        self.road = road

    def do_action(self, player):
        print(self)
        player.hand.buy_road(self.road)


class trade(Action):
    name = 'trade'

    def __init__(self, src, dst, amount):
        self.src = src
        self.dst = dst
        self.amount = amount

    def do_action(self, player):
        player.hand.trade(self.src, self.dst)
        pass


class buy_dev_card(Action):
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
                    legal_moves += [use_knight(terrain)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["monopole"]))) > 0:
            for i in range(1, 6):
                legal_moves += [use_monopole(Resource[i])]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["road builder"]))) > 0:
            for [road1, road2] in self.board.get_two_legal_roads(self.index):
                legal_moves += [use_build_roads(road1, road2)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["year of prosper"]))) > 0:
            # need to check if the cards
            for i in range(1, 6):
                for j in range(1, 6):
                    legal_moves += [use_year_of_plenty(Resource[i], Resource[j])]
        if self.board.hands[self.index].can_buy_road():
            for road in self.board.get_legal_roads(self.index):
                legal_moves += [build_road(road)]
        if self.board.hands[self.index].can_buy_settlement():
            for crossword in self.board.get_legal_crossroads(self.index):
                legal_moves += [build_settlement(crossword)]
        if self.board.hands[self.index].can_buy_city():
            # todo get settlements
            pass
        if self.board.hands[self.index].can_buy_development_card():
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


    def compute_turn(self):
        self.computer_random_action()