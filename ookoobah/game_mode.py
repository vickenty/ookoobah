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
import session
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
            return True

    def update_cursor(self, mouse):
        mouse.set_cursor(self.block_class)

class EraseTool (BaseTool):
    def apply(self, pos, grid):
        if grid.get(pos):
            grid[pos] = None
        return True

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
    FPS_FONT_SIZE = 10
    DEFAULT_LEVEL_NAME = "test"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.tool = TriggerTool()

        self.camera = Camera(Vector3(0, 0, 20), Vector3(0, 0, 0), Vector3(0, 1, 0))
        self.camera.resize(0, 0, self.window.width, self.window.height)
        self.init_opengl()
        self.init_gui()

        self.time = 0
        self.next_step = self.STEP_SIZE
        self.fps_magic = pyglet.clock.ClockDisplay(font=pyglet.font.load([], self.FPS_FONT_SIZE))
        self.mouse_pos = (self.window.width / 2, self.window.height / 2)

        self.renderer = None
        self.game_session = None
        level_name = self.get_current_level_name()
        self.load_level(level_name)

    def disconnect(self):
        if self.renderer:
            self.renderer.delete()
        self.shutdown_opengl()

    def init_opengl(self):
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

    def shutdown_opengl(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)

    def init_gui(self):
        build_menu = gui.Submenu([(cls.__name__, gui.SELECT, DrawTool(cls)) for cls in core.ALL_BLOCKS])
        build_menu.choices.append(('Remove', gui.SELECT, EraseTool()))
        file_menu = gui.Submenu([
            ('Save', self.on_save_pressed, ()),
            ('Load', self.on_load_pressed, ())
        ])

        self.gui.replace([
            gui.Button('File', file_menu),
            gui.Button('Build', build_menu),
            gui.Button('Lock', gui.SELECT, LockTool()),
            gui.Button('Reset', self.on_game_reset),
            gui.Button('Back', self.on_back_pressed),
        ])

    def tick(self):
        self.time += 1

        game_status = self.game_session.get_status()

        if self.time > self.SLOW_START and game_status == core.Game.STATUS_NEW:
            self.game_session.start()

        if self.time > self.next_step and game_status == core.Game.STATUS_ON:
            self.game_session.step()
            self.next_step = self.time + self.STEP_SIZE # / (self.game_session.game.speed + 1)

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
            mpos = self.mouse_pos_grid.xy
            if self.tool.apply(mpos, self.game_session.game.grid):
                self.renderer.mark_dirty(mpos)

    def on_game_reset(self, manager, args):
        # TODO There is a similar piece under load_level() and connect(), unify maybe?
        self.time = 0
        self.next_step = self.STEP_SIZE
        self.renderer.delete()
        self.game_session.reset()
        self.renderer.reset(self.game_session.game)
        self.gui.show_popup('Reset')

    def on_back_pressed(self, manager, args):
        # Go back to the main menu (=menu mode),
        # all game state is lost
        self.control.switch_handler("menu_mode")

    def on_save_pressed(self, manager, args):
        level_name = self.get_current_level_name()
        self.save_level(level_name)

    def on_load_pressed(self, manager, args):
        level_name = self.get_current_level_name()
        self.load_level(level_name)

    def get_current_level_name(self):
        return sys.argv[1] if len(sys.argv) == 2 else self.DEFAULT_LEVEL_NAME

    def save_level(self, level_name, *args, **kwargs):
        level_filename = self.get_level_filename(level_name)
        with open(level_filename, 'w+') as level_file:
            pickle.dump(self.game_session.game.grid, level_file)
        self.gui.show_popup('Saved')

    def load_level(self, level_name, *args, **kwargs):
        level_filename = self.get_level_filename(level_name)
        with open(level_filename, 'r') as level_file:
            grid = pickle.load(level_file)
        # TODO There is a similar piece under on_game_reset() and connect(), unify maybe?
        self.time = 0
        self.next_step = self.STEP_SIZE
        self.game_session = session.Session(grid)
        self.renderer = render.GameRenderer(self.game_session.game)
        self.gui.show_popup('Loaded')

    def get_level_filename(self, level_name):
        data_dir = self.get_data_dir()
        return os.path.join(data_dir, level_name + '.level')

    def get_data_dir(self):
        # TODO: pyglet.resource.get_script_home() returns empty string
        game_dir = sys.path[0]
        data_dir = pyglet.resource.path[0]
        return os.path.join(game_dir, data_dir)

    def _create_test_session(self):
        grid = {}
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
        game_session = session.Session(grid)
        return game_session
