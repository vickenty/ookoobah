class Grid(dict):
    def size(self):
        # TODO Cache me, maybe
        return map(max, zip(*self.keys()))

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

    def step(self):
        self.ball.move()
        block = self.grid.get(self.ball.pos)
        if block:
            block.act(self.ball)
        self.step_n += 1
