from abc import ABC
from Resources import Resource
from Board import SETTLEMENT_PRICE
from Board import ROAD_PRICE
from Board import  CITY_PRICE
from Board import Board
from Board import Crossroad
from random import randint
import math
from Heuristics import SimpleHeuristic
from Heuristics import StatisticsHeuristic
from Auxilary import r2s
from random import uniform
from Auxilary import s2r


class LogToAction:
    def __init__(self, board, player, action_log):
        self.player = player
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
            return Trade(self.player, None, self.src, self.exchange_rate, self.dst, self.take)
        elif self.name == 'build free road':
            return BuildFreeRoad(self.player, None, self.road)
        elif self.name == 'build road':
            return BuildRoad(self.player, None, self.road)
        elif self.name == 'build settlement':
            return BuildSettlement(self.player, None, self.crossroad)
        elif self.name == 'build first settlement':
            return BuildFirstSettlement(self.player, None, self.crossroad)
        elif self.name == 'build second settlement':
            return BuildSecondSettlement(self.player, None, self.crossroad)
        elif self.name == 'build city':
            return BuildCity(self.player, None, self.crossroad)

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


class Action(ABC):
    def __init__(self, player, heuristic_method):
        self.player = player
        self.heuristic_method = heuristic_method
        self.heuristic = uniform(0, 1) if self.heuristic_method is None else self.heuristic_method(self)
        self.log = self.player.log
        self.name = 'action'

    def do_action(self):
        self.player.hand.print_resources()
        print("player : " + self.player.name + " " + self.name)
        self.log_action()

    def compute_heuristic(self):
        pass

    def log_action(self):
        return {'name': self.name}


class DoNothing(Action):
    def __init__(self, player, heuristic_method):
        super().__init__(player, heuristic_method)
        self.name = 'do nothing'

    def do_action(self):
        pass

    def compute_heuristic(self):
        return self.player.hand.heuristic


class UseKnight(Action):
    def __init__(self, player, heuristic_method, terrain, dst):
        super().__init__(player, heuristic_method)
        self.terrain = terrain
        self.dst = dst
        self.name = 'use knight'

    def do_action(self):
        super().do_action()
        self.player.hand.use_knight(self.terrain, self.dst)

    def compute_heuristic(self):
        resource = self.player.hand.use_knight(self.terrain, self.dst)
        new_heuristic = self.player.hand.heuristic
        self.player.hand.undo_use_knight(resource, self.terrain, self.dst)
        return new_heuristic


class UseMonopole(Action):
    def __init__(self, player, heuristic_method, resource):
        super().__init__(player, heuristic_method)
        self.resource = resource
        self.name = 'use monopole'

    def do_action(self):
        super().do_action()
        self.player.hand.use_monopole(self.resource)

    def compute_heuristic(self):
        selected_resource_quantity = 0
        for hand in self.player.board.players:
            selected_resource_quantity += hand.resources[self.resource]
        return self.player.hand.heuristic + (
                self.player.hand.resource_value[self.resource] * selected_resource_quantity)


class UseYearOfPlenty(Action):
    def __init__(self, player, heuristic_method, resource1, resource2):
        super().__init__(player, heuristic_method)
        self.resource1 = resource1
        self.resource2 = resource2
        self.name = 'use year of plenty'

    def do_action(self):
        super().do_action()
        self.player.hand.use_year_of_plenty(self.resource1, self.resource2)

    def compute_heuristic(self):
        player = self.player
        return player.hand.resource_value[self.resource1] + player.hand.resource_value[self.resource1]


class UseBuildRoads(Action):
    def __init__(self, player, heuristic_method, road1, road2):
        super().__init__(player, heuristic_method)
        self.road1 = road1
        self.road2 = road2
        self.name = 'use build roads'

    def do_action(self):
        super().do_action()
        self.player.hand.build_2_roads(self.road1, self.road2)

    def compute_heuristic(self):
        heuristic_increment = 0
        player = self.player
        old_road_length = player.longest_road_value
        if player.board.longest_road_owner != player.index:
            player.tmp_buy_road(self.road1)
            player.tmp_buy_road(self.road2)
            heuristic_increment += (player.board.longest_road_owner == player.index) * 5
        else:
            player.hand.tmp_buy_road(self.road1)
            self.player.hand.tmp_buy_road(self.road2)
        heuristic_increment += player.longest_road_value - old_road_length
        player.hand.undo_buy_road(self.road2)
        player.hand.undo_buy_road(self.road1)
        return heuristic_increment + player.hand.heuristic


class UseVictoryPoint(Action):
    def __init__(self, player, heuristic_method):
        super().__init__(player, heuristic_method)
        self.name = "use victory_point"

    def do_action(self):
        super().do_action()
        self.player.hand.use_victory_point()

    def compute_heuristic(self):
        player = self.player
        if len(list(filter(lambda x: x.ok_to_use, player.hand.cards["victory points"]))) + player.hand.points >= 10:
            return math.inf
        else:
            return -math.inf


class BuildSettlement(Action):
    def __init__(self, player, heuristic_method, crossroad):
        self.crossroad = crossroad
        self.name = 'build settlement'
        super().__init__(player, heuristic_method)

    def do_action(self):
        super().do_action()
        self.player.hand.buy_settlement(self.crossroad)

    def log_action(self):
        log = {
            'name': self.name,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.player.hand.can_pay(SETTLEMENT_PRICE)


class BuildFirstSettlement(BuildSettlement):
    def __init__(self, player, heuristic_method, crossroad):
        super().__init__(player, heuristic_method, crossroad)
        self.name = 'build first settlement'

    def do_action(self):
        self.player.hand.create_settlement(self.crossroad)
        self.log_action()

    def is_legal(self):
        return True


class BuildSecondSettlement(BuildSettlement):
    def __init__(self, player, heuristic_method, crossroad):
        super().__init__(player, heuristic_method, crossroad)
        self.name = 'build second settlement'

    def do_action(self):
        self.player.hand.create_settlement(self.crossroad)
        self.crossroad.produce(self.player.index)
        self.log_action()

    def is_legal(self):
        return True


class BuildCity(Action):
    def __init__(self, player, heuristic_method, crossroad):
        super().__init__(player, heuristic_method)
        self.crossroad = crossroad
        self.name = 'build city'

    def do_action(self):
        super().do_action()
        self.player.hand.buy_city(self.crossroad)

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.player.hand.can_pay(CITY_PRICE)


class BuildRoad(Action):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method)
        self.road = road
        self.name = 'build road'

    def do_action(self):
        super().do_action()
        self.player.hand.buy_road(self)

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'location': self.road.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.player.hand.can_pay(ROAD_PRICE)


class BuildFreeRoad(BuildRoad):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method, road)
        self.name = 'build free road'

    def do_action(self):
        self.player.hand.create_road(self.road)
        self.log_action()

    def is_legal(self):
        return True


class Trade(Action):
    def __init__(self, player, heuristic_method, src, exchange_rate, dst, take):
        super().__init__(player, heuristic_method)
        self.src = src
        self.dst = dst
        self.take = take
        self.give = take * exchange_rate
        self.name = 'trade'

    def do_action(self):
        super().do_action()
        self.player.hand.trade(self)

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'source': r2s(self.src),
            'destination': r2s(self.dst),
            'take': self.take,
            'give': self.give
        }
        self.log.action(log)

    def is_legal(self):
        return self.player.hand.can_pay({self.src: self.give})


class BuyDevCard(Action):
    def __init__(self, player, heuristic_method):
        super().__init__(player, heuristic_method)
        self.name = 'buy devCard'

    def do_action(self):
        super().do_action()
        self.player.hand.buy_development_card(self.player.board.devStack)

    def compute_heuristic(self):
        player = self.player
        return player.hand.heuristic + player.hand.dev_card_value


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
                            legal_moves += [UseKnight(self, None, terrain, p)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["monopole"]))) > 0:
            for i in range(1, 6):
                legal_moves += [UseMonopole(self, None, Resource[i])]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["road builder"]))) > 0:
            for [road1, road2] in self.board.get_two_legal_roads(self.index):
                legal_moves += [UseBuildRoads(self, None, road1, road2)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["year of prosper"]))) > 0:
            # need to check if the cards
            for i in range(1, 6):
                for j in range(1, 6):
                    legal_moves += [UseYearOfPlenty(self, None, Resource[i], Resource[j])]
        if self.board.hands[self.index].can_buy_road():
            for road in self.board.get_legal_roads(self.index):
                legal_moves += [BuildRoad(self, None, road)]
        if self.board.hands[self.index].can_buy_settlement():
            for crossword in self.board.get_lands(self.index):
                legal_moves += [BuildSettlement(self, None, crossword)]
        if self.board.hands[self.index].can_buy_city():
            for settlement in self.board.get_settlements(self.index):
                legal_moves += [BuildCity(self, None, settlement)]
        if self.board.hands[self.index].can_buy_development_card():
            legal_moves += [BuyDevCard(self, None)]
        for resource in Resource:
            if resource is not Resource.DESSERT:
                can_trade, exchange_rate = self.hand.can_trade(resource, 1)
                if can_trade:
                    for dst in Resource:
                        if resource is not Resource.DESSERT:
                            legal_moves += [Trade(self, None, resource, exchange_rate, dst, 1)]
        return legal_moves

    #########################################################################
    # AI player functions
    #########################################################################
    def computer_1st_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        BuildFirstSettlement(self, None, cr).do_action()
        road = cr.neighbors[0].road
        BuildFreeRoad(self, None, road).do_action()
        return cr, road

    def computer_2nd_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        BuildSecondSettlement(self, None, cr).do_action()
        road = cr.neighbors[0].road
        BuildFreeRoad(self, None, road).do_action()
        return cr, road

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
                a.do_action()
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


class Dork(Player):
    def __init__(self, index, board: Board):
        super().__init__(index, board, "Dork")
        self.statistics = StatisticsHeuristic()

    def computer_1st_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        actions = []
        heuristic = self.statistics.settlement_value
        for cr in legal_crossroads:
            actions += [BuildFirstSettlement(self, heuristic, cr)]
        best_action = take_best_action(actions)
        actions = []
        cr = best_action.crossroad
        for n in cr.neighbors:
            actions += [BuildFreeRoad(self, None, n.road)]
        take_best_action(actions)

    def computer_2nd_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        actions = []
        heuristic = self.statistics.settlement_value
        for cr in legal_crossroads:
            actions += [BuildSecondSettlement(self, heuristic, cr)]
        best_action = take_best_action(actions)
        actions = []
        cr = best_action.crossroad
        for n in cr.neighbors:
            actions += [BuildFreeRoad(self, None, n.road)]
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
