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
    def act(self, ball):
        raise NotImplementedError()

class Launcher(object):
    def __init__(self, direction=None):
        if direction is None:
            direction = Ball.DIR_RIGHT
        self.direction = direction

    def act(self, ball):
        pass

class Wall(Block):
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
        self.slope = slope

    def act(self, ball):
        ball.direction = (
            ball.direction[1] * self.slope,
            ball.direction[0] * self.slope,
        )

class Exit(Block):
    def act(self, ball):
        pass

class Trap(Block):
    def act(self, ball):
        pass

class Ball(object):
    DIR_RIGHT = (1, 0)
    DIR_DOWN = (0, 1)
    DIR_LEFT = (-1, 0)
    DIR_UP = (0, -1)

    def __init__(self, direction=DIR_RIGHT, pos=(0, 0)):
        self.direction = direction
        self.pos = pos
        pass

    def __str__(self):
        return "<Ball: pos=%s, direction=%s>" % (self.pos, self.direction)

    def move(self):
        self.pos = (
            self.pos[0] + self.direction[0],
            self.pos[1] + self.direction[1],
        )

class Game(object):
    STATUS_ON = "on"
    STATUS_VICTORY = "victory"
    STATUS_DEFEAT = "defeat"

    def __init__(self):
        self.step_n = 0
        self.grid = Grid()
        self.ball = None

    def __str__(self):
        return "<Game: step_n=%s, grid=%s, ball=%s>" % (self.step_n, self.grid, self.ball)

    def start(self):
        for pos, block in self.grid.items():
            if isinstance(block, Launcher):
                # TODO Shove balls into a list: there are may be multiple launchers, and thus balls
                self.ball = Ball(direction=block.direction, pos=pos)

        assert self.ball is not None, "no launcher blocks found"

    def get_status(self):
        block = self.grid.get(self.ball.pos)
        if isinstance(block, Exit):
            return Game.STATUS_VICTORY
        elif isinstance(block, Trap):
            return Game.STATUS_DEFEAT
        else:
            return Game.STATUS_ON

    def step(self):
        state = self.get_status()
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

        self.step_n += 1

        return state
