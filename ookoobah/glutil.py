from pyglet import gl

def ptr(*args):
    return (gl.GLfloat * len(args))(*args)
