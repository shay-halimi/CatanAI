from Resources import Resource
from Board import Board
from Board import Crossroad


class Player:
    def __init__(self, index, board: Board, name=None, is_computer=True):
        self.index = index
        self.name = name
        self.is_computer = is_computer
        self.board = board
        self.hand = board.hands[index]

    def get_legal_moves(self):
        # TODO add legal moves by type. i.e move bandit need to come with all the locations you can move
        legal_moves = []
        # finding legal moves from devCards
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["knight"]))) > 0:
            # need to check if the cards
            legal_moves += ["move bandit"]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["monopole"]))) > 0:
            # need to check if the cards
            legal_moves += ["use monopole"]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["road building"]))) > 0:
            # need to check if the cards
            legal_moves += ["build 2 roads"]
        if len(list(filter((lambda x: x.ok_to_use), self.hand.cards["year of plenty"]))) > 0:
            # need to check if the cards
            legal_moves += ["use year of plenty"]
        if self.board.hands[self.index].can_buy_road:
            legal_moves += ["build road"]
        if self.board.hands[self.index].can_buy_settlement:
            legal_moves += ["build settlement"]
        if self.board.hands[self.index].can_buy_city:
            legal_moves += ["build city"]
        if self.board.hands[self.index].can_buy_Devcard:
            legal_moves += ["buy Devcard"]




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
        return cr, cr.roads[0]

    def computer_2nd_settlement(self):
        legal_crossroads = self.board.get_legal_crossroads_start(self.index)
        cr = Crossroad.greatest_crossroad(legal_crossroads)
        return cr, cr.roads[0]
