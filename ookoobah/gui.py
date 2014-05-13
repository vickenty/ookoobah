from __future__ import division

import pyglet
from pyglet.window import mouse
from pyglet.gl import *
from euclid import Vector2

DONE = object()
BACK = object()

class Manager (object):
    ANIM_STRIDE = 2
    MARGIN = 20
    SPACING = 25

    def __init__(self, window):
        self.window = window
        self.stack = []
        self.active = []
        self.buttons = []
        self.selected = None

    def replace(self, buttons):
        self.hide(True, True)
        self.stack = []
        self.set_active(buttons)

    def push(self, buttons):
        self.hide()
        self.stack.append(self.active)
        self.set_active(buttons)

    def set_active(self, buttons):
        self.active = list(buttons)
        self.buttons.extend(self.active)
        self.show(True)

    def pop(self):
        self.hide(True)
        self.active = self.stack.pop()
        self.show()

    def hide(self, delete=False, everything=False):
        buttons = self.buttons if everything else self.active

        for idx, btn in enumerate(buttons):
            btn.delay = idx * self.ANIM_STRIDE
            new_x = -btn.width - self.MARGIN if delete else -btn.width + self.MARGIN * (len(self.stack) + 1)
            new_y = btn.pos[1] - self.MARGIN
            btn.target = Vector2(new_x, new_y)
            btn.auto_delete = delete

    def show(self, reset_pos=False):
        offset = 0
        for idx, btn in enumerate(self.active):
            offset -= btn.height + self.SPACING
            btn.delay = idx * self.ANIM_STRIDE
            if reset_pos:
                btn.pos = Vector2(-btn.width - self.MARGIN, offset + self.MARGIN)
            btn.target = Vector2(self.MARGIN * (len(self.stack) + 1), offset)

    def tick(self, dt=None):
        self.buttons = [b for b in self.buttons if b.tick() is not DONE]

    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.window.width, 0, self.window.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, self.window.height, 0)
        [btn.draw() for btn in self.buttons]

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def on_mouse_release(self, x, y, btn, mods):
        if not self.active:
            return
        y -= self.window.height
        if btn == mouse.LEFT:
            if y > self.active[-1].pos.y and x < self.MARGIN * len(self.stack):
                self.pop()
                return

            for obj in self.active:
                if obj.contains(x, y):
                    if self.selected:
                        self.selected.selected(0)
                        self.selected = None

                    if obj.callback is BACK:
                        self.pop()

                    elif obj.callback is None:
                        obj.selected(self.MARGIN)
                        self.selected = obj

                    else:
                        obj.callback(obj)

                    return pyglet.event.EVENT_HANDLED

        elif btn == mouse.RIGHT:
            if self.stack:
                self.pop()
            return pyglet.event.EVENT_HANDLED

class Button (object):
    THRESHOLD = 1
    SPEED = 0.4

    def __init__(self, text, callback):
        self.label = pyglet.text.Label(text)
        self.callback = callback

        w = self.label.content_width
        h = self.label.content_height

        self.width = w + 10
        self.height = h + 5
        
        self.delay = 0
        self.target = Vector2(0, 0)
        self.pos = Vector2(0, 0)
        self.offset = Vector2(0, 0)
        self.auto_delete = False

        self.vlist = pyglet.graphics.vertex_list(8,
            ('v2f', (
                -15, -15, w + 10, -15, w + 15, h + 9, -10, h + 9,
                -10, -10, w + 5, -10, w + 10, h + 4, -5, h + 4,
            )),
            ('c3f', (.1, .1, .1) * 4 + (.2, .2, .2) * 4)
        )

    def tick(self):
        if self.delay > 0:
            self.delay -= 1
            return

        target = self.target + self.offset
        delta = target - self.pos
        if abs(delta) < self.THRESHOLD:
            self.pos = target

            if self.auto_delete:
                self.delete()
                return DONE
        else:
            self.pos += delta * self.SPEED
    
    def draw(self):
        glPushMatrix(GL_MODELVIEW)
        x, y = self.pos
        glTranslatef(x, y, 0)
        self.vlist.draw(GL_QUADS)
        self.label.draw()
        glPopMatrix()

    def delete(self):
        self.label.delete()
        self.vlist.delete()

    def selected(self, offset):
        self.offset.x = offset
        color = (.4, .4, .2) if offset else (.2, .2, .2)
        self.vlist.colors[12:] = color * 4

    def contains(self, x, y):
        px, py = self.pos
        return -10 <= x - px <= self.width and -10 <= y - py <= self.height

if __name__ == '__main__':
    win = pyglet.window.Window(width=640, height=480)
    man = Manager(win)
    txt = [
        ('Spam', (
            ('Spam', (('Eggs', None), ('Bacon', None), ('Spam', None))),
            ('Bacon', None)
        )),
        ('Quit', DONE),
    ]

    def mk_handler(sub):
        if sub is DONE:
            return lambda _: pyglet.app.exit()
        elif sub:
            def handler(_):
                man.push([Button(label, mk_handler(sub2)) for label, sub2 in sub] + [Button('Back', BACK)])
            return handler

    man.replace(Button(t, mk_handler(sub)) for t, sub in txt)

    glClearColor(.3, .3, .3, 1)

    @win.event
    def on_draw():
        win.clear()
        man.draw()
    
    win.push_handlers(man)

    def update(dt):
        man.tick()

    pyglet.clock.schedule_interval_soft(update, 1/60)

    pyglet.app.run()
