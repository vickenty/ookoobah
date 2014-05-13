#!/usr/bin/env python

from ookoobah import core
from ookoobah import utils

game = core.Game()

utils.populate_grid_from_string(game.grid, """
    # # # # # #
    # > . . \ #
    # . # . . #
    # . . . . #
    # . \ . / #
    # # # # # #
""")

game.start()
print "hit <enter> to render next; ^C to abort"
while True:
    print utils.dump_game_to_string(game)
    game.step()
    raw_input()
