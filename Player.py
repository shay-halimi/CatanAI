from Heuristics import SimpleHeuristic
from Heuristics import StatisticsHeuristic
from Heuristics import best_action
from Heuristics import greatest_crossroad
from Heuristics import hand_heuristic
from Heuristics import show_score_analysis
from Actions import Trade
from Actions import BuildFreeRoad
from Actions import BuildRoad
from Actions import BuildSettlement
from Actions import BuildFirstSettlement
from Actions import BuildSecondSettlement
from Actions import BuildCity
from Actions import DoNothing
from Actions import UseDevCard
from Actions import UseKnight
from Actions import UseMonopole
from Actions import UseBuildRoads
from Actions import UseYearOfPlenty
from Actions import BuyDevCard
from Actions import ThrowCards
from Actions import Action
from Board import Board,Terrain,Crossroad
from Hand import Hand
from Resources import Resource
from Auxilary import s2r
from random import randint


class LogToAction:
    def __init__(self, board, player, action_log):
        self.player = player  # type: Player
        self.hand = player.hand  # type: Hand
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


def take_best_action(actions):
    if actions:
        baction = actions.pop() # type: Action
        for a in actions:
            if a.heuristic > baction.heuristic:
                baction = a
        baction.do_action()
        print('taken action : ' + baction.name)
        print('user : ' + str(baction.index))
        print('score : ' + str(baction.heuristic))
        print('\n\n')
        return baction
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
        self.board: Board = board
        self.hand = board.hands[index]
        self.hand.name = self.name
        self.simple_heuristic = SimpleHeuristic(self.index, self.board)
        self.log = self.board.log

    def throw_my_cards(self, num_cards):
        cards = {}
        while num_cards > 0:
            resource_index = randint(1, 5)
            resource = Resource(resource_index)
            if resource not in cards:
                cards[resource] = 0
            if min(self.hand.resources[resource], num_cards) > 0:
                cards_to_throw = randint(1, min(self.hand.resources[resource], num_cards))
                cards[resource] += cards_to_throw
                num_cards -= cards_to_throw
        ThrowCards(self.hand, None, cards)

    def get_legal_moves(self, heuristic) -> list[Action]:
        legal_moves = []
        h = None if heuristic is None else heuristic["do nothing"]
        legal_moves += [DoNothing(self.hand, h)]
        # finding legal moves from devCards
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["knight"]))) > 0:
            # need to check if the cards
            for line in self.board.map:
                for terrain in line:
                    if terrain == self.board.bandit_location:
                        continue
                    for cr in Terrain.get_crossroads((terrain)):
                        destination = cr.get_ownership()
                        if destination is not None and destination != self.index:
                            h = None if heuristic is None else heuristic["use knight"]
                            legal_moves += [UseKnight(self.hand, h, terrain, destination)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["monopole"]))) > 0:
            for r in Resource:
                if r != Resource.DESSERT:
                    h = None if heuristic is None else heuristic["use monopole"]
                    legal_moves += [UseMonopole(self.hand, h, r)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["road builder"]))) > 0:
            for [road1, road2] in self.board.get_two_legal_roads(self.index):
                h = None if heuristic is None else heuristic["use build roads"]
                legal_moves += [UseBuildRoads(self.hand, h, road1, road2)]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["year of prosper"]))) > 0:
            for r1 in Resource:
                if r1 != Resource.DESSERT:
                    for r2 in Resource:
                        if r2 != Resource.DESSERT:
                            h = None if heuristic is None else heuristic["use year of plenty"]
                            legal_moves += [UseYearOfPlenty(self.hand, h, r1, r2)]
        if self.board.hands[self.index].can_buy_road():
            for road in self.board.get_legal_roads(self.index):
                h = None if heuristic is None else heuristic["build road"]
                legal_moves += [BuildRoad(self.hand, h, road)]
        if self.board.hands[self.index].can_buy_settlement():
            for crossword in self.board.get_lands(self.index):
                h = None if heuristic is None else heuristic["build settlement"]
                legal_moves += [BuildSettlement(self.hand, h, crossword)]
        if self.board.hands[self.index].can_buy_city():
            for settlement in self.board.get_settlements(self.index):
                h = None if heuristic is None else heuristic["build city"]
                legal_moves += [BuildCity(self.hand, h, settlement)]
        if self.board.hands[self.index].can_buy_development_card():
            h = None if heuristic is None else heuristic["buy dev card"]
            legal_moves += [BuyDevCard(self.hand, h)]
        for resource in Resource:
            if resource is not Resource.DESSERT:
                can_trade, exchange_rate = self.hand.can_trade(resource, 1)
                if can_trade:
                    for dst in Resource:
                        if dst is not Resource.DESSERT:
                            h = None if heuristic is None else heuristic["trade"]
                            legal_moves += [Trade(self.hand, h, resource, exchange_rate, dst, 1)]
        # ToDo : Add trade between players
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
        actions = self.get_legal_moves(None)
        settlements = []
        cities = []
        roads = []
        trades = []
        buy_development = None
        use_development = []
        for a in actions:
            if isinstance(a, BuildSettlement):
                settlements += [a]
            elif isinstance(a, BuildCity):
                cities += [a]
            elif isinstance(a, BuildRoad):
                roads += [a]
            elif isinstance(a, Trade):
                trades += [a]
            elif isinstance(a, BuyDevCard):
                buy_development = a
            elif isinstance(a, UseDevCard):
                use_development += [a]
        a = None
        if settlements:
            a = best_action(settlements)
        elif cities:
            a = best_action(cities)
        elif roads:
            a = best_action(roads)
        elif use_development:
            a = best_action(use_development)
        elif buy_development:
            a = buy_development
        elif trades:
            a = best_action(trades)
        if a:
            a.do_action()
        return a

    def compute_turn(self):
        return self.simple_choice()


def create_general_heuristic(heuristic):
    return {"do nothing": heuristic,
            "use knight": heuristic,
            "use monopole": heuristic,
            "road builder": heuristic,
            "use build roads": heuristic,
            "use year of plenty": heuristic,
            "build road": heuristic,
            "build settlement": heuristic,
            "build city": heuristic,
            "buy dev card": heuristic,
            "trade": heuristic}


def print_choices(actions: list[Action]):
    types = {}
    if actions:
        print('total points : ' + str(actions[0].points))
    for action in actions:
        if action.name not in types:
            types[action.name] = action
        elif action.heuristic > types[action.name].heuristic:
            types[action.name] = action
    for type, action in types.items():
        print(type + ' : ' + str(action.heuristic))
        show_score_analysis(action.hand)
        print('####################################\n')
#
# Class Fudge(Player)
#     def __init__(self, index, board: Board):
#         super().__init__(index, board, "Dork")
#         self.statistics = StatisticsHeuristic(board.statistics_logger)
#         self.heuristic = create_general_heuristic(hand_heuristic)

class Dork(Player):
    def __init__(self, index, board: Board):
        super().__init__(index, board, "Dork")
        self.statistics = StatisticsHeuristic(board.statistics_logger)
        self.heuristic = create_general_heuristic(hand_heuristic)

    def computer_1st_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        actions = []
        heuristic = hand_heuristic
        for cr in legal_crossroads:
            actions += [BuildFirstSettlement(self.hand, heuristic, cr)]
        baction = take_best_action(actions) # type: BuildFirstSettlement
        actions = []
        cr = baction.crossroad
        # add heuristic for road
        for n in cr.neighbors:
            actions += [BuildFreeRoad(self.hand, heuristic, n.road)]
        take_best_action(actions)

    def computer_2nd_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start()
        actions = []
        heuristic = hand_heuristic
        for cr in legal_crossroads:
            actions += [BuildSecondSettlement(self.hand, heuristic, cr)]
        best_action = take_best_action(actions) # type: BuildSecondSettlement
        actions = []
        cr = best_action.crossroad
        for n in cr.neighbors:
            actions += [BuildFreeRoad(self.hand, heuristic, n.road)]
        take_best_action(actions)

    def simple_choice(self):
        print('\nI am ' + str(self.index) + ' now in simple choice : ')
        actions = self.get_legal_moves(self.heuristic)
        best_action = None  # type: Action
        print_choices(actions)
        for a in actions:
            if best_action is None:
                best_action = a
            elif a.heuristic > best_action.heuristic:
                best_action = a
        if best_action is not None:
            print('   my best action : ')
            print(best_action.name + ' : ' + str(best_action.heuristic))
            best_action.do_action()

    def compute_turn(self):
        self.simple_choice()
