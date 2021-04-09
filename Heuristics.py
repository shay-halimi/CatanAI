from Board import Board
from Resources import Resource


class SimpleHeuristic:
    def __init__(self, id, board: Board):
        self.id = id
        self.board = board
        self.hand = board.hands[id]

    def need_resource(self, resource, trade):
        do_trade = 0
        if self.hand.resources[resource] < 1:
            if trade.dst is resource:
                do_trade += 1
        if trade.src is resource:
            if self.hand.resources[resource] - trade.amount * 4 < 1:
                do_trade -= 1
        return do_trade

    def accept_trade(self, trade):
        do_trade = 0
        do_trade += self.need_resource(Resource.WOOD, trade)
        do_trade += self.need_resource(Resource.CLAY, trade)
        if self.hand.get_lands():
            do_trade += self.need_resource(Resource.SHEEP, trade)
            do_trade += self.need_resource(Resource.WHEAT, trade)
        return do_trade > 0
