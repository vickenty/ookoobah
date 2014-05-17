from __future__ import division

from collections import deque

import pyglet
from pyglet import font
from pyglet.window import mouse, key
from pyglet.gl import *
from euclid import Vector2
from spring import Spring

DONE = object()
BACK = object()
SELECT = object()

LABEL_BACK = u'\u276e Back'
LABEL_REMOVE = u'\u2716 Remove'
LABEL_START = u'\u25b6 Start'
LABEL_STOP = u'\u25a0 Stop'

LOADED_FONTS = {}

class Font(object):
    name = None
    filename = None
    size = None

    def __init__(self):
        if not self.filename in LOADED_FONTS:
            pyglet.resource.add_font(self.filename)
            LOADED_FONTS[self.filename] = 1

class MainMenuFont(Font):
    name = "DejaVu Sans Light"
    filename = 'DejaVuSans-ExtraLight.ttf'
    size = 24
    height = 32

class GameMenuFont(Font):
    name = "DejaVu Sans"
    filename = 'DejaVuSans.ttf'
    size = 10
    height = 16

class PopupFont(Font):
    name = "DejaVu Sans"
    filename = 'DejaVuSans.ttf'
    size = 20
    height = 20

class Manager (object):
    ANIM_STRIDE = 2
    MARGIN = 20
    SPACING = 25

    colors = {
        'okay': (0x34, 0xB2, 0x7D, 0xFF),
    }

    def __init__(self, window):
        self.window = window
        self.stack = []
        self.active = []
        self.buttons = []
        self.selected = None
        self.popup = None
        self.popup_queue = deque()

    def show_popup(self, text, color='okay'):
        color = self.colors[color]
        self.popup_queue.append((text, color))

    def replace(self, buttons):
        self.hide(True, True)
        self.stack = []
        self.set_active(buttons)

    def push(self, buttons, add_back=True):
        self.hide()
        self.stack.append(self.active)
        if add_back:
            buttons += [ Button(LABEL_BACK, GameMenuFont(), BACK) ]
        self.set_active(buttons)

    def set_active(self, buttons):
        self.active = list(buttons)
        self.buttons.extend(self.active)
        self.show(True)

    def pop(self):
        self.hide(True)
        self.selected = None
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

        if self.popup and self.popup.tick() is DONE:
            self.popup = None

        if not self.popup and self.popup_queue:
            text, color = self.popup_queue.popleft()
            self.popup = Popup(text, color)

    def draw(self):
        glPushMatrix()
        glTranslatef(0, self.window.height, 0)
        [btn.draw() for btn in self.buttons]
        glPopMatrix()

        if self.popup:
            self.popup.draw(self.window)

    def on_mouse_release(self, x, y, btn, mods):
        if not self.active:
            return
        y -= self.window.height
        if btn == mouse.LEFT:
            if y > self.active[-1].pos.y and x < self.MARGIN * len(self.stack):
                self.pop()
                return pyglet.event.EVENT_HANDLED

            for obj in self.active:
                if obj.contains(x, y):
                    self.handle_click(obj)

    def handle_click(self, obj):
        old_selected = self.selected
        if self.selected:
            self.selected.selected(0)
            self.selected = None

        # Second click removes selection and that's it.
        if old_selected == obj:
            return pyglet.event.EVENT_HANDLED

        if callable(obj.callback):
            ret = obj.callback(self, obj.args)
        else:
            ret = obj.callback

        if ret is BACK:
            self.pop()

        elif ret is SELECT:
            obj.selected(self.MARGIN)
            self.selected = obj

        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, sym, mod):
        if key._0 <= sym <= key._9:
            ofs = sym - key._0
            ofs = (ofs - 1) % 10

            if ofs < len(self.active):
                self.handle_click(self.active[ofs])

        if sym == key.ESCAPE:
            if self.stack:
                self.pop()
            if self.selected:
                self.selected.selected(0)
                self.selected = None
            return pyglet.event.EVENT_HANDLED

class Button (object):
    THRESHOLD = 1
    SPEED = 0.4

    def __init__(self, text, font, callback, args=None, color=None):
        self.label = pyglet.text.Label(
            text,
            font_name = font.name,
            font_size = font.size,
            anchor_y = 'baseline'
        )
        self.callback = callback
        self.args = args

        w = self.label.content_width
        h = font.height

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

class CountButton (Button):
    THRESHOLD = 1
    SPEED = 0.4

    def __init__(self, text, font, count, callback, args=None, color=None):
        self._text = text
        self._count = count
        super(CountButton, self).__init__(self.text_count, font, callback, args, color)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.label.text = self.text_count

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value
        self.label.text = self.text_count

    @property
    def text_count(self):
        return u'%s \u00d7 %d' % (self._text, self._count)

class Submenu (object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, manager, args):
        buttons = self.build()
        manager.push(buttons)

    def build(self):
        return [Button(label, font, callback, args) for label, font, callback, args in self.choices]

class Popup (object):
    SPEED = 0.2
    SNAP = 0.001
    SLEEP = 60
    POS_Y = 0.3

    def __init__(self, text, color):
        font = PopupFont()
        self.label = pyglet.text.Label(
            text,
            anchor_x = 'center',
            font_name = font.name,
            font_size = font.size,
            anchor_y = 'baseline',
            color = color
        )
        self.offset = Spring(Vector2(1.5, self.POS_Y), self.SPEED, self.SNAP)
        self.offset.next_value = Vector2(.5, self.POS_Y)
        self.sleep = self.SLEEP
        self.done = False

    def tick(self):
        self.offset.tick()
        if self.offset.static:
            if self.done:
                self.label.delete()
                return DONE

            if self.sleep > 0:
                self.sleep -= 1
            else:
                self.offset.next_value = Vector2(-.5, self.POS_Y)
                self.done = True

    def draw(self, window):
        x, y = self.offset.value.xy
        glPushMatrix()
        glTranslatef(x * window.width, y * window.height, 0)
        self.label.draw()
        glPopMatrix()

if __name__ == '__main__':
    win = pyglet.window.Window(width=640, height=480)
    man = Manager(win)
    txt = [
        ('Spam', (
            ('Spam', (('Eggs', SELECT), ('Bacon', SELECT), ('Spam', SELECT))),
            ('Bacon', SELECT)
        )),
        ('Welcome', lambda man, args: man.show_popup('Welcome')),
        ('Quit', DONE),
    ]

    def mk_handler(sub):
        if sub is DONE:
            return lambda man, args: pyglet.app.exit()
        elif sub is SELECT:
            return sub
        elif callable(sub):
            return sub
        elif sub:
            def handler(manager, args):
                manager.push([Button(label, mk_handler(sub2)) for label, sub2 in sub])
            return handler

    font = GameMenuFont()
    man.replace(CountButton(t, font, 15, mk_handler(sub)) for t, sub in txt)

    glClearColor(.3, .3, .3, 1)

    @win.event
    def on_draw():
        win.clear()
        man.draw()

    win.push_handlers(man)

    def update(dt):
        man.tick()
        man.active[0].count += 1

    pyglet.clock.schedule_interval_soft(update, 1/60)

    pyglet.app.run()
