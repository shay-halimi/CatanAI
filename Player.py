from abc import ABC, abstractmethod
from Resources import Resource
from Board import Board
from Board import Crossroad
from random import randint
from Heuristics import SimpleHeuristic


def after_action(player):
    player.hand.print_resources()
    print("\n# ----   ---- #\n")


class Action(ABC):
    def __init__(self):
        self.name = 'action'
        self.heuristic = 0

    def do_action(self, player):
        player.hand.print_resources()
        print("player : " + player.name + " " + self.name)


class UseKnight(Action):
    def __init__(self, terrain, dst):
        super().__init__()
        self.terrain = terrain
        self.dst = dst
        self.name = 'use knight'

    def do_action(self, player):
        super().do_action(player)
        player.hand.use_knight(self.terrain, self.dst)
        after_action(player)


class UseMonopole(Action):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource
        self.name = 'use monopole'

    def do_action(self, player):
        super().do_action(player)
        player.hand.use_monopole(self.resource)
        after_action(player)


class UseYearOfPlenty(Action):
    def __init__(self, resource1, resource2):
        super().__init__()
        self.resource1 = resource1
        self.resource2 = resource2
        self.name = 'use year of plenty'

    def do_action(self, player):
        super().do_action(player)
        player.hand.use_year_of_plenty(self.resource1, self.resource2)
        after_action(player)


class UseBuildRoads(Action):
    def __init__(self, road1, road2):
        super().__init__()
        self.road1 = road1
        self.road2 = road2
        self.name = 'use build roads'

    def do_action(self, player):
        super().do_action(player)
        player.hand.build_2_roads(self.road1, self.road2)
        after_action(player)


class UseVictoryPoint(Action):
    def __init__(self, road1, road2):
        super().__init__()
        self.name = "use victory_point"

    def do_action(self, player):
        super().do_action(player)
        player.hand.use_victory_point()
        after_action(player)


class BuildSettlement(Action):
    def __init__(self, crossroad):
        super().__init__()
        self.crossroad = crossroad
        self.name = 'build settlement'

    def do_action(self, player):
        super().do_action(player)
        player.hand.buy_settlement(self.crossroad)
        after_action(player)


class BuildCity(Action):
    def __init__(self, crossroad):
        super().__init__()
        self.crossroad = crossroad
        self.name = 'build city'

    def do_action(self, player):
        super().do_action(player)
        player.hand.buy_city(self.crossroad)
        after_action(player)


class BuildRoad(Action):
    def __init__(self, road):
        super().__init__()
        self.road = road
        self.name = 'build road'

    def do_action(self, player):
        super().do_action(player)
        player.hand.buy_road(self.road)
        after_action(player)


class Trade(Action):
    def __init__(self, src, exchange_rate, dst, take):
        super().__init__()
        self.src = src
        self.dst = dst
        self.take = take
        self.give = take * exchange_rate
        self.name = 'trade'

    def do_action(self, player):
        super().do_action(player)
        player.hand.trade(self)
        after_action(player)


class BuyDevCard(Action):
    def __init__(self):
        super().__init__()
        self.name = 'buy devCard'

    def do_action(self, player):
        super().do_action(player)
        player.hand.buy_development_card(player.board.devStack)
        after_action(player)


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
        self.simple_heuristic = SimpleHeuristic(self.index, self.board)

    def throw_my_cards(self, num_cards):
        while num_cards > 0:
            resource_index = randint(1, 5)
            resource = Resource(resource_index)
            if min(self.hand.resources[resource], num_cards) > 0:
                cards_to_throw = randint(1, min(self.hand.resources[resource], num_cards))
                self.hand.resources[resource] -= cards_to_throw
                num_cards -= cards_to_throw

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
            for crossword in self.board.get_lands(self.index):
                legal_moves += [BuildSettlement(crossword)]
        if self.board.hands[self.index].can_buy_city():
            for settlement in self.board.get_settlements(self.index):
                legal_moves += [BuildCity(settlement)]
        if self.board.hands[self.index].can_buy_development_card():
            legal_moves += [BuyDevCard()]
        for resource in Resource:
            if resource is not Resource.DESSERT:
                can_trade, exchange_rate = self.hand.can_trade(resource, 1)
                if can_trade:
                    for dst in Resource:
                        if resource is not Resource.DESSERT:
                            legal_moves += [Trade(resource, exchange_rate, dst, 1)]
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
        self.hand.create_settlement(cr)
        self.hand.create_road(cr.neighbors[0].road)

    def computer_2nd_settlement(self, player):
        legal_crossroads = self.board.get_legal_crossroads_start(player)
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        self.hand.create_settlement(cr)
        cr.produce(self.index)
        self.hand.create_road(cr.neighbors[0].road)

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
                return True
        for a in actions:
            if isinstance(a, BuildCity):
                a.do_action(self)
                return True
        if not self.hand.get_lands() and self.hand.settlement_pieces:
            for a in actions:
                if isinstance(a, BuildRoad):
                    a.do_action(self)
                    return True
        for a in actions:
            if isinstance(a, Trade):
                if self.simple_heuristic.accept_trade(a):
                    a.do_action(self)
                    return True
        return False

    def compute_turn(self):
        self.simple_choice()
