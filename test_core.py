#!/usr/bin/env python

from ookoobah import core
from ookoobah import utils

grid = utils.make_grid_from_string("""
    # # # # # #
    # > . . \ #
    # . # . | #
    # . / | o #
    # . \ . / #
    # # # # # #
""")

game = core.Game(grid=grid)
game.start()

print "hit <enter> to render next; ^C to abort"

status = core.Game.STATUS_ON
while status == core.Game.STATUS_ON:
    print utils.dump_game_to_string(game)
    status = game.step()
    raw_input()

print "game status: %s" % status
