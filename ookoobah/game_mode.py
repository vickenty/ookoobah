import mode
import render


class GameMode(mode.Mode):

    name = "game_mode"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        # TODO: This is where we'll init the game objects
        # and pass them to the renderer
        self.renderer = render.GridRenderer(self.window)

    def tick(self):
        pass

    def on_draw(self):
        self.renderer.draw()

