import math


class MiniMax:

    def __init__(self, game_tree):
        self.game_tree = game_tree
        self.root = game_tree.root
        self.currentNode = None
        self.successors = []

    def minimax(self, node):
        best_val = self.max_value(node)
        successors = self.getSuccessors(node)
        print("heuristic Value of Root Node: = " + str(best_val))
        # find the node with our best move
        best_move = None
        for elem in successors:  # —> Need to propagate values up tree for this to work
            if elem.heuristic == best_val:
                best_move = elem
                break
        return best_move

    def max_value(self, node):
        print("Visited Node " + node.Name)
        if self.isTerminal(node):
            return self.getheuristic(node)
        max_value = -math.inf
        successors_states = self.getSuccessors(node)
        for state in successors_states:
            max_value = max(max_value, self.min_value(state))
        return max_value

    def min_value(self, node):
        print(" Visited Node  " + node.Name)
        if self.isTerminal(node):
            return self.getheuristic(node)
        min_value = math.inf
        successor_states = self.getSuccessors(node)
        for state in successor_states:
            min_value = min(min_value, self.max_value(state))
        return min_value

    #   UTILITY METHODS   #

    # successor states in a game tree are the child nodes…
    def getSuccessors(self, node):
        assert node is not None
        return node.children

    # a function that checks if we arrived at a final game node
    # return true if the node has NO children (successor states)
    # return false if the node has children (successor states)
    def isTerminal(self, node):
        assert node is not None
        return len(node.children) == 0

    def getheuristic(self, node):
        assert node is not None
        return node.heuristic
