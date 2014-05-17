#!/usr/bin/env python
"""Point of execution for play.

Configures module path and libraries and then calls lib.main.main.

"""

import os
import sys
import getopt

if __name__ == "__main__":
    # Change to the game directory
    sys.path.insert(1, 'pyglet-c9188efc2e30')

    import ookoobah.main
    ookoobah.main.main()
