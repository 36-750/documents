"""
Some useful functions for Sudoku solving.

You should not need to read or edit any of the code here. These
functions are just useful utilities.

- Alex Reinhart
"""

from collections import namedtuple

Sudoku_t = namedtuple("Sudoku", ["cells", "peers", "n"])

class Sudoku(Sudoku_t):
    """We extend the namedtuple to provide pretty-printing and a copy method."""
    __slots__ = ()

    def __repr__(self):
        out = ''
        def display_cell(contents):
            if len(contents) == 1:
                return str(singleton(contents))
            return "."

        row_max = self.n**2

        for row in range(1, row_max + 1):
            out += ' '.join((display_cell(self.cells[(row, col)])
                             + (" |" if col % self.n == 0 and col != row_max
                                else ""))
                            for col in range(1, self.n**2 + 1))
            out += "\n"
            if row % self.n == 0 and row != row_max:
                out += "-" * (2 * self.n**2 + 2 * (self.n - 1) - 1)
                out += "\n"

        return out

    def copy(self):
        """Return a new Sudoku sharing the same peers and n, but new cells."""

        return Sudoku(cells=self.cells.copy(), peers=self.peers, n=self.n)

def empty_grid(n):
    """Make an empty Sudoku grid, where every cell can have every value.

    `n` is the block size, so a normal 9 x 9 Sudoku has n = 3, since each
    block is 3 x 3.
    """

    peers = {(row, col) : make_peers((row, col), n)
             for row in range(1, n**2 + 1)
             for col in range(1, n**2 + 1)}

    cells = {(row, col) : set(range(1, n**2 + 1))
             for row in range(1, n**2 + 1)
             for col in range(1, n**2 + 1)}

    return Sudoku(cells=cells, peers=peers, n=n)

def make_peers(cell, n):
    """Get a set of peers of a cell in a grid with block size `n`."""

    row, col = cell
    side_len = n**2 + 1

    peers = ({(row, x) for x in range(1, side_len)} |
             {(x, col) for x in range(1, side_len)} |
             get_block_indices(cell, n))

    return peers - set([cell])

def get_side_indices(n, idx):
    """Given a single coordinate, find the indices of the block.

    For example, in a n = 3 grid, row 4 is in the second block, which spans
    rows 4 to 6.
    """

    which_block = (idx - 1) // n

    block_start = n * which_block + 1

    return range(block_start, block_start + n)

def get_block_indices(cell, n):
    """Return the set of indices of all cells in a given cell's block."""

    row, col = cell

    return {(r, c) for r in get_side_indices(n, row)
            for c in get_side_indices(n, col)}

def singleton(s):
    """Extract the value out of a singleton set."""

    assert len(s) == 1, "Set is not a singleton"

    return list(s)[0]


################################################################################
## DO NOT READ BELOW THIS LINE
##
## Later parts of the exercise have you write these functions yourself.
################################################################################

def assign(grid, cell, digit):
    """Assign a cell to take a given value.

    Works by using `eliminate()` to remove all other values and propagate the
    constraint to peer cells.
    """

    cur_digits = grid.cells[cell]

    other_values = cur_digits - {digit}

    for val in other_values:
        grid = eliminate(grid, cell, val)

    if grid == False:
        return False

    return grid

def eliminate(grid, cell, digit):
    """Eliminate `digit` from the possible values of `cell`."""

    if grid == False:
        ## current grid is impossible
        return False

    possible_digits = grid.cells[cell]

    if digit not in possible_digits:
        ## This value was already eliminated.
        return grid

    new_digits = possible_digits - {digit}
    grid.cells[cell] = new_digits

    if len(new_digits) == 0:
        ## We've eliminated the only possible value for this cell. Abort.
        return False
    elif len(new_digits) == 1:
        ## There's only one possible value here; may as well eliminate it from
        ## the peers of this cell, since they can't take this value.
        for peer in grid.peers[cell]:
            grid = eliminate(grid, peer, singleton(new_digits))

    return grid

def largest_first(grid, cell):
    return sorted(grid.cells[cell], reverse=True)

def smallest_first(grid, cell):
    return sorted(grid.cells[cell])

def most_constrained(grid):
    return min(filter(lambda cell: len(cell[1]) > 1, grid.cells.items()),
               key=lambda cell: len(cell[1]))[0]

def least_constrained(grid):
    return max(filter(lambda cell: len(cell[1]) > 1, grid.cells.items()),
               key=lambda cell: len(cell[1]))[0]
