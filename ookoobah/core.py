import random
from inventory import Inventory
import sounds

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
    human_name = 'Start'
    all_states = (
        (("direction", Ball.DIR_RIGHT),),
        (("direction", Ball.DIR_DOWN),),
        (("direction", Ball.DIR_LEFT),),
        (("direction", Ball.DIR_UP),),
    )

    def act(self, ball):
        pass

class Wall(Block):
    human_name = 'Wall'

    def act(self, ball):
        ball.direction = (
            -ball.direction[0],
            -ball.direction[1],
        )
        sounds.play('wall.wav')
        return True

class OneWay(Block):
    human_name = 'One way'
    all_states = (
        (("direction", Ball.DIR_RIGHT),),
        (("direction", Ball.DIR_DOWN),),
        (("direction", Ball.DIR_LEFT),),
        (("direction", Ball.DIR_UP),),
    )

    def act(self, ball):
        sounds.play('mirror.wav')
        ball.direction = self.direction

class Mirror(Block):
    human_name = 'Mirror'

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
        sounds.play('mirror.wav')

class FlipFlopMirror(Mirror):
    human_name = 'Flip mirror'

    def act(self, ball):
        super(FlipFlopMirror, self).act(ball)
        self.cycle_states()
        sounds.play('mirror.wav')

class Exit(Block):
    human_name = 'Finish'

    all_states = (
        (("is_on", False),),
    )

    def act(self, ball):
        if self.is_on:
            ball.status = Ball.STATUS_LEFT

class FlipFlop(Block):
    human_name = 'Bit'

    all_states = (
        (("is_on", False),),
        (("is_on", True),),
    )

    def act(self, ball):
        self.is_on = not self.is_on
        if self.is_on:
            sounds.play('flip-on.wav')
        else:
            sounds.play('flip-off.wav')

class Trap(Block):
    human_name = 'Trap'
    def act(self, ball):
        ball.status = Ball.STATUS_DEAD

class Swamp(Block):
    human_name = 'Cloud'

    def act(self, ball):
        pass

class Portal(Block):
    human_name = 'Portal'

    def act(self, ball):
        ball.pos = random.choice(self.other_portals)
        sounds.play('portal.wav')

class Game(object):
    STATUS_NEW = "new"
    STATUS_ON = "on"
    STATUS_VICTORY = "victory"
    STATUS_DEFEAT = "defeat"

    def __init__(self, grid):
        self.step_n = 0
        self.grid = grid
        self.inventory = Inventory()
        self.ball = None
        self.exit = None

    def build_inventory(self):
        for pos, block in self.grid.items():
            if not block.locked:
                del self.grid[pos]
                self.inventory.add_block(block.__class__)

    def erase_block(self, pos):
        try:
            self.inventory.add_block(self.grid[pos].__class__)
            del self.grid[pos]
        except KeyError:
            pass

    def place_block(self, pos, block_class, use_inventory=True):
        self.erase_block(pos)
        if use_inventory:
            self.inventory.use_block(block_class)
        self.grid[pos] = block_class()

    def grid_size(self):
        return tuple(n + 1 for n in map(max, zip(*self.grid.keys())))

    def start(self):
        assert self.get_status() == Game.STATUS_NEW, "game has been started already"

        ball = None
        exit = None
        portals = set()

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
            elif isinstance(block, Portal):
                portals.add(pos)

        if ball is None:
            raise Exception("no launcher found")
        if len(portals) == 1:
            raise Exception("single portal is non-sense")

        self.ball = ball
        self.exit = exit
        for pos in portals:
            self.grid[pos].other_portals = tuple(portals - set((pos,)))

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
        if self.exit:
            self.exit.is_on = all(ff.is_on for ff in self.grid.values() if isinstance(ff, FlipFlop))

ALL_BLOCKS = (
    Launcher,
    Exit,
    Wall,
    FlipFlop,
    Mirror,
    FlipFlopMirror,
    OneWay,
    Portal,
    Swamp,
    Trap,
)
