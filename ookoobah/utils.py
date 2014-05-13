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

BLOCK_TO_CHAR = {v: k for k, v in CHAR_TO_BLOCK.items()}

def populate_grid_from_string(grid, string):
    for y, line in enumerate(string.strip().split("\n")):
        for x, char in enumerate(line.strip()):
            block, param = CHAR_TO_BLOCK[char]
            if block:
                grid[x, y] = block(**dict(param))

def dump_grid_to_string(grid):

    def block_matches_desc(block, desc):
        b_type, b_attrs = desc
        return (block is None and b_type is None) \
            or (b_type is not None \
                and isinstance(block, b_type) \
                and all(hasattr(block, k) and getattr(block, k) == v for k, v in b_attrs))

    def block_to_char(block):
        return next(char for desc, char in BLOCK_TO_CHAR.items() if block_matches_desc(block, desc))

    (width, height) = grid.size()
    chars = ((block_to_char(grid.get((x, y))) for x in range(width)) for y in range(height))

    return "\n".join("".join(row) for row in chars)
