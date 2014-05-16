from __future__ import division
import pyglet
from pyglet.gl import *
import math

import core
import shapes
from spring import Spring
from euclid import Vector3
from glutil import *

class GameRenderer(object):
    """Top level renderer.

    Renders the score and calls all other game object renderers.
    """
    BACKGROUND_COLOR = (0.8862, 0.3215, 0.2784, 1)

    def __init__(self, game):
        self.game = game
        self.batch = pyglet.graphics.Batch()

        # TODO: render the score and other labels

        # Init the renderers for all game objects
        self.grid_renderer = GridRenderer(game.grid, self.batch)
        self.ball_renderer = None
        self.lock_renderer = LockRenderer()
        self.mouse = Mouse(self.batch)

    def update_ball(self):
        if self.game.ball and not self.ball_renderer:
            self.ball_renderer = BallRenderer(self.game.ball, self.batch)
        elif not self.game.ball and self.ball_renderer:
            self.ball_renderer.delete()
            self.ball_renderer = None

    def tick(self):
        if self.ball_renderer:
            self.ball_renderer.update()
        self.grid_renderer.update()
        self.update_ball()

    def draw(self, show_locks):
        # We can draw the batch only after all renderers updated it
        self.batch.draw()
        if show_locks:
            self.lock_renderer.draw(self.game.grid)

    def delete(self):
        if self.ball_renderer:
            self.ball_renderer.delete()
            self.ball_renderer = None
        if self.grid_renderer:
            self.grid_renderer.delete()
            self.grid_renderer = None

    def reset(self, game):
        self.delete()
        self.game = game
        self.grid_renderer = GridRenderer(game.grid, self.batch)

    def mark_dirty(self, pos):
        self.grid_renderer.dirty.append(pos)

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

class RotateGroup (pyglet.graphics.Group):
    def __init__(self, x, y, angle, parent=None):
        super(RotateGroup, self).__init__(parent)
        self.x = x
        self.y = y
        self.angle = angle

    def set_state(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0, 0, 1)

    def unset_state(self):
        glPopMatrix()

class Mirror (BlockRenderer):
    size = (.8, .1, .9)
    color = (.1, .9, .9)

    def __init__(self, batch, group, x, y, block):
        group = RotateGroup(x, y, block.slope, parent=group)
        super(Mirror, self).__init__(batch, group, 0, 0, block)

        self.group = group
        self.slope = Spring(block.slope, 0.2, 0.1)

    def update(self):
        self.slope.next_value = self.block.slope
        self.slope.tick()
        self.group.angle = 45 * self.slope.value

class FlipFlopMirror (Mirror):
    color = (.2, .5, .9)

class Launcher (BlockRenderer):
    size = (.4, .4, .8)
    color = hex_color_f("4D77CB")
    rotate = (math.pi / 2, 0, 0)
    shape_class = shapes.Pyramid

    def __init__(self, batch, group, x, y, block):
        group = RotateGroup(x, y, block.all_states_idx, parent=group)
        super(Launcher, self).__init__(batch, group, 0, 0, block)

        self.group = group
        self.state = Spring(block.all_states_idx, 0.2, 0.1)

    def update(self):
        self.state.next_value = self.block.all_states_idx
        self.state.tick()
        self.group.angle = 90 * self.state.value

class Trap (BlockRenderer):
    size = (.4, .4, .4)
    color = (0.743, 0.29, 0.251)
    rotate = (0, math.pi/4, 0)
    shape_class = shapes.Cross

class FlipFlop (BlockRenderer):
    size = (.3, .3, .3)
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
        self.dirty = []
        self.update(True)

    def update(self, force=False):
        items = self.grid if force else self.dirty
        self.dirty = []

        for pos in items:
            old = self.get(pos)
            if old:
                old.delete()

            if self.grid.get(pos):
                self[pos] = create_block_renderer(self.grid[pos], self.batch, None, *pos)
            elif pos in self:
                del self[pos]

        [r.update() for r in self.itervalues()]

    def delete(self):
        for renderer in self.values():
            renderer.delete()

class LockRenderer (object):
    def __init__(self):
        self.sprite = pyglet.graphics.vertex_list(4,
            ('v3f', (-.4, -.4, 0, .4, -.4, 0, .4, .4, 0, -.4, .4, 0)),
            ('c4f', (.8, 0, 0, .5) * 4)
        )

    def draw(self, grid):
        for (x, y), block in grid.iteritems():
            if not block.locked:
                continue
            glPushMatrix()
            glTranslatef(x, y, 1.1)
            self.sprite.draw(GL_QUADS)
            glPopMatrix()

class BallGroup (pyglet.graphics.Group):
    def __init__(self, renderer, parent=None):
        super(BallGroup, self).__init__(parent)
        self.renderer = renderer

    def set_state(self):
        glPushMatrix()
        glTranslatef(*self.renderer.pos)

        s = max(0, self.renderer.size)

        glScalef(s, s, s)

    def unset_state(self):
        glPopMatrix()

class BallRenderer(object):
    SPEED = 0.02

    def __init__(self, ball, batch):
        self.ball = ball

        self.group = BallGroup(self)
        self.shape = shapes.Ico(batch, self.group, (0, 0, 0), (.2, .2, .2), (1, 1, 0))

        self.old_pos = None
        self.old_dir = None
        self.update()

    def update(self):
        if self.old_pos != self.ball.pos or self.old_dir != self.ball.direction:
            self.old_pos = self.ball.pos
            self.old_dir = self.ball.direction

            self.frame = 0
            x, y = self.ball.pos
            self.pos = Vector3(x, y, 0)

            dx, dy = self.ball.direction
            self.vel = Vector3(dx, dy, 0) * self.SPEED
        else:
            self.frame += 1
            self.pos += self.vel

        self.size = 1 - self.frame / 20 + (self.frame % 5) / 50

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
    core.FlipFlopMirror: FlipFlopMirror,
    core.FlipFlop: FlipFlop,
    core.Trap: Trap,
    core.Launcher: Launcher,
}

# TODO: move to a better place
def create_block_renderer(block, batch, group, x, y):
    renderer_class = CORE_MAPPING.get(block.__class__, GenericRenderer)
    return renderer_class(batch, group, x, y, block)
