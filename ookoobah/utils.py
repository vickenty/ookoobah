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
}

def populate_grid_from_string(grid, string):
    build = lambda block, param: block(**dict(param)) if block is not None else None
    for y, line in enumerate(string.strip().split("\n")):
        for x, char in enumerate(line.strip()):
            grid[x, y] = build(*CHAR_TO_BLOCK[char])
