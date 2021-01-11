import random


class Die:
    def __init__(self):
        self.number = random.randrange(1, 6)

    def __str__(self):
        return str(self.number)

    def throw(self):
        self.number = random.randrange(1, 6)


class Dice:
    def __init__(self):
        self.die1 = Die()
        self.die2 = Die()
        self.sum = self.die1.number + self.die2.number

    def __str__(self):
        return str(self.sum)

    def throw(self):
        self.die1.throw()
        self.die2.throw()
        self.sum = self.die1.number + self.die2.number


def test_die():
    print("Testing die:")
    die = Die()
    print("   Initial state: " + str(die))
    die.throw()
    print("   After throw: " + str(die))


def test_dice():
    print("Testing Dice:")
    dice = Dice()
    print("   Initial state: first die is " + str(dice.die1) + ", second dice is " + str(dice.die2) + " and the sum is " + str(dice))
    dice.throw()
    print("   Initial state: first dice is " + str(dice.die1) + ", second dice is " + str(dice.die2) + " and the sum is " + str(dice))


test_die()
test_dice()
