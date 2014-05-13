#!/usr/bin/env python

from ookoobah import core
from ookoobah import utils

game = core.Game()
utils.populate_grid_from_string(game.grid, """
    # # # # # #
    # > . . \ #
    # . # . . #
    # . o . . #
    # . \ . / #
    # # # # # #
""")
game.start()

print "hit <enter> to render next; ^C to abort"

status = core.Game.STATUS_ON
while status == core.Game.STATUS_ON:
    print utils.dump_game_to_string(game)
    status = game.step()
    raw_input()

print utils.dump_game_to_string(game)
print "game status: %s" % game.get_status()
