#!/usr/bin/env python

from ookoobah import core
from ookoobah import session
from ookoobah import utils

grid = utils.make_grid_from_string("""
    # # # # # #
    # > . . \ #
    # . # . | #
    # . / | o #
    # . \ . / #
    # # # # # #
""")

sess = session.Session(grid=grid)
sess.start()

print "<enter> to render next; <r> to reset; ^C to abort"

status = core.Game.STATUS_ON
while status == core.Game.STATUS_ON:
    print utils.dump_game_to_string(sess.game)
    status = sess.game.step()
    if raw_input() == "r":
        sess.reset()
        sess.start()

print "game status: %s" % status
