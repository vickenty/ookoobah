class BaseTool (object):
    draw_locks = False
    def update_cursor(self, mouse):
        mouse.set_cursor(None)

class DrawTool (BaseTool):
    def __init__(self, block_class):
        self.block_class = block_class

    def apply(self, pos, grid, editor):
        old = grid.get(pos)
        if old.__class__ == self.block_class:
            old.cycle_states()
        else:
            grid[pos] = self.block_class()
            grid[pos].locked = editor
            return True

    def update_cursor(self, mouse):
        mouse.set_cursor(self.block_class)

class EraseTool (BaseTool):
    def apply(self, pos, grid, editor):
        try:
            del grid[pos]
        except KeyError:
            pass
        return True

class LockTool (BaseTool):
    draw_locks = True
    def apply(self, pos, grid, editor):
        obj = grid.get(pos)
        if obj:
            obj.locked = not obj.locked

class TriggerTool (BaseTool):
    def apply(self, pos, grid, editor):
        if pos in grid:
            grid[pos].cycle_states()

