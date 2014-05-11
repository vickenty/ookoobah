import pyglet
import math


class GameRenderer(object):
    """Top level renderer.

    Renders the score and calls all other game object renderers.
    """
    FPS = 60

    def __init__(self, game, window):
        self.game = game
        self.window = window
        self.frame = 0
        self.renderers = []
        self.renderers.append( GridRenderer(game.grid, window) )
        self.renderers.append( BallRenderer(game.ball, window) )

    def draw(self):
        self._next_frame()
        self.window.clear()        
        for renderer in self.renderers:
            renderer.draw()

    def _next_frame(self):
        # TODO: there must be an FPS counter somewhere in pyglet
        self.frame = 0 if self.frame == self.FPS else self.frame + 1


class GridRenderer(object):

    NUM_ROWS = 8
    NUM_COLS = 8
    CELL_SIZE = 30
    CELL_SPACING = 5

    COLOR_BACKGROUND_1 = (226, 82, 71, 255)
    COLOR_BACKGROUND_2 = (50, 54,  158, 255)
    COLOR_CELL = (217, 147, 78, 255)

    def __init__(self, grid, window):
        self.grid = grid
        self.frame = 0
        self.batch = pyglet.graphics.Batch()
        self.window = window

        # Init the background
        self.background = self._add_rectangle( 0, 0, self.window.width, self.window.height,
            self.COLOR_BACKGROUND_1, pyglet.graphics.OrderedGroup(0))

        # Init the grid (centered on the screen)
        grid_size_x = self.NUM_COLS * (self.CELL_SIZE + self.CELL_SPACING) - self.CELL_SPACING
        grid_size_y = self.NUM_ROWS * (self.CELL_SIZE + self.CELL_SPACING) - self.CELL_SPACING
        start_pos_x = (self.window.width - grid_size_x) / 2
        start_pos_y = (self.window.height - grid_size_y) / 2

        for col in range(self.NUM_COLS):
            pos_x = start_pos_x + (self.CELL_SIZE + self.CELL_SPACING) * col
            for row in range(self.NUM_ROWS):
                pos_y = start_pos_y + (self.CELL_SIZE + self.CELL_SPACING) * row
                self._add_rectangle( pos_x, pos_y, self.CELL_SIZE, self.CELL_SIZE, self.COLOR_CELL)

    def draw(self):
        self.batch.draw()

    def _add_rectangle(self, x, y, width, height, color, group=pyglet.graphics.OrderedGroup(1)):
        x2 = x + width
        y2 = y + height
        return self.batch.add(4, pyglet.gl.GL_QUADS, group,
            ('v2i', (x, y, x, y2, x2, y2, x2, y)),
            ('c4B', (color * 4))
        )


class BallRenderer(object):

    def __init__(self, ball, window):
        pass

    def draw(self):
        pass