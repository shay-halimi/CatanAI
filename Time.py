class Time:
    def __init__(self, turns):
        self.turns = turns
        self.round = 0
        self.turn = 0

    def next_turn(self) -> (int, int):
        if self.turn == self.turns - 1:
            self.turn = 0
            self.round += 1
        else:
            self.turn += 1
        return self.round, self.turn
