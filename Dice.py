import random

ROBBER = 7


class Die:
    def __init__(self):
        self.number = random.randrange(1, 6)

    def __str__(self):
        return str(self.number)

    def throw(self):
        self.number = random.randrange(1, 6)


class Dice:
    def __init__(self):
        self.dice1 = Die()
        self.dice2 = Die()
        self.sum = self.dice1.number + self.dice2.number
        self.number_to_terrain = {}
        for i in range(2, 13):
            self.number_to_terrain[i] = []

    def __str__(self):
        return str(self.sum)

    def throw(self):
        self.dice1.throw()
        self.dice2.throw()
        self.sum = self.dice1.number + self.dice2.number
        if self.sum == 7:
            return []
        return self.number_to_terrain[self.sum]

    def load(self, num):
        self.sum = num
        return self.number_to_terrain[self.sum]


def test_die():
    print("Testing dice:")
    dice = Die()
    print("   Initial state: " + str(dice))
    dice.throw()
    print("   After throw: " + str(dice))
