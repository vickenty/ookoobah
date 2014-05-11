#!/usr/bin/env python

from ookoobah import core
from ookoobah import level

game = core.Game()

game.grid[0, 0] = core.Launcher()
game.grid[2, 0] = core.Mirror()
game.grid[3, 0] = core.Wall()

game.start()
for n in range(10):
    print game.ball
    game.step()
