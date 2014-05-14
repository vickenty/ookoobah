from __future__ import division
import pyglet
from pyglet.gl import *
from pyglet.window import key
from euclid import Vector3
import mode
import core
import render
import gui
from glutil import *

class GameMode(mode.Mode):
    name = "game_mode"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.game = self._create_test_game()
        self.game.start()
        self.renderer = render.GameRenderer(self.game)
        self.current_block_class = None
        self.init_gl()
        self.init_gui()

        self.modelview = (GLdouble * 16)()
        self.projection = (GLdouble * 16)()
        self.viewport = (GLint * 4)()
        self.unproj = [GLdouble(), GLdouble(), GLdouble()]
        self.mouse_pos = (self.window.width / 2, self.window.height / 2)

    def init_gl(self):
        glLoadIdentity()

        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)

        glLightfv(GL_LIGHT0, GL_POSITION, ptr(5, 5, 5, 1))
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, ptr(5, 5, -5, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, ptr(.8, .8, .8, 1))
        glLightfv(GL_LIGHT0, GL_SPECULAR, ptr(.8, .8, .8, 1))

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, ptr(.5, .5, .5, 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, ptr(0, 0, 0, 0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 0)

    def init_gui(self):
        # FIXME: Burn this with fire.
        blocks = (cls for cls in core.__dict__.values() if type(cls) == type and issubclass(cls, core.Block) and cls != core.Block)
        buttons = [gui.Button(cls.__name__, gui.SELECT, cls) for cls in blocks]
        self.gui.replace(buttons)

    def tick(self):
        self.game.step()

    def on_resize(self, w, h):
        glViewport(0, 0, w, h)
        self.viewport[:] = (0, 0, w, h)

        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glu.gluPerspective(45.0, w / h, 0.1, 50)
        glMatrixMode(gl.GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    def on_draw(self):
        self.window.clear()
        glLoadIdentity()
        gluLookAt(0, 0, 20, 0, 0, 0, 0, 1, 0)
        glGetDoublev(GL_MODELVIEW_MATRIX, self.modelview)
        glGetDoublev(GL_PROJECTION_MATRIX, self.projection)

        if self.gui.selected:
            self.current_block_class ,= self.gui.selected.args
        else:
            self.current_block_class = None

        self.renderer.mouse.set_cursor(self.current_block_class)
        self.update_mouse()
        self.renderer.draw()

        glPushAttrib(GL_ENABLE_BIT)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        self.gui.draw()
        glPopAttrib(GL_ENABLE_BIT)

    def update_mouse(self):
        self.mouse_pos_world = self.unproject(self.mouse_pos)
        self.mouse_pos_grid = Vector3(*[int(round(v)) for v in self.mouse_pos_world])
        self.renderer.mouse.pos = self.mouse_pos_grid

    def _unproject(self, x, y, z):
        gluUnProject(x, y, z,
            self.modelview,
            self.projection,
            self.viewport,
            self.unproj[0],
            self.unproj[1],
            self.unproj[2]
        )
        return Vector3(*[v.value for v in self.unproj])

    def unproject(self, (x, y)):
        # http://stackoverflow.com/questions/9406269/object-picking-with-ray-casting
        l0 = self._unproject(x, y, 0.1)
        l1 = self._unproject(x, y, 0.9)
        ld = l1 - l0

        # http://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
        # assuming that p0 = (0, 0, 0), and n = (0, 0, -1)
        d = -l0.z / ld.z
        p = l0 + ld * d

        return p

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_pos = (x, y)
        self.update_mouse()
        self.create_new_block()

    def create_new_block(self):
        if not self.current_block_class:
            return
        pos = self.mouse_pos_grid.xy
        self.game.grid[pos] = self.current_block_class()
        self.renderer.update_grid(pos)

    def _create_test_game(self):
        game = core.Game()
        game.grid[2, 0] = core.Launcher()
        game.grid[4, 0] = core.Mirror()
        game.grid[4, 3] = core.Mirror(core.Mirror.SLOPE_FORWARD)
        game.grid[-3, 3] = core.Mirror()
        game.grid[-3, 0] = core.Mirror(core.Mirror.SLOPE_FORWARD)
        for x in range(-4, 5):
            game.grid[x, -5] = core.Wall()
            game.grid[x, 5] = core.Wall()
        for y in range(-4, 5):
            game.grid[-5, y] = core.Wall()
            game.grid[5, y] = core.Wall()
        return game
