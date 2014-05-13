from __future__ import division
import pyglet
from pyglet.gl import *
import math

import core
import shapes

class GameRenderer(object):
    """Top level renderer.

    Renders the score and calls all other game object renderers.
    """
    BACKGROUND_COLOR = (0.8862, 0.3215, 0.2784, 1)

    def __init__(self, game):
        self.game = game
        self.batch = pyglet.graphics.Batch()

        #glClearColor(*self.BACKGROUND_COLOR)

        # TODO: render the score and other labels

        # Init the renderers for all game objects
        self.grid_renderer = GridRenderer(game.grid, self.batch)
        self.ball_renderer = BallRenderer(game.ball, self.batch)
        self.mouse = Mouse(self.batch)

    def draw(self):
        # We can draw the batch only after all renderers updated it
        self.batch.draw()

class BlockRenderer (object):
    def __init__(self, batch, group, x, y, block):
        self.shape = shapes.Box(batch, group, (x, y, 0), self.size, self.color)

    def delete(self):
        self.shape.delete()

class Wall (BlockRenderer):
    size = (.9, .9, .9)
    color = (.3, .3, .3)

class Launcher (BlockRenderer):
    size = (.5, .5, .5)
    color = (.5, .1, .1)

class Mirror (BlockRenderer):
    size = (1, 1, .4)
    color = (.1, .9, .9)

class GridRenderer(dict):
    def __init__(self, grid, batch):
        self.grid = grid
        self.batch = batch

        for (x, y), block in self.grid.iteritems():
            blockClass = block.__class__
            self[x, y] = create_block_renderer(blockClass, batch, None, x, y)

class BallGroup (pyglet.graphics.Group):
    def __init__(self, ball, parent=None):
        super(BallGroup, self).__init__(parent)
        self.ball = ball

    def set_state(self):
        glPushMatrix()
        x, y = self.ball.pos
        glTranslatef(x, y, 0)

    def unset_state(self):
        glPopMatrix()

class BallRenderer(object):
    def __init__(self, ball, batch):
        self.group = BallGroup(ball)
        self.shape = shapes.Ico(batch, self.group, (0, 0, 0), (.3, .3, .3), (1, 1, 0))

class FollowGroup (pyglet.graphics.Group):
    def __init__(self, target, parent=None):
        super(FollowGroup, self).__init__(parent)
        self.target = target

    def set_state(self):
        glPushAttrib(GL_POLYGON_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        x, y, z = self.target.pos
        glPushMatrix()
        glTranslatef(x, y, z)

    def unset_state(self):
        glPopMatrix()
        glPopAttrib()

class Mouse (object):
    def __init__(self, batch):
        self.group = FollowGroup(self)
        # We need to cache the batch in order to change shapes on the fly
        self.batch = batch
        self.cursor = None
        self.block_class = None
        self.pos = (0, 0, 0)

    def set_cursor(self, blockClass):
        if self.block_class == blockClass:
            return
        self.block_class = blockClass

        if self.cursor:
            self.cursor.delete()
            self.cursor = None

        if blockClass:
            self.cursor = create_block_renderer(blockClass, self.batch, self.group, 0, 0)

# TODO: move to a better place
def create_block_renderer(blockClass, batch, group, x, y):
    CORE_MAPPING = {
        core.Wall: Wall,
        core.Launcher: Launcher,
        core.Mirror: Mirror
    }
    renderer_class = CORE_MAPPING[blockClass]
    return renderer_class(batch, group, x, y, blockClass)
