import mode
import core
import render


class GameMode(mode.Mode):

    name = "game_mode"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.game = core.Game()
        self.renderer = render.GameRenderer(self.game, self.window)

    def tick(self):
        pass

    def on_draw(self):
        self.renderer.draw()

