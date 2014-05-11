import pyglet


class GridRenderer(object):

    FPS = 30

    NUM_ROWS = 10
    NUM_COLS = 10
    CELL_SIZE = 50
    CELL_SPACING = 5

    COLOR_BACKGROUND_1 = (50, 108, 158, 255)
    COLOR_BACKGROUND_2 = (50, 54, 158, 255)
    COLOR_CELL = (50, 54, 158, 255)

    def __init__(self, window, grid=None):
        self.grid = grid
        self.frame = 0
        self.batch = pyglet.graphics.Batch()
        self.window = window

        # Init the background
        self.background = self._rectangle( 0, 0, self.window.width, self.window.height,
            self.COLOR_BACKGROUND_1, pyglet.graphics.OrderedGroup(0))

        # Init the grid
        for row in range(self.NUM_ROWS):
            for col in range(self.NUM_COLS):
                pass
                #self._rectangle(  )        

    def draw(self):
        self._next_frame()
        self.window.clear()
        self.batch.draw()

    def _next_frame(self):
        # TODO: there must be an FPS counter somewhere        
        self.frame = 0 if self.frame == self.FPS else self.frame + 1

    def _rectangle(self, x, y, width, height, color, group=None):
        return self.batch.add(4, pyglet.gl.GL_QUADS, group,
            ('v2i', (0, 0, 0, height, width, height, width, 0)),
            ('c4B', (color * 4))
        )
