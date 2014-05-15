"""Data loaders.

Add functions here to load specific types of resources.

"""

from __future__ import division

import os

from pyglet import resource

resource.path = [ os.path.join('..', 'data') ]
resource.reindex()
