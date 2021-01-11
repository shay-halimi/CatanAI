import random
import Board


ROBBER = 7


class Die:
    def __init__(self):
        self.number = random.randrange(1, 6)

    def __str__(self):
        return str(self.number)

    def throw(self):
        self.number = random.randrange(1, 6)


class Dice:
    def __init__(self, board: Board.Board):
        self.board = board
        self.dice1 = Die()
        self.dice2 = Die()
        self.sum = self.dice1.number + self.dice2.number
        self.number_to_terrain = {2: {(0, 3)}, 3: {(2, 3), (3, 1)}, 4: {(1, 3), (3, 2)}, 5: {(3, 3), (4, 0)},
                                  6: {(1, 2), (4, 1)}, 7: {}, 8: {(2, 4), (0, 3)}, 9: {(0, 4), (2, 0)},
                                  10: {(1, 4), (0, 2)}, 11: {(2, 1), (4, 2)}, 12: {(1, 1)}}

    def __str__(self):
        return str(self.sum)

    def throw(self):
        self.dice1.throw()
        self.dice2.throw()
        self.sum = self.dice1.number + self.dice2.number
        if sum == ROBBER:
            self.robber()
        else:
            for index in self.number_to_terrain[self.sum]:
                terrain = self.board.map[index[0]][index[1]]
                terrain.produce()

    def robber(self):
        pass  # ToDo: robber should activate a robber.


def test_die():
    print("Testing dice:")
    dice = Die()
    print("   Initial state: " + str(dice))
    dice.throw()
    print("   After throw: " + str(dice))


def test_dice():
    print("Testing Dices:")
    board = Board.Board()
    dice = Dice(board)
    print("   Initial state: first dice is " + str(dice.dice1) + ", second dice is " + str(
        dice.dice2) + " and the sum is " + str(dice))
    dice.throw()
    print("   After throw: first dice is " + str(dice.dice1) + ", second dice is " + str(
        dice.dice2) + " and the sum is " + str(dice))


test_die()
test_dice()
