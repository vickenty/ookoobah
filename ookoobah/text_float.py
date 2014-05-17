import pyglet
from pyglet.gl import GL_QUADS

class TextFloat (object):
    def __init__(self, text, x, y, width, font_name=None, font_size=None):
        self.label = pyglet.text.Label(text, x=x, y=y, font_name=font_name, font_size=font_size, multiline=True, width=width, anchor_y = 'top')

        x -= 5
        y += 5
        w = x + self.label.content_width + 10
        h = y - self.label.content_height - 10

        self.vlist = pyglet.graphics.vertex_list(4,
            ('v2f', (x, y, w, y, w, h, x, h)),
            ('c4f', (.2, .2, .2, .4) * 4))

    def draw(self):
        self.vlist.draw(GL_QUADS)
        self.label.draw()

    def delete(self):
        self.vlist.delete()
        self.label.delete()

if __name__ == '__main__':
    import data
    from pyglet.gl import *
    window = pyglet.window.Window()
    tf = TextFloat("Y Helo Thar\n\nThis is long text label maybe with newlines and shit and whatnot and generally very long line", 100, 400, 400)

    glClearColor(.4, .4, .4, 1)
    @window.event
    def on_draw():
        window.clear()
        tf.draw()

    on_draw()
    pyglet.clock.schedule_interval_soft(lambda dt: None, 1/60.)

    pyglet.app.run()
