from __future__ import division
import pyglet
from pyglet.gl import *
import math

import core
import shapes
from euclid import Vector3

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
        self.ball_renderer = None
        self.mouse = Mouse(self.batch)

    def update_ball(self):
        if self.game.ball and not self.ball_renderer:
            self.ball_renderer = BallRenderer(self.game.ball, self.batch)
        elif not self.game.ball and self.ball_renderer:
            self.ball_renderer.delete()
            self.ball_renderer = None

    def draw(self):
        # We can draw the batch only after all renderers updated it
        self.grid_renderer.update()
        self.update_ball()
        self.batch.draw()

    def reset(self, game):
        self.grid_renderer.delete()
        self.grid_renderer = GridRenderer(game.grid, self.batch)

class BlockRenderer (object):
    rotate = None
    shape_class = shapes.Box

    def __init__(self, batch, group, x, y, block):
        self.x = x
        self.y = y
        self.block = block
        self.shape = self.make_shape(batch, group)

    def make_shape(self, batch, group):
        return self.shape_class(batch, group, (self.x, self.y, 0), self.size, tuple(self.color), self.rotate)

    def delete(self):
        self.shape.delete()

    def update(self):
        pass

class Wall (BlockRenderer):
    size = (.9, .9, .9)
    color = (.3, .3, .3)

class Mirror (BlockRenderer):
    size = (.8, .1, .9)
    color = (.1, .9, .9)

    @property
    def rotate(self):
        return (0, math.pi * self.block.slope / 4, 0)

class FlipFlop (BlockRenderer):
    size = (.5, .5, .5)
    shape_class = shapes.Disc

    colors = {
        False: Vector3(.5, .5, .5),
        True: Vector3(.8, .8, .2)
    }

    THRESHOLD = 0.1
    SPEED = 0.1

    def __init__(self, batch, group, x, y, block):
        self.old_is_on = block.is_on
        self.new_color = self.color = self.colors[block.is_on]
        super(FlipFlop, self).__init__(batch, group, x, y, block)

    def update(self):
        if self.old_is_on != self.block.is_on:
            self.new_color = self.colors[self.block.is_on]
            self.old_is_on = self.block.is_on

        delta = self.new_color - self.color
        if abs(delta) < self.THRESHOLD:
            self.color = self.new_color.copy()
        else:
            self.color += delta * self.SPEED

        self.shape.set_color(tuple(self.color))

class ScalerGroup (pyglet.graphics.Group):
    def __init__(self, x, y, parent=None):
        super(ScalerGroup, self).__init__(parent)
        self.offset = x, y, 0

    def set_state(self):
        glPushMatrix()
        glTranslatef(*self.offset)
        glScalef(1/20, 1/20, 1/20)

    def unset_state(self):
        glPopMatrix()

class GenericRenderer (BlockRenderer):
    def __init__(self, batch, group, x, y, block):
        self.block = block
        self.shape = pyglet.text.Label(block.__class__.__name__[0],
                batch=batch, anchor_x='center', anchor_y='center',
                group=ScalerGroup(x, y, parent=group))

class GridRenderer(dict):
    def __init__(self, grid, batch):
        self.grid = grid
        self.batch = batch
        self.update(True)

    def update(self, force=False):
        if force == True:
            for pos in  self.grid:
                self[pos] = create_block_renderer(self.grid[pos], self.batch, None, pos[0], pos[1])
        else:
            for pos in self.grid.get_dirty():
                old = self.get(pos)
                if old:
                    old.delete()
                self[pos] = create_block_renderer(self.grid[pos], self.batch, None, pos[0], pos[1])

    def delete(self):
        for renderer in self.values():
            renderer.delete()

        [r.update() for r in self.itervalues()]

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

    def delete(self):
        self.shape.delete()

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

        if self.block_class:
            block = self.block_class()
            self.cursor = create_block_renderer(block, self.batch, self.group, 0, 0)

CORE_MAPPING = {
    core.Wall: Wall,
    core.Mirror: Mirror,
    core.FlipFlop: FlipFlop,
}

# TODO: move to a better place
def create_block_renderer(block, batch, group, x, y):
    renderer_class = CORE_MAPPING.get(block.__class__, GenericRenderer)
    return renderer_class(batch, group, x, y, block)
