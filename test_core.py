#!/usr/bin/env python

from ookoobah import core
from ookoobah import utils

game = core.Game()

utils.populate_grid_from_string(game.grid, """
    ######
    #>..\#
    #.#..#
    #....#
    #.\./#
    ######
""")

game.start()
for n in range(10):
    print utils.dump_grid_to_string(game.grid, game.ball)
    game.step()
