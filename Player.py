from Heuristics import SimpleHeuristic
from Heuristics import StatisticsHeuristic
from Heuristics import best_action
from Heuristics import greatest_crossroad
from Actions import Trade
from Actions import BuildFreeRoad
from Actions import BuildRoad
from Actions import BuildSettlement
from Actions import BuildFirstSettlement
from Actions import BuildSecondSettlement
from Actions import BuildCity
from Actions import DoNothing
from Actions import UseKnight
from Actions import UseMonopole
from Actions import UseBuildRoads
from Actions import UseYearOfPlenty
from Actions import BuyDevCard
from Board import Board
from Hand import Hand
from Resources import Resource
from Auxilary import s2r
from random import randint


class LogToAction:
    def __init__(self, board, player, action_log):
        self.player = player # type: Player
        self.hand = player.hand # type: Hand
        self.name = action_log['name']
        self.crossroads = board.crossroads
        if self.name == 'trade':
            self.src = s2r(action_log['source'])
            self.dst = s2r(action_log['destination'])
            self.take = action_log['take']
            self.exchange_rate = action_log['give'] / self.take
        elif self.name == 'build free road' or self.name == 'build road':
            self.road = self.get_road(action_log['location'])
        else:
            self.crossroad = self.get_crossroad(action_log['location'])

    def get_action(self):
        if self.name == 'trade':
            return Trade(self.hand, None, self.src, self.exchange_rate, self.dst, self.take)
        elif self.name == 'build free road':
            return BuildFreeRoad(self.hand, None, self.road)
        elif self.name == 'build road':
            return BuildRoad(self.hand, None, self.road)
        elif self.name == 'build settlement':
            return BuildSettlement(self.hand, None, self.crossroad)
        elif self.name == 'build first settlement':
            return BuildFirstSettlement(self.hand, None, self.crossroad)
        elif self.name == 'build second settlement':
            return BuildSecondSettlement(self.hand, None, self.crossroad)
        elif self.name == 'build city':
            return BuildCity(self.hand, None, self.crossroad)

    def get_crossroad(self, crossroad_log):
        x = crossroad_log['location x']
        y = crossroad_log['location y']
        return self.crossroads[x][y]

    def get_road(self, road_log):
        u = self.get_crossroad(road_log['u'])
        v = self.get_crossroad(road_log['v'])
        for n in u.neighbors:
            if v is n.crossroad:
                return n.road

    def is_legal(self):
        return True


def take_best_action(actions):
    if actions:
        best_action = actions.pop()
        for a in actions:
            if a.heuristic > best_action.heuristic:
                best_action = a
        best_action.do_action()
        return best_action
    else:
        return None


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
        self.log = self.board.log

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
        legal_moves += [DoNothing(self, None)]
        # finding legal moves from devCards
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["knight"]))) > 0:
            # need to check if the cards
            for terrain in self.board.map:
                for player in self.board.players:
                    if terrain == self.board.bandit_location:
                        continue
                    for p in range(self.board.players):
                        if p != self.index:
                            legal_moves += [UseKnight(self.hand, None, terrain, p)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["monopole"]))) > 0:
            for i in range(1, 6):
                legal_moves += [UseMonopole(self, None, Resource[i])]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["road builder"]))) > 0:
            for [road1, road2] in self.board.get_two_legal_roads(self.index):
                legal_moves += [UseBuildRoads(self.hand, None, road1, road2)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["year of prosper"]))) > 0:
            for i in range(1, 6):
                for j in range(1, 6):
                    legal_moves += [UseYearOfPlenty(self.hand, None, Resource[i], Resource[j])]
        if self.board.hands[self.index].can_buy_road():
            for road in self.board.get_legal_roads(self.index):
                legal_moves += [BuildRoad(self.hand, None, road)]
        if self.board.hands[self.index].can_buy_settlement():
            for crossword in self.board.get_lands(self.index):
                legal_moves += [BuildSettlement(self.hand, None, crossword)]
        if self.board.hands[self.index].can_buy_city():
            for settlement in self.board.get_settlements(self.index):
                legal_moves += [BuildCity(self.hand, None, settlement)]
        if self.board.hands[self.index].can_buy_development_card():
            legal_moves += [BuyDevCard(self.hand, None)]
        for resource in Resource:
            if resource is not Resource.DESSERT:
                can_trade, exchange_rate = self.hand.can_trade(resource, 1)
                if can_trade:
                    for dst in Resource:
                        if dst is not Resource.DESSERT:
                            legal_moves += [Trade(self.hand, None, resource, exchange_rate, dst, 1)]
        return legal_moves

    #########################################################################
    # AI player functions
    #########################################################################
    def computer_1st_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        cr = greatest_crossroad(legal_crossroads)
        BuildFirstSettlement(self.hand, None, cr).do_action()
        road = cr.neighbors[0].road
        BuildFreeRoad(self.hand, None, road).do_action()
        return cr, road

    def computer_2nd_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        cr = greatest_crossroad(legal_crossroads)
        BuildSecondSettlement(self.hand, None, cr).do_action()
        road = cr.neighbors[0].road
        BuildFreeRoad(self.hand, None, road).do_action()
        return cr, road

    def simple_choice(self):
        actions = self.get_legal_moves()
        settlements = []
        cities = []
        roads = []
        trades = []
        for a in actions:
            if isinstance(a, BuildSettlement):
                settlements += [a]
            elif isinstance(a, BuildCity):
                cities += [a]
            elif isinstance(a, BuildRoad):
                roads += [a]
            elif isinstance(a, Trade):
                trades += [a]
        a = None
        if settlements:
            a = best_action(settlements)
        elif cities:
            a = best_action(cities)
        elif roads:
            a = best_action(roads)
        elif trades:
            a = best_action(trades)
        if a:
            a.do_action()
        return a

    def compute_turn(self):
        return self.simple_choice()


class Dork(Player):
    def __init__(self, index, board: Board):
        super().__init__(index, board, "Dork")
        self.statistics = StatisticsHeuristic()

    def computer_1st_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        actions = []
        heuristic = self.statistics.settlement_value
        for cr in legal_crossroads:
            actions += [BuildFirstSettlement(self.hand, heuristic, cr)]
        best_action = take_best_action(actions)
        actions = []
        cr = best_action.crossroad
        # add heuristic for road
        for n in cr.neighbors:
            actions += [BuildFreeRoad(self.hand, None, n.road)]
        take_best_action(actions)

    def computer_2nd_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        actions = []
        heuristic = self.statistics.settlement_value
        for cr in legal_crossroads:
            actions += [BuildSecondSettlement(self.hand, heuristic, cr)]
        best_action = take_best_action(actions)
        actions = []
        cr = best_action.crossroad
        for n in cr.neighbors:
            actions += [BuildFreeRoad(self.hand, None, n.road)]
        take_best_action(actions)

    def simple_choice(self):
        actions = self.get_legal_moves()
        best_action = None
        for a in actions:
            if isinstance(a, BuildSettlement):
                if best_action is None:
                    best_action = a
                elif a.heuristic > best_action.heuristic:
                    best_action = a
        if best_action is not None:
            best_action.do_action()
            return True
        for a in actions:
            if isinstance(a, BuildCity):
                a.do_action()
                return True
        if not self.hand.get_lands() and self.hand.settlement_pieces:
            for a in actions:
                if isinstance(a, BuildRoad):
                    a.do_action()
                    return True
        for a in actions:
            if isinstance(a, Trade):
                if self.simple_heuristic.accept_trade(a):
                    a.do_action()
                    return True
        return False

    def compute_turn(self):
        self.simple_choice()
