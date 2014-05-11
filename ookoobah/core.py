class Grid(dict):
    pass

class Block(object):
    def act(self, ball):
        raise NotImplemented

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
    def __init__(self, grid, ball):
        self.step_n = 0
        self.grid = grid
        self.ball = ball

    def __str__(self):
        return "<Game: step_n=%s, grid=%s, ball=%s>" % (self.step_n, self.grid, self.ball)

    def step(self):
        self.ball.move()
        block = self.grid.get(self.ball.pos)
        if block:
            block.act(self.ball)
        self.step_n += 1

if __name__ == "__main__":
    grid = Grid()
    grid[2, 0] = Mirror()
    grid[3, 0] = Wall()
    ball = Ball()
    game = Game(grid=grid, ball=ball)
    for n in range(10):
        print game
        game.step()
