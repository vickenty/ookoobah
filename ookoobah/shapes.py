from __future__ import division
from euclid import Vector3
from pyglet.gl import GL_TRIANGLES

class Shape (object):
    def __init__(self, batch, group, pos, size, color):
        real = []
        norm = []
        self.size = size
        for face in self.shape:
            a = Vector3(*face[1]) - Vector3(*face[0])
            b = Vector3(*face[2]) - Vector3(*face[0])
            n = a.cross(b).normalize()

            for vert in face:
                real.extend(p + v * s for p, v, s in zip(pos, vert, size))
                norm.extend(n)

        count = len(self.shape) * 3
        self.vlist = batch.add(count, GL_TRIANGLES, group,
            ('v3f', real),
            ('c3f', color * count),
            ('n3f', norm))

    def move_to(self, pos):
        self.vlist.vertices = [p + v * s
            for face in self.shape
            for vert in face
            for p, v, s in zip(pos, vert, self.size)
        ]

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

class Ico (Shape):
    r1 = 0.8506508082
    r2 = 0.5257311120

    coord = [
        (-r1,  r2,   0),
        (-r1, -r2,   0),
        (-r2,   0, -r1),
        (-r2,   0,  r1),
        ( r1, -r2,   0),
        ( r1,  r2,   0),
        ( r2,   0, -r1),
        ( r2,   0,  r1),
        (  0, -r1, -r2),
        (  0, -r1,  r2),
        (  0,  r1, -r2),
        (  0,  r1,  r2),
    ]

    shape = [[coord[idx] for idx in face] for face in [
        (11,  7,  5),
        (11,  5, 10),
        (11, 10,  0),
        (11,  0,  3),
        (11,  3,  7),
        (10,  5,  6),
        (10,  6,  2),
        (10,  2,  0),
        ( 9,  8,  4),
        ( 9,  4,  7),
        ( 9,  7,  3),
        ( 9,  3,  1),
        ( 9,  1,  8),
        ( 8,  1,  2),
        ( 8,  2,  6),
        ( 8,  6,  4),
        ( 7,  4,  5),
        ( 6,  5,  4),
        ( 3,  0,  1),
        ( 2,  1,  0),
    ]]

if __name__ == '__main__':
    import pyglet
    import ctypes
    from pyglet import gl
    import math

    window = pyglet.window.Window(width=640, height=480)
    batch = pyglet.graphics.Batch()

    box = Box(batch, None, (-1.5, -.5, 0), (1, 1, 1), (1, 0, 1))
    pyr = Pyramid(batch, None, (.5, -.5, 0), (1, 1, 1), (1, 1, 0))
    ico = Ico(batch, None, (0, 0, 0), (.5, .5, .5), (1, 1, 1))

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

        box.move_to((math.sin(t[0] / 12) / 2 - 2, -.5, 0))

        batch.draw()

    def update(dt):
        pass

    pyglet.clock.schedule_interval_soft(update, 1/60.)

    pyglet.app.run()
