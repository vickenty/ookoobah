import mode
import core
import render


class GameMode(mode.Mode):

    name = "game_mode"

    def connect(self, controller):
        super(GameMode, self).connect(controller)
        self.game = self._create_test_game()
        self.renderer = render.GameRenderer(self.game, self.window)
        self.game.start()

    def tick(self):
        pass

    def on_draw(self):
        self.renderer.draw()

    def _create_test_game(self):
        game = core.Game()
        game.grid[0, 0] = core.Launcher()
        game.grid[2, 0] = core.Mirror()
        game.grid[3, 0] = core.Wall()
        game.grid[13, 10] = core.Wall()
        return game
