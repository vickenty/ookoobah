from __future__ import division
import pyglet
from pyglet.gl import *
from pyglet.window import key
import mode
import core
import render
from glutil import *

class GameMode(mode.Mode):
    name = "game_mode"

    # Key constants are defined in pyglet.window.key
    key_2_block_class = {
        key._1: core.Launcher,
        key._2: core.Wall,
        key._3: core.Mirror
    }

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.game = self._create_test_game()
        self.game.start()
        self.renderer = render.GameRenderer(self.game)
        self.init_gl()

        self.modelview = (GLdouble * 16)()
        self.projection = (GLdouble * 16)()
        self.viewport = (GLint * 4)()
        self.unproj = [GLdouble(), GLdouble(), GLdouble()]
        self.mouse_pos = (0, 0)

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

        self.renderer.mouse.pos = map(round, self.unproject(self.mouse_pos))

        self.renderer.draw()

    def unproject(self, (x, y)):
        # NB: magic number is screen-space Z-coordinate (0, 0, 0).Since our
        # levels are flat, it's okay to hard code this, and not call
        # glGetPixels. Works only in strict top-down view.
        gluUnProject(x, y, 0.9969,
            self.modelview,
            self.projection,
            self.viewport,
            self.unproj[0],
            self.unproj[1],
            self.unproj[2]
        )
        return [v.value for v in  self.unproj]

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol in self.key_2_block_class:
            blockClass = self.key_2_block_class[symbol]
            self.renderer.mouse.set_cursor(blockClass)

    def _create_test_game(self):
        game = core.Game()
        game.grid[2, 0] = core.Launcher()
        game.grid[4, 0] = core.Mirror()
        for x in range(-4, 5):
            game.grid[x, -5] = core.Wall()
            game.grid[x, 5] = core.Wall()
        for y in range(-4, 5):
            game.grid[-4, y] = core.Wall()
            game.grid[4, y] = core.Wall()
        return game
