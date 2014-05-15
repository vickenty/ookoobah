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
from glutil import *
from camera import Camera

class BaseTool (object):
    draw_locks = False
    def update_cursor(self, mouse):
        mouse.set_cursor(None)

class DrawTool (BaseTool):
    def __init__(self, block_class):
        self.block_class = block_class

    def apply(self, pos, grid):
        old = grid.get(pos)
        if old.__class__ == self.block_class:
            old.cycle_states()
        else:
            grid[pos] = self.block_class()

    def update_cursor(self, mouse):
        mouse.set_cursor(self.block_class)

class EraseTool (BaseTool):
    def apply(self, pos, grid):
        grid[pos] = None

class LockTool (BaseTool):
    draw_locks = True
    def apply(self, pos, grid):
        obj = grid.get(pos)
        if obj:
            obj.locked = not obj.locked

class TriggerTool (BaseTool):
    def apply(self, pos, grid):
        if grid.get(pos):
            grid[pos].cycle_states()

class GameMode(mode.Mode):
    name = "game_mode"

    STEP_SIZE = 15
    SLOW_START = 120
    DEFAULT_LEVEL_NAME = "test"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.game = self._create_test_game()
        self.renderer = render.GameRenderer(self.game)
        self.tool = TriggerTool()

        self.camera = Camera(Vector3(0, 0, 20), Vector3(0, 0, 0), Vector3(0, 1, 0))
        self.camera.resize(0, 0, self.window.width, self.window.height)
        self.init_gl()
        self.init_gui()

        self.time = 0
        self.next_step = self.STEP_SIZE
        self.fps_magic = pyglet.clock.ClockDisplay(font=pyglet.font.load([], 16))
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
        build_menu = gui.Submenu([(cls.__name__, gui.SELECT, DrawTool(cls)) for cls in blocks])
        build_menu.choices.append(('Remove', gui.SELECT, EraseTool()))
        build_menu.choices.append(('Lock', gui.SELECT, LockTool()))
        file_menu = gui.Submenu([('Save', self.save_level, ()), ('Load', self.load_level, ())])

        self.gui.replace([
            gui.Button('File', file_menu),
            gui.Button('Build', build_menu),
        ])

    def tick(self):
        self.time += 1
        if self.time > self.SLOW_START and not self.game.ball:
            self.game.start()

        if self.time > self.next_step and self.game.ball:
            self.game.step()
            self.next_step = self.time + self.STEP_SIZE # / (self.game.speed + 1)

        self.camera.tick()
        self.renderer.tick()

    def on_resize(self, w, h):
        self.camera.resize(0, 0, w, h)
        return pyglet.event.EVENT_HANDLED

    def on_draw(self):
        self.window.clear()
        glLoadIdentity()

        self.camera.setup()

        if self.gui.selected:
            self.tool = self.gui.selected.args
        else:
            self.tool = TriggerTool()

        self.update_mouse()

        self.renderer.draw(self.tool.draw_locks)

        with gl_disable(GL_LIGHTING, GL_DEPTH_TEST):
            with gl_ortho(self.window):
                self.gui.draw()
                self.fps_magic.draw()

    def update_mouse(self):
        self.mouse_pos_world = self.camera.unproject(self.mouse_pos)
        self.mouse_pos_grid = Vector3(*[int(round(v)) for v in self.mouse_pos_world])
        self.renderer.mouse.pos = self.mouse_pos_grid
        self.tool.update_cursor(self.renderer.mouse)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_pos = (x, y)
        self.update_mouse()
        if self.tool:
            self.tool.apply(self.mouse_pos_grid.xy, self.game.grid)

    def save_level(self, *args, **kwargs):
        level_filename = self.get_level_filename()
        with open(level_filename, 'w+') as level_file:
            pickle.dump(self.game.grid, level_file)
        self.gui.show_popup('Saved')

    def load_level(self, *args, **kwargs):
        level_filename = self.get_level_filename()
        with open(level_filename, 'r') as level_file:
            grid = pickle.load(level_file)
        self.game = core.Game(grid)
        self.renderer.reset(self.game)
        self.gui.show_popup('Loaded')

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
        grid[4, 0].slope = core.Mirror.SLOPE_BACKWARD
        grid[4, 3] = core.Mirror()
        grid[4, 3].slope = core.Mirror.SLOPE_FORWARD
        grid[-3, 3] = core.Mirror()
        grid[-3, 3].slope = core.Mirror.SLOPE_BACKWARD
        grid[-3, 0] = core.Mirror()
        grid[-3, 0].slope = core.Mirror.SLOPE_FORWARD
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
