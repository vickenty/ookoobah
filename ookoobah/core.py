class Ball(object):
    DIR_RIGHT = (1, 0)
    DIR_DOWN = (0, 1)
    DIR_LEFT = (-1, 0)
    DIR_UP = (0, -1)

    STATUS_ALIVE = 0
    STATUS_DEAD = 1
    STATUS_LEFT = 2

    def __init__(self, direction, pos):
        self.direction = direction
        self.pos = pos
        self.status = Ball.STATUS_ALIVE

    def move(self):
        self.pos = (
            self.pos[0] + self.direction[0],
            self.pos[1] + self.direction[1],
        )

class Block(object):
    all_states = ((),)
    all_states_idx = -1

    def __init__(self):
        self.locked = True
        self.cycle_states()

    def act(self, ball):
        raise NotImplementedError()

    def cycle_states(self):
        self.all_states_idx += 1
        if self.all_states_idx == len(self.all_states):
            self.all_states_idx = 0
        for k, v in self.all_states[self.all_states_idx]:
            setattr(self, k, v)

class Launcher(Block):
    all_states = (
        (("direction", Ball.DIR_RIGHT),),
        (("direction", Ball.DIR_DOWN),),
        (("direction", Ball.DIR_LEFT),),
        (("direction", Ball.DIR_UP),),
    )

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

    all_states = (
        (("slope", SLOPE_BACKWARD),),
        (("slope", SLOPE_FORWARD),),
    )

    def act(self, ball):
        ball.direction = (
            ball.direction[1] * self.slope,
            ball.direction[0] * self.slope,
        )

class FlipFlopMirror(Mirror):
    def act(self, ball):
        super(FlipFlopMirror, self).act(ball)
        self.cycle_states()

class Exit(Block):
    def act(self, ball):
        if self.is_on:
            ball.status = Ball.STATUS_LEFT

class FlipFlop(Block):
    all_states = (
        (("is_on", False),),
        (("is_on", True),),
    )

    def act(self, ball):
        self.is_on = not self.is_on

class Trap(Block):
    def act(self, ball):
        ball.status = Ball.STATUS_DEAD

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

    def start(self):
        assert self.get_status() == Game.STATUS_NEW, "game has been started already"

        ball = None
        exit = None

        for pos, block in self.grid.items():
            if isinstance(block, Launcher):
                # TODO Shove balls into a list: there are may be multiple launchers, and thus balls
                if ball is not None:
                    raise Exception("must be a single launcher")
                ball = Ball(direction=block.direction, pos=pos)
            elif isinstance(block, Exit):
                if exit is not None:
                    raise Exception("must be a single exit")
                exit = block

        if ball is None:
            raise Exception("no launcher found")

        self.ball = ball
        self.exit = exit

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

ALL_BLOCKS = (
    Exit,
    FlipFlop,
    FlipFlopMirror,
    Launcher,
    Mirror,
    Trap,
    Wall,
)
