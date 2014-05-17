from __future__ import division
import sys
import os
import pyglet
import pickle
from pyglet.gl import *
from pyglet.window import key, mouse
from euclid import Vector3
import mode
import core
import session
import render
import gui
from tools import *
from glutil import *
from camera import Camera
from text_float import TextFloat
import sounds

LEVELS = (
    "intro-basics",
    "beginning",
    "intro-trap",
    "shroom",
    "intro-cloud",
    "breadboard",
    "intro-flip-mirror",
    "flip-danger",
    "intro-one-way",
    "regulator",
    "intro-portal",
    "drunk-portals",
    "wall-trick",
    "mine-field",
)

class GameMode(mode.Mode):
    name = "game_mode"

    STEP_SIZE = 15
    SLOW_START = 120
    FPS_FONT_SIZE = 10

    def __init__(self, editor_mode=True, level_name=None):
        super(GameMode, self).__init__()
        self.editor_mode = editor_mode
        self.level_name = level_name

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.tool = TriggerTool()
        self.alt_tool = EraseTool()

        self.init_opengl()

        self.skip_level = False
        self.game_complete = False

        self.fps_magic = pyglet.clock.ClockDisplay(font=pyglet.font.load([], self.FPS_FONT_SIZE))
        self.mouse_pos = (self.window.width / 2, self.window.height / 2)
        self.renderer = None

        if not self.level_name:
            self.level_name = self.get_default_level_name()

        grid, level_help = self.load_grid_from_file(self.level_name)
        self.game_session = session.Session(grid)
        self.game_status = None
        self.level_help = None
        self.charge_player = None

        if level_help and not self.editor_mode:
            level_help += '\n\nClick to continue.\n'
            font = gui.GameMenuFont()
            self.level_help = TextFloat(level_help, 0, -200, 500, font.name, 12)

        self.init_level()
        self.init_renderer()
        self.init_gui()
        self.init_camera()

    def init_camera(self):
        grid = self.game_session.game.grid
        if grid:
            minx = miny = float("Inf")
            maxx = maxy = float("-Inf")
            for x, y in grid:
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x)
                maxy = max(maxy, y)
        else:
            minx = miny = maxx = maxy = 0

        cx = minx + (maxx - minx) / 2
        cy = miny + (maxy - miny) / 2

        self.camera = Camera(Vector3(cx, cy, 20), Vector3(cx, cy, 0), Vector3(0, 1, 0))
        self.camera.resize(0, 0, self.window.width, self.window.height)

    def disconnect(self):
        self.delete_renderer()
        self.shutdown_opengl()

        self.stop_charge_player()

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

    def init_renderer(self):
        self.renderer = render.GameRenderer(self.game_session.game)

    def delete_renderer(self):
        if self.renderer:
            self.renderer.delete()
        self.renderer = None

    def init_gui(self):
        font = gui.GameMenuFont()
        build_menu = gui.Submenu([(cls.human_name, font, gui.SELECT, DrawTool(cls)) for cls in core.ALL_BLOCKS])
        build_menu.choices.append((gui.LABEL_REMOVE, font, gui.SELECT, EraseTool()))

        self.b_start_stop = gui.Button(gui.LABEL_START, font, self.on_game_start_stop)

        if self.editor_mode:
            self.gui.replace([
                gui.Button(u'\u270f Build\u2026', font, build_menu),
                gui.Button(u'\u2798 Save', font, self.on_save_pressed),
                gui.Button(u'\u2744 Lock', font, gui.SELECT, LockTool()),
                self.b_start_stop,
                gui.Button(gui.LABEL_BACK, font, self.on_back_pressed),
            ])
        else:
            self.block_buttons = {
                block_class: gui.CountButton(block_class.human_name, font, count, gui.SELECT, DrawTool(block_class))
                for block_class, count in self.game_session.game.inventory.items()
            }

            block_buttons = [self.block_buttons[cls] for cls in core.ALL_BLOCKS if cls in self.block_buttons]

            self.gui.replace(block_buttons + [
                gui.Button(gui.LABEL_REMOVE, font, gui.SELECT, EraseTool()),
                gui.Button(u'\u21ba Retry', font, self.on_game_reset),
                gui.Button(gui.LABEL_BACK, font, self.on_back_pressed),
            ])

    def tick(self):
        if not self.level_help:
            self.time += 1

        if self.time == 1 and not self.editor_mode:
            self.charge_player = sounds.play('charge.wav')

        new_status = self.game_session.get_status()
        if self.game_status == core.Game.STATUS_ON and new_status == core.Game.STATUS_DEFEAT:
            self.camera.shake(1)
            sounds.play('boom.wav', 0.4)
        self.game_status = new_status

        if not self.editor_mode:
            if new_status == core.Game.STATUS_VICTORY or self.skip_level:
                sounds.play('victory.wav')
                next_level_name = self.level_name if self.editor_mode else self.get_next_level_name()
                if next_level_name:
                    self.control.switch_handler("game_mode", False, next_level_name)
                    return
                elif not self.game_complete:
                    self.gui.show_popup("Congrats! You completed the game!")
                    self.game_complete = True

        if not self.editor_mode and self.time > self.SLOW_START and new_status == core.Game.STATUS_NEW:
            self.game_session.start()
            self.stop_charge_player()
            sounds.play('start.wav')

        if self.time > self.next_step and new_status == core.Game.STATUS_ON:
            self.game_session.step()
            self.next_step = self.time + self.STEP_SIZE # / (self.game_session.game.speed + 1)

        cam_idx = 2 if self.keys[key.LSHIFT] or self.keys[key.RSHIFT] else 1
        cam_pos = self.camera.eye.next_value
        if self.keys[key.UP]:
            cam_pos[cam_idx] += 0.2
        if self.keys[key.DOWN]:
            cam_pos[cam_idx] -= 0.2
        if self.keys[key.LEFT]:
            cam_pos.x -= 0.2
        if self.keys[key.RIGHT]:
            cam_pos.x += 0.2

        cam_pos.x = min(20, max(-20, cam_pos.x))
        cam_pos.y = min(20, max(-20, cam_pos.y))
        cam_pos.z = min(40, max(5, cam_pos.z))

        self.camera.tick()
        self.renderer.tick()

    def stop_charge_player(self):
        if self.charge_player:
            self.charge_player.pause()
            self.charge_player = None

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
                if self.level_help:
                    self.level_help.draw(self.window)

    def update_mouse(self):
        self.mouse_pos_world = self.camera.unproject(self.mouse_pos)
        self.mouse_pos_grid = Vector3(*[int(round(v)) for v in self.mouse_pos_world])
        self.renderer.mouse.pos = self.mouse_pos_grid
        self.tool.update_cursor(self.renderer.mouse)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_key_press(self, sym, mods):
        self.hide_help()
        if sym == key.F12:
            self.skip_level = True
            return pyglet.event.EVENT_HANDLED

    def hide_help(self):
        if self.level_help:
            self.level_help.delete()
            self.level_help = None

    def on_mouse_release(self, x, y, button, modifiers):
        if self.level_help:
            self.hide_help()
            return

        self.mouse_pos = (x, y)
        self.update_mouse()

        mpos = self.mouse_pos_grid.xy
        grid = self.game_session.game.grid
        block = grid.get(mpos)

        if block and block.locked and not self.editor_mode:
            self.camera.shake(0.1)
            sounds.play('noway.wav')
            return

        try:
            if button == mouse.LEFT:
                tool = self.tool
            if button == mouse.RIGHT or (button == mouse.LEFT and modifiers & key.MOD_SHIFT):
                tool = self.alt_tool

            if tool.apply(mpos, self.game_session.game, self.editor_mode):
                self.renderer.mark_dirty(mpos)

        except Exception as e:
            self.camera.shake(0.2)
            sounds.play('noway.wav')

        self.update_inventory()

    def update_inventory(self):
        if not self.editor_mode:
            for cls, count in self.game_session.game.inventory.items():
                self.block_buttons[cls].count = count

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        cam_pos = self.camera.eye.next_value
        cam_pos.z -= scroll_y

    def on_game_start_stop(self, manager, args):
        if self.game_session.get_status() == core.Game.STATUS_NEW:
            try:
                self.game_session.start()
                self.b_start_stop.label.text = gui.LABEL_STOP
            except Exception, e:
                self.gui.show_popup("%s" % e)
                self.init_level()
        else:
            self.init_level()
            self.b_start_stop.label.text = gui.LABEL_START

    def on_game_reset(self, manager, args):
        self.init_level()
        self.update_inventory()
        self.stop_charge_player()

    def on_back_pressed(self, manager, args):
        # Go back to the main menu (=menu mode),
        # all game state is lost
        self.control.switch_handler("menu_mode")

    def on_save_pressed(self, manager, args):
        self.save_level(self.level_name)

    def get_default_level_name(self):
        return sys.argv[1] if len(sys.argv) > 1 else LEVELS[0]

    def get_next_level_name(self):
        # Always stay on the same level if the level was specified on the command line
        if len(sys.argv) > 1:
            return sys.argv[1]

        current_level_index = LEVELS.index(self.level_name)
        if current_level_index >= 0 and current_level_index < len(LEVELS) - 1:
            return LEVELS[current_level_index+1]
        else:
            return None

    def save_level(self, level_name):
        level_filename = self.get_level_filename(level_name)
        with open(level_filename, 'w+') as level_file:
            pickle.dump(self.game_session.game.grid, level_file)
        self.gui.show_popup('Saved')

    def load_grid_from_file(self, level_name):
        grid = {}
        level_filename = self.get_level_filename(level_name)
        try:
            with open(level_filename, 'r') as level_file:
                grid = pickle.load(level_file)
        except IOError:
            if not self.editor_mode:
                raise

        level_help = None
        try:
            with open(level_filename + '.txt', 'r') as f:
                level_help = '\n\n'.join(para.replace('\n', ' ') for para in f.read().split('\n\n'))
        except IOError:
            pass

        level_title = self.level_name.replace("-", " ").title()
        self.gui.show_popup(level_title, color="title")

        return grid, level_help

    def init_level(self):
        self.time = 0
        self.next_step = self.STEP_SIZE
        self.game_session.reset()
        self.game_status = None
        if not self.editor_mode:
            self.game_session.game.build_inventory()

        if self.renderer:
            self.renderer.delete()
        self.renderer = render.GameRenderer(self.game_session.game)

    def get_level_filename(self, level_name):
        data_dir = os.path.join(pyglet.resource.get_script_home(), 'data')
        return os.path.join(data_dir, level_name + '.level')

    def get_data_dir(self):
        return pyglet.resource.path[0]

    def _create_test_grid(self):
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
        return grid
