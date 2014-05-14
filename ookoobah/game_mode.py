from __future__ import division
import sys
import os
import pyglet
import pickle
from pyglet.gl import *
from pyglet.window import key
from euclid import Vector3
import mode
import core
import render
import gui
import utils
from glutil import *

class GameMode(mode.Mode):
    name = "game_mode"

    STEP_SIZE = 15
    SLOW_START = 120
    DEFAULT_LEVEL_NAME = "test"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.game = self._create_test_game()
        self.renderer = render.GameRenderer(self.game)
        self.current_block_class = None
        self.init_gl()
        self.init_gui()

        self.time = 0
        self.next_step = self.STEP_SIZE
        self.fps_magic = pyglet.clock.ClockDisplay(font=pyglet.font.load([], 16))

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
        buttons.append(gui.Button('Save', self.save_level))
        buttons.append(gui.Button('Load', self.load_level))
        self.gui.replace(buttons)

    def tick(self):
        self.time += 1
        if self.time > self.SLOW_START and not self.game.ball:
            self.game.start()

        if self.time > self.next_step and self.game.ball:
            self.game.step()
            self.next_step = self.time + self.STEP_SIZE # / (self.game.speed + 1)

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

        with gl_disable(GL_LIGHTING, GL_DEPTH_TEST):
            with gl_ortho(self.window):
                self.gui.draw()
                self.fps_magic.draw()

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

    def save_level(self, *args, **kwargs):
        level_filename = self.get_level_filename()
        with open(level_filename, 'w+') as level_file:
            pickle.dump(self.game.grid, level_file)

    def load_level(self, *args, **kwargs):
        level_filename = self.get_level_filename()
        with open(level_filename, 'r') as level_file:
            grid = pickle.load(level_file)
        self.game = core.Game(grid)
        self.renderer.reset(self.game)

    def get_level_filename(self):
        level_name = sys.argv[1] if len(sys.argv) == 2 else self.DEFAULT_LEVEL_NAME
        data_dir = self.get_data_dir()
        return os.path.join(data_dir, level_name + '.level')

    def get_data_dir(self):
        # TODO: pyglet.resource.get_script_home() returns empty string
        game_dir = sys.path[0]
        data_dir = pyglet.resource.path[0]
        return os.path.join(game_dir, data_dir)

    def _create_test_game(self):
        grid = core.Grid()
        grid[2, 0] = core.Launcher()
        grid[4, 0] = core.Mirror()
        grid[4, 3] = core.Mirror(core.Mirror.SLOPE_FORWARD)
        grid[-3, 3] = core.Mirror()
        grid[-3, 0] = core.Mirror(core.Mirror.SLOPE_FORWARD)
        grid[-1, -4] = core.Exit()
        grid[0, -1] = core.FlipFlop()
        grid[-1, 4] = core.Trap()
        grid[0, 4] = core.Trap()
        grid[1, 4] = core.Trap()
        for x in range(-4, 5):
            grid[x, -5] = core.Wall()
            grid[x, 5] = core.Wall()
        for y in range(-4, 5):
            grid[-5, y] = core.Wall()
            grid[5, y] = core.Wall()
        game = core.Game(grid)
        return game
