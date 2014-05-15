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
        buttons = [
            gui.Button('Play', self.on_play_pressed),
            gui.Button('Edit', self.on_edit_pressed),
            gui.Button('Exit', self.on_exit_pressed),
        ]
        self.gui.replace(buttons)

    def on_play_pressed(self, manager, args):
        self.control.switch_handler("game_mode")

    def on_edit_pressed(self, manager, args):
        self.control.switch_handler("game_mode")

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
