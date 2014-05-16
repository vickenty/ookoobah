from __future__ import division

from pyglet.gl import *

from euclid import Vector3
from spring import Spring

class Camera (object):
    SPEED = 0.1
    CLIP  = 0.01
    def __init__(self, eye, center, up):
        self.eye = Spring(eye, self.SPEED, self.CLIP)
        self.vec = Spring(center - eye, self.SPEED, self.CLIP)
        self.up = Spring(up, self.SPEED, self.CLIP)

        self.modelview = (GLdouble * 16)()
        self.projection = (GLdouble * 16)()
        self.viewport = (GLint * 4)()
        self.unproj = [GLdouble(), GLdouble(), GLdouble()]

    def resize(self, x, y, w, h):
        glViewport(x, y, w, h)
        self.viewport[:] = (x, y, w, h)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glu.gluPerspective(45.0, w / h, 0.1, 50)
        glMatrixMode(gl.GL_MODELVIEW)

    def move(self, eye, center, up):
        self.eye.next_value = eye
        self.vec.next_value = center - eye
        self.up.next_value = up

    def tick(self):
        self.eye.tick()
        self.vec.tick()
        self.up.tick()

    def setup(self):
        eye = self.eye.value
        center = eye + self.vec.value
        up = self.up.value
        gluLookAt(eye.x, eye.y, eye.z,
            center.x, center.y, center.z,
            up.x, up.y, up.z)
        glGetDoublev(GL_MODELVIEW_MATRIX, self.modelview)
        glGetDoublev(GL_PROJECTION_MATRIX, self.projection)

    def _unproject(self, x, y, z):
        gluUnProject(x, y, z,
            self.modelview,
            self.projection,
            self.viewport,
            self.unproj[0],
            self.unproj[1],
            self.unproj[2]
        )
        return Vector3(*[v.value for v in self.unproj])

    def unproject(self, (x, y)):
        # http://stackoverflow.com/questions/9406269/object-picking-with-ray-casting
        l0 = self._unproject(x, y, 0.1)
        l1 = self._unproject(x, y, 0.9)
        ld = l1 - l0

        # http://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
        # assuming that p0 = (0, 0, 0), and n = (0, 0, -1)
        d = -l0.z / ld.z
        p = l0 + ld * d

        return p

