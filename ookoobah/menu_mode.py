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

    def disconnect(self):
        pass

    def init_menu(self):
        self.b_fullscreen = gui.Button('Full screen', self.toggle_full_screen)
        buttons = [
            gui.Button('Play', self.on_play_pressed),
            gui.Button('Edit', self.on_edit_pressed),
            self.b_fullscreen,
            gui.Button('Exit', self.on_exit_pressed),
        ]
        self.gui.replace(buttons)

    def toggle_full_screen(self, manager, args):
        fs = self.window.fullscreen
        self.window.set_fullscreen(not fs)
        self.b_fullscreen.label.text = 'Full screen' if fs else 'Windowed'

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
