import pyglet
import math


class GameRenderer(object):
    """Top level renderer.

    Renders the score and calls all other game object renderers.
    """
    FPS = 60
    COLOR_BACKGROUND_1 = (226, 82, 71, 255)
    COLOR_BACKGROUND_2 = (50, 54,  158, 255)

    def __init__(self, game, window):
        self.game = game
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.frame = 0
        pyglet.clock.set_fps_limit(self.FPS)

        # Init the background
        self.background = _add_rectangle( self.batch, 0, 0, self.window.width, self.window.height,
            self.COLOR_BACKGROUND_1, pyglet.graphics.OrderedGroup(0))

        # TODO: render the score and other labels

        # Init the renderers for all game objects
        self.renderers = []
        self.renderers.append( GridRenderer(game.grid, self.batch, window.width, window.height) )
        self.renderers.append( BallRenderer(game.ball, self.batch) )

    def draw(self):
        self._next_frame()
        self.window.clear()

        for renderer in self.renderers:
            renderer.draw()

        # We can draw th batch only after all renderers updated it
        self.batch.draw()

    def _next_frame(self):
        # TODO: there must be an FPS counter somewhere in pyglet
        self.frame = 0 if self.frame == self.FPS else self.frame + 1


class GridRenderer(object):

    CELL_SIZE = 30
    CELL_SPACING = 5
    COLOR_CELL = (217, 147, 78, 255)

    def __init__(self, grid, batch, window_width, window_height ):
        self.grid = grid
        self.batch = batch

        # Init the grid (centered on the screen)
        (num_cols, num_rows) = grid.size()
        grid_size_x = num_cols * (self.CELL_SIZE + self.CELL_SPACING) - self.CELL_SPACING
        grid_size_y = num_rows * (self.CELL_SIZE + self.CELL_SPACING) - self.CELL_SPACING
        start_pos_x = (window_width - grid_size_x) / 2
        start_pos_y = (window_height - grid_size_y) / 2

        # Render the cells
        for col in range(num_cols):
            pos_x = start_pos_x + (self.CELL_SIZE + self.CELL_SPACING) * col
            for row in range(num_rows):
                pos_y = start_pos_y + (self.CELL_SIZE + self.CELL_SPACING) * row
                _add_rectangle( batch, pos_x, pos_y, self.CELL_SIZE, self.CELL_SIZE, self.COLOR_CELL)

    def draw(self):
        # TODO: no need to draw the batch - only update the vertex list here
        #self.batch.draw()
        pass


class BallRenderer(object):

    def __init__(self, ball, batch):
        self.batch = batch

    def draw(self):
        pass

def _add_rectangle(batch, x, y, width, height, color, group=pyglet.graphics.OrderedGroup(1)):
    x2 = x + width
    y2 = y + height
    return batch.add(4, pyglet.gl.GL_QUADS, group,
        ('v2i', (x, y, x, y2, x2, y2, x2, y)),
        ('c4B', (color * 4))
    )