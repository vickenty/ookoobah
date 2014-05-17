class BaseTool (object):
    draw_locks = False
    def update_cursor(self, mouse):
        mouse.set_cursor(None)

class DrawTool (BaseTool):
    def __init__(self, block_class):
        self.block_class = block_class

    def apply(self, pos, game, editor):
        old = game.grid.get(pos)
        if old.__class__ == self.block_class:
            old.cycle_states()
        else:
            game.place_block(pos, self.block_class, not editor)
            game.grid[pos].locked = editor
            return True

    def update_cursor(self, mouse):
        mouse.set_cursor(self.block_class)

class EraseTool (BaseTool):
    def apply(self, pos, game, editor):
        game.erase_block(pos)

class LockTool (BaseTool):
    draw_locks = True
    def apply(self, pos, game, editor):
        obj = game.grid.get(pos)
        if obj:
            obj.locked = not obj.locked

class TriggerTool (BaseTool):
    def apply(self, pos, game, editor):
        if pos in game.grid:
            game.grid[pos].cycle_states()

