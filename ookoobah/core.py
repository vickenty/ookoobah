class Grid(dict):
    def __init__(self, *args, **kwargs):
        super(Grid, self).__init__(*args, **kwargs)
        self.dirty = []

    def __setitem__(self, key, value):
        self.dirty.append(key)
        super(Grid, self).__setitem__(key, value)

    def size(self):
        # TODO Cache me, maybe
        return tuple(n + 1 for n in map(max, zip(*self.keys())))

    def get_dirty(self):
        dirty = self.dirty
        self.dirty = []
        return dirty

class Block(object):
    def __init__(self, *args, **kwargs):
        self.locked = False

    def act(self, ball):
        raise NotImplementedError()

class Launcher(Block):
    def __init__(self, direction=None):
        super(Launcher, self).__init__()
        if direction is None:
            direction = Ball.DIR_RIGHT
        self.direction = direction

    def act(self, ball):
        pass

class Wall(Block):
    def __init__(self):
        super(Wall, self).__init__()

    def act(self, ball):
        ball.direction = (
            -ball.direction[0],
            -ball.direction[1],
        )
        return True

class Mirror(Block):
    SLOPE_BACKWARD = 1
    SLOPE_FORWARD = -1

    def __init__(self, slope=SLOPE_BACKWARD):
        super(Mirror, self).__init__()
        self.slope = slope

    def act(self, ball):
        ball.direction = (
            ball.direction[1] * self.slope,
            ball.direction[0] * self.slope,
        )

class Exit(Block):
    def __init__(self, is_on=False):
        super(Exit, self).__init__()
        self.is_on = False

    def act(self, ball):
        if self.is_on:
            ball.status = Ball.STATUS_LEFT

class FlipFlop(Block):
    def __init__(self, is_on=False):
        super(FlipFlop, self).__init__()
        self.is_on = is_on

    def act(self, ball):
        self.is_on = not self.is_on

class Trap(Block):
    def __init__(self):
        super(Trap, self).__init__()

    def act(self, ball):
        ball.status = Ball.STATUS_DEAD

class Ball(object):
    DIR_RIGHT = (1, 0)
    DIR_DOWN = (0, 1)
    DIR_LEFT = (-1, 0)
    DIR_UP = (0, -1)

    STATUS_ALIVE = 0
    STATUS_DEAD = 1
    STATUS_LEFT = 2

    def __init__(self, direction=DIR_RIGHT, pos=(0, 0), status=STATUS_ALIVE):
        self.direction = direction
        self.pos = pos
        self.status = status

    def __str__(self):
        return "<Ball: pos=%s, direction=%s>" % (self.pos, self.direction)

    def move(self):
        self.pos = (
            self.pos[0] + self.direction[0],
            self.pos[1] + self.direction[1],
        )

class Game(object):
    STATUS_NEW = "new"
    STATUS_ON = "on"
    STATUS_VICTORY = "victory"
    STATUS_DEFEAT = "defeat"

    def __init__(self, grid):
        self.step_n = 0
        self.grid = grid
        self.ball = None
        self.exit = None

    def __str__(self):
        return "<Game: step_n=%s, grid=%s, ball=%s>" % (self.step_n, self.grid, self.ball)

    def start(self):
        for pos, block in self.grid.items():
            if isinstance(block, Launcher):
                # TODO Shove balls into a list: there are may be multiple launchers, and thus balls
                assert self.ball is None, "launcher block redefined"
                self.ball = Ball(direction=block.direction, pos=pos)
            elif isinstance(block, Exit):
                assert self.exit is None, "exit block redefined"
                self.exit = block

        assert self.ball is not None, "no launcher blocks found"
        assert self.exit is not None, "no exit block found"

        self._update_exit()

    def get_status(self):
        if not self.ball:
            return Game.STATUS_NEW
        elif self.ball.status == Ball.STATUS_LEFT:
            return Game.STATUS_VICTORY
        elif self.ball.status == Ball.STATUS_DEAD:
            return Game.STATUS_DEFEAT
        else:
            return Game.STATUS_ON

    def step(self):
        state = self.get_status()
        assert state != Game.STATUS_NEW, "game has not been started"
        if state != Game.STATUS_ON:
            return state

        keep_moving = True
        while keep_moving:
            self.ball.move()

            block = self.grid.get(self.ball.pos)
            if block:
                keep_moving = block.act(self.ball)
            else:
                keep_moving = False

            self._update_exit()

        self.step_n += 1

        return state

    def _update_exit(self):
        # TODO Cache me, maybe
        self.exit.is_on = all(ff.is_on for ff in self.grid.values() if isinstance(ff, FlipFlop))
