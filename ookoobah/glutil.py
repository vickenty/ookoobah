from contextlib import contextmanager
from pyglet.gl import *

def ptr(*args):
    return (GLfloat * len(args))(*args)

@contextmanager
def gl_disable(*bits):
    glPushAttrib(GL_ENABLE_BIT)
    map(glDisable, bits)

    yield

    glPopAttrib(GL_ENABLE_BIT)

@contextmanager
def gl_ortho(window):
    # clobbers current modelview matrix
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window.width, 0, window.height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    yield

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
