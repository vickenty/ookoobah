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

    @property
    def full_screen_label(self):
        return 'Exit full screen' if self.window.fullscreen else 'Fullscreen'

    def init_menu(self):
        font = gui.MainMenuFont()
        font2 = gui.GameMenuFont()
        self.b_fullscreen = gui.Button(self.full_screen_label, font2, self.on_toggle_full_screen)

        buttons = []
        if len(sys.argv) > 1:
            buttons.append(gui.Button('Play', font, self.on_play_pressed))
            buttons.append(gui.Button('Edit', font, self.on_edit_pressed))
        else:
            buttons.append(gui.Button('New game', font, self.on_play_pressed))
            #buttons.append(gui.Button('Continue', font, self.on_play_pressed))
        buttons.append(self.b_fullscreen)
        buttons.append(gui.Button('Exit', font2, self.on_exit_pressed))
        self.gui.replace(buttons)

    def on_toggle_full_screen(self, manager, args):
        self.toggle_full_screen()

    def toggle_full_screen(self):
        self.window.set_fullscreen(not self.window.fullscreen)
        self.window.set_minimum_size(800, 600)
        self.b_fullscreen.label.text = self.full_screen_label

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
