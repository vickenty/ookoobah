from copy import deepcopy
import core

class Session(object):
    def __init__(self, grid):
        self.game = core.Game(grid)
        self.original_game = None

    def start(self):
        self.original_game = deepcopy(self.game)
        return self.game.start()

    def reset(self):
        if self.original_game:
            self.game = self.original_game
            self.original_game = None
