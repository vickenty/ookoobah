from __future__ import division
from euclid import Vector3
from pyglet.gl import GL_TRIANGLES

class Shape (object):
    def __init__(self, batch, group, pos, size, color):
        real = []
        norm = []
        for face in self.shape:
            a = Vector3(*face[1]) - Vector3(*face[0])
            b = Vector3(*face[2]) - Vector3(*face[0])
            n = a.cross(b).normalize()
            print n
            for vert in face:
                real.extend(pos + Vector3(*vert) * size)
                norm.extend(n)

        count = len(self.shape) * 3
        self.vlist = batch.add(count, GL_TRIANGLES, group,
            ('v3f', real),
            ('c3f', color * count),
            ('n3f', norm))

class Box (Shape):
    shape = [
        ((1, 1, 0), (1, 0, 0), (0, 0, 0)),
        ((0, 0, 0), (0, 1, 0), (1, 1, 0)),
        ((0, 0, 1), (1, 0, 1), (1, 1, 1)),
        ((1, 1, 1), (0, 1, 1), (0, 0, 1)),
        ((1, 1, 1), (1, 1, 0), (0, 1, 0)),
        ((0, 1, 0), (0, 1, 1), (1, 1, 1)),
        ((0, 0, 0), (1, 0, 0), (1, 0, 1)),
        ((1, 0, 1), (0, 0, 1), (0, 0, 0)),
        ((0, 0, 0), (0, 0, 1), (0, 1, 1)),
        ((0, 1, 1), (0, 1, 0), (0, 0, 0)),
        ((1, 1, 1), (1, 0, 1), (1, 0, 0)),
        ((1, 0, 0), (1, 1, 0), (1, 1, 1)),
    ]

class Pyramid (Shape):
    shape = [
       ((0, 1, 0), (1, 0, 0), (0, 0, 0)),
       ((0, 1, 0), (1, 1, 0), (1, 0, 0)),
       ((0, 0, 0), (1, 0, 0), (.5, .5, 1)),
       ((1, 0, 0), (1, 1, 0), (.5, .5, 1)),
       ((1, 1, 0), (0, 1, 0), (.5, .5, 1)),
       ((0, 1, 0), (0, 0, 0), (.5, .5, 1)),
    ]

if __name__ == '__main__':
    import pyglet
    import ctypes
    from pyglet import gl
    window = pyglet.window.Window(width=640, height=480)
    batch = pyglet.graphics.Batch()

    Box(batch, None, Vector3(-1.5, -1.5, 0), Vector3(1, 1, 1), (1, 0, 1))
    Pyramid(batch, None, Vector3(.5, .5, 0), Vector3(1, 1, 1), (1, 1, 0))

    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_LIGHT0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_COLOR_MATERIAL)

    def ptr(*args):
        return (gl.GLfloat * len(args))(*args)

    gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, ptr(1, 1, 1, 1))
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, ptr(1, 1, 1, 1))

    gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, ptr(.5, .5, .5, 1))
    gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_SPECULAR, ptr(1, 1, 1, 1))
    gl.glMaterialf(gl.GL_FRONT_AND_BACK, gl.GL_SHININESS, 50)

    @window.event
    def on_resize(w, h):
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glu.gluPerspective(45.0, w / h, 0.1, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    @window.event
    def on_draw(t=[0]):
        t[0] += 2
        window.clear()
        gl.glLoadIdentity()
        gl.glu.gluLookAt(5, 5, 5, 0, 0, 0, 0, 0, 1)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, ptr(5, 0, 5, 1))
        gl.glRotatef(t[0], 0, 0, 1)
        batch.draw()

    def update(dt):
        pass

    pyglet.clock.schedule_interval_soft(update, 1/60.)

    pyglet.app.run()
