#!/usr/bin/env python
"""Point of execution for play.

Configures module path and libraries and then calls lib.main.main.

"""

import sys
sys.path.insert(0, 'pyglet-c9188efc2e30')

import getopt
import os
import ookoobah.main

def run():
    ookoobah.main.main()

if __name__ == "__main__":
    # Change to the game directory
    os.chdir(os.path.dirname(os.path.join(".", sys.argv[0])))

    # Start the actual game
    run()
