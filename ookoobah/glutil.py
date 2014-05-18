from __future__ import division
from contextlib import contextmanager
from pyglet.gl import *

__all__ = [
    'ptr',
    'gl_disable',
    'gl_ortho',
    'hex_color_i',
    'hex_color_f',
]

def ptr(*args):
    return (GLfloat * len(args))(*args)

@contextmanager
def gl_disable(*bits):
    glPushAttrib(GL_ENABLE_BIT)
    map(glDisable, bits)

    yield

    glPopAttrib()

@contextmanager
def gl_ortho(window):
    # clobbers current modelview matrix
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window.width, 0, window.height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    yield

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def hex_color_i(value):
    return tuple(int(value[i:i+2], 16) for i in range(0, len(value), 2))

def hex_color_f(value):
    return tuple(v / 255 for v in hex_color_i(value))

