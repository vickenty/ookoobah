#!/usr/bin/env python
"""Point of execution for play.

Configures module path and libraries and then calls lib.main.main.

"""

import getopt
import os
import sys
import ookoobah.main

def run():
    ookoobah.main.main()

if __name__ == "__main__":
    # Change to the game directory
    os.chdir(os.path.dirname(os.path.join(".", sys.argv[0])))

    # Start the actual game
    run()
