from __future__ import division
import sys
import os
import pyglet
from pyglet.gl import *
from pyglet.window import key
import mode
import gui

class MenuMode(mode.Mode):
    name = "menu_mode"

    def connect(self, controller):
        super(MenuMode, self).connect(controller)
        self.init_opengl()
        self.init_menu()
        self.toggle_full_screen(True)

    def disconnect(self):
        pass

    def init_menu(self):
        font = gui.MainMenuFont()
        self.b_fullscreen = gui.Button('I love you!', font, self.on_toggle_full_screen)
        buttons = [
            gui.Button('Play', font, self.on_play_pressed),
            gui.Button('Edit levels', font, self.on_edit_pressed),
            self.b_fullscreen,
            gui.Button('Exit', font, self.on_exit_pressed),
        ]
        self.gui.replace(buttons)

    def on_toggle_full_screen(self, manager, args):
        self.toggle_full_screen()

    def toggle_full_screen(self, is_fs=None):
        if is_fs is None:
            is_fs = not self.window.fullscreen
        self.window.set_fullscreen(is_fs)
        self.b_fullscreen.label.text = 'Full screen' if not is_fs else 'Windowed'

    def on_play_pressed(self, manager, args):
        self.control.switch_handler("game_mode", False)

    def on_edit_pressed(self, manager, args):
        self.control.switch_handler("game_mode", True)

    def on_exit_pressed(self, manager, args):
        sys.exit(0)

    def on_draw(self):
        self.window.clear()
        self.gui.draw()

    def init_opengl(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.window.width, 0, self.window.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
