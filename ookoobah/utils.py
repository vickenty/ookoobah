import core

CHAR_TO_BLOCK = {
    ".":  (None, ()),
    ">":  (core.Launcher, (("direction", core.Ball.DIR_RIGHT),)),
    "v":  (core.Launcher, (("direction", core.Ball.DIR_DOWN),)),
    "<":  (core.Launcher, (("direction", core.Ball.DIR_LEFT),)),
    "^":  (core.Launcher, (("direction", core.Ball.DIR_UP),)),
    "#":  (core.Wall, ()),
    "/":  (core.Mirror, (("slope", core.Mirror.SLOPE_FORWARD),)),
    "\\": (core.Mirror, (("slope", core.Mirror.SLOPE_BACKWARD),)),
    "X":  (core.FlipFlopMirror, ()),
    "o":  (core.Exit, (("is_on", False),)),
    "O":  (core.Exit, (("is_on", True),)),
    "+":  (core.Trap, ()),
    "|":  (core.FlipFlop, (("is_on", False),)),
    "-":  (core.FlipFlop, (("is_on", True),)),
}

BLOCK_TO_CHAR = {v: k for k, v in CHAR_TO_BLOCK.items()}

def make_grid_from_string(string):
    grid = {}
    for y, line in enumerate(string.strip().split("\n")):
        for x, char in enumerate(c for c in line if not c.isspace()):
            block, param = CHAR_TO_BLOCK[char]
            if block:
                b = block()
                for k, v in param:
                    setattr(b, k, v)
                grid[x, y] = b
    return grid

BALL_POS_TO_CHAR = {
    core.Ball.DIR_RIGHT: ">",
    core.Ball.DIR_DOWN: "v",
    core.Ball.DIR_LEFT: "<",
    core.Ball.DIR_UP: "^",
}

def dump_game_to_string(game):
    grid, ball = game.grid, game.ball

    def block_matches_desc(block, desc):
        b_type, b_attrs = desc
        return (block is None and b_type is None) \
            or (b_type is not None \
                and type(block) is b_type \
                and all(hasattr(block, k) and getattr(block, k) == v for k, v in b_attrs))

    def block_to_char(block):
        return next(char for desc, char in BLOCK_TO_CHAR.items() if block_matches_desc(block, desc))

    def place_ball(ball, char_pos, char):
        if ball and ball.pos == char_pos:
            return "\x1b[7m%s\x1b[0m" % BALL_POS_TO_CHAR[ball.direction]
        else:
            return char

    (width, height) = game.grid_size()
    chars = ((place_ball(ball, (x, y), block_to_char(grid.get((x, y)))) for x in range(width)) for y in range(height))

    return "\n".join(" ".join(row) for row in chars)
