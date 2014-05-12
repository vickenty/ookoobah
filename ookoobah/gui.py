from __future__ import division

import pyglet
from pyglet.gl import *
from euclid import Vector2

class Button (object):
    THRESHOLD = 0.01
    SPEED = 0.2

    def __init__(self, delay, pos, text):
        self.label = pyglet.text.Label(text)
        w = self.label.content_width
        h = self.label.content_height
        
        self.delay = delay
        self.target = pos
        self.pos = (-self.label.content_width - 40, pos[1])
        self.vlist = pyglet.graphics.vertex_list(8,
                ('v2f', (
                    -15, -15, w + 15, -15, w + 15, h + 9, -15, h + 9,
                    -10, -10, w + 10, -10, w + 10, h + 4, -10, h + 4,
                )),
                ('c3f', (.1, .1, .1) * 4 + (.2, .2, .2) * 4))

    def think(self):
        if self.delay > 0:
            self.delay -= 1
            return

        delta = self.target - self.pos
        if abs(delta) < self.THRESHOLD:
            self.pos = self.target
        else:
            self.pos += delta * self.SPEED
    
    def draw(self):
        glPushMatrix(GL_MODELVIEW)
        x, y = self.pos
        glTranslatef(x, y, 0)
        self.vlist.draw(GL_QUADS)
        self.label.draw()
        glPopMatrix()

if __name__ == '__main__':
    win = pyglet.window.Window(width=640, height=480)
    txt = [ 'Spam', 'Spam, Spam', 'Eggs', 'Bacon' ]
    btn = [Button(i * 5, Vector2(win.width - 150, 300 - (i + 1) * 60), t) for i, t in enumerate(txt)]

    glClearColor(.3, .3, .3, 1)

    @win.event
    def on_draw():
        win.clear()
        [b.draw() for b in btn]
    
    @win.event
    def on_mouse_release(x, y, btn, mods):
        print x, y, btn, mods

    def update(dt):
        [b.think() for b in btn]

    pyglet.clock.schedule_interval_soft(update, 1/60)

    pyglet.app.run()
