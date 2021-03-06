from __future__ import division
import math
from euclid import Vector3, Matrix4, Point3
from pyglet.gl import GL_TRIANGLES, GL_POINTS, GL_LINES
import random

class Shape (object):
    primitive = GL_TRIANGLES
    do_normals = True
    def __init__(self, batch, group, pos, size, color, rotate=None):
        real = []
        norm = []

        matrix = Matrix4()
        matrix.translate(*pos)
        if rotate:
            matrix.rotate_euler(*rotate)
        matrix.scale(*size)

        self.size = size
        self.vertex_count = 0
        for face in self.shape:
            if self.do_normals:
                a = Vector3(*face[1]) - Vector3(*face[0])
                b = Vector3(*face[2]) - Vector3(*face[0])
                n = a.cross(b).normalize()

            for vert in face:
                self.vertex_count += 1
                real.extend(matrix * Point3(*vert))
                if self.do_normals:
                    norm.extend(n)

        data = [
            ('v3f', real),
            ('c%df' % len(color), color * self.vertex_count)
        ]
        if self.do_normals:
            data.append(('n3f', norm))

        self.vlist = batch.add(self.vertex_count, self.primitive, group, *data)

    def delete(self):
        self.vlist.delete()

    def move_to(self, pos):
        self.vlist.vertices = [p + v * s
            for face in self.shape
            for vert in face
            for p, v, s in zip(pos, vert, self.size)
        ]

    def set_color(self, color):
        self.vlist.colors = color * self.vertex_count

class Box (Shape):
    shape = [
        ((.5, .5, -.5), (.5, -.5, -.5), (-.5, -.5, -.5)),
        ((-.5, -.5, -.5), (-.5, .5, -.5), (.5, .5, -.5)),
        ((-.5, -.5, .5), (.5, -.5, .5), (.5, .5, .5)),
        ((.5, .5, .5), (-.5, .5, .5), (-.5, -.5, .5)),
        ((.5, .5, .5), (.5, .5, -.5), (-.5, .5, -.5)),
        ((-.5, .5, -.5), (-.5, .5, .5), (.5, .5, .5)),
        ((-.5, -.5, -.5), (.5, -.5, -.5), (.5, -.5, .5)),
        ((.5, -.5, .5), (-.5, -.5, .5), (-.5, -.5, -.5)),
        ((-.5, -.5, -.5), (-.5, -.5, .5), (-.5, .5, .5)),
        ((-.5, .5, .5), (-.5, .5, -.5), (-.5, -.5, -.5)),
        ((.5, .5, .5), (.5, -.5, .5), (.5, -.5, -.5)),
        ((.5, -.5, -.5), (.5, .5, -.5), (.5, .5, .5)),
    ]

class Pyramid (Shape):
    shape = [
       ((-.5, .5, -.5), (.5, -.5, -.5), (-.5, -.5, -.5)),
       ((-.5, .5, -.5), (.5, .5, -.5), (.5, -.5, -.5)),
       ((-.5, -.5, -.5), (.5, -.5, -.5), (0, 0, .5)),
       ((.5, -.5, -.5), (.5, .5, -.5), (0, 0, .5)),
       ((.5, .5, -.5), (-.5, .5, -.5), (0, 0, .5)),
       ((-.5, .5, -.5), (-.5, -.5, -.5), (0, 0, .5)),
    ]

def pairwise(seq, loop=True):
    it = iter(seq)
    first = prev = next(it)
    for item in it:
        yield (prev, item)
        prev = item
    if loop:
        yield (prev, first)

def angles(count):
    return (math.pi / 8 * i for i in range(0, count))

class Disc (Shape):
    shape = [
        ((0, 0, 0), p1, p2) for p1, p2 in pairwise((math.cos(phi), math.sin(phi), 0) for phi in angles(16))
    ]

class Cross (Shape):
    shape = [
        ((-.1, -1, 0), (.1, 1, 0), (-.1, 1, 0)),
        ((-.1, -1, 0), (.1, -1, 0), (.1, 1, 0)),
        ((-1, -.1, 0), (1, -.1, 0), (1, .1, 0)),
        ((-1, -.1, 0), (1, .1, 0), (-1, .1, 0))
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

class Arrows (Shape):
    shape = [
        ((-.3, -.5, .1), (-.3, -.3, .1), (-.5, -.3, .1)),
        ((.3, .5, .1), (.3, .3, .1), (.5, .3, .1)),
        ((.3, -.5, .1), (.5, -.3, .1), (.3, -.3, .1)),
        ((-.3, .5, .1), (-.5, .3, .1), (-.3, .3, .1))
    ]

class Cloud (Shape):
    primitive = GL_POINTS
    do_normals = False

    @property
    def shape(self):
        return [
            ((
                random.gauss(0, .25),
                random.gauss(0, .25),
                random.gauss(0, .25)
            ),)
            for _ in range(1000)
        ]

class Pine (Shape):
    shape = [
        ((-.5, .2, 0), (-.5, -.2, 0), (-.2, 0, 0)),
        ((-.15, .2, 0), (-.15, -.2, 0), (.15, 0, 0)),
        ((.2, .2, 0), (.2, -.2, 0), (.5, 0, 0)),
    ]

class Spiral (Shape):
    primitive = GL_LINES
    do_normals = False
    shape = [ (a, b) for a, b in pairwise(((math.cos(phi) * phi / 6, math.sin(phi) * phi / 6, phi / 6) for phi in angles(32)), False) ]

if __name__ == '__main__':
    import pyglet
    import ctypes
    from pyglet import gl
    import math
    from glutil import *

    window = pyglet.window.Window(width=640, height=480)
    batch = pyglet.graphics.Batch()

    box = Box(batch, None, (-1, 0, 0), (1, 1, 1), (1, 0, 1))
    pyr = Pyramid(batch, None, (1, 0, 0), (1, 1, 1), (1, 1, 0))
    ico = Ico(batch, None, (0, 0, 0), (.5, .5, .5), (1, 1, 1))

    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_LIGHT0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_COLOR_MATERIAL)

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
        ico.move_to((0, math.cos(t[0] / 11), 0))
        pyr.move_to((.5, -.5, math.sin(t[0] / 10)))

        batch.draw()

    def update(dt):
        pass

    pyglet.clock.schedule_interval_soft(update, 1/60.)

    pyglet.app.run()
