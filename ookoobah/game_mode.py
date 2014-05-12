import pyglet
from pyglet.gl import *
import mode
import core
import render
from glutil import *

class GameMode(mode.Mode):
    name = "game_mode"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.game = self._create_test_game()
        self.game.start()
        self.renderer = render.GameRenderer(self.game)
        self.init_gl()

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
        print self.game.ball

    def on_resize(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glu.gluPerspective(45.0, w / h, 0.1, 1000)
        glMatrixMode(gl.GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    def on_draw(self):
        self.window.clear()
        glLoadIdentity()
        gluLookAt(0, 0, 20, 0, 0, 0, 0, 1, 0)
        self.renderer.draw()

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
