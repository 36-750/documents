"""
Represent a Sudoku grid, read one from a file, and solve with backtracking.

The grid is represented as a Sudoku object with a few fields:

- `cells` is a dictionary whose keys are cell coordinates and whose values are
  sets of possible values for that cell. Hence `grid.cells[(1,1)]` is the set
  of possible values for the top left cell.
- `peers` is a dictionary whose keys are cell coordinates and whose values are
  sets of coordinates of peers for each cell.
- `n` is the block size of the grid. A 9 x 9 Sudoku grid has n = 3, since each
  block is 3 x 3.

Additionally, the object has a `grid.copy()` method. This is needed because
objects in Python are passed by reference, so passing a Sudoku object to a
function which modifies it would result in destructive changes to our copy
too. So, for example, if you want to try setting a cell to a certain value,
see if the grid is solvable, and then backtrack if that value doesn't work,
you should set the value in a copy, so you can backtrack to the original.

Tip for those not familiar with sets in Python: {4, 2} represents a set
containing the set of numbers 4 and 2. Items can be removed via subtraction:
{4, 2} - {2} = {4}. There are also set unions, intersections, and so on.

- Alex Reinhart
"""

import math

from sudoku_grid_util import *


#################### START EDITING HERE ####################

def solve_sudoku(grid, next_cell, order_choices):
    """Solve a Sudoku grid via backtracking.

    If the grid cannot be solved, return False.

    grid: A Sudoku object returned from `parse_grid`
    next_cell: A function which takes the current grid and returns the
        coordinates of the cell we should fill in next
    order_choices: A function which takes the current grid and the coordinates
        of the cell chosen to fill in next, and returns an ordered list of the
        values which should be tried in that cell
    """

    if grid == False:
        ## must have died earlier
        return False

    if solved(grid):
        ## This is a solution. We win.
        return grid

    next_idx = next_cell(grid)
    choices = order_choices(grid, next_idx)

    ## INSERT CODE HERE ##
    ## Pick a cell and try to assign values to it.
    ##
    ## See the assign() definition below to see how to use it. You also have a
    ## most_constrained(grid) function, which takes a grid as an argument and
    ## returns the coordinates of the most constrained cell, and a
    ## smallest_first(grid, cell) function which returns the possible values for
    ## that grid cell, ordered from smallest to largest. These can be used as
    ## `next_cell` and `order_choices` arguments.
    ##
    ## Be sure to use `grid.copy()` to get a copy of a grid before assigning
    ## values in it.

    for choice in choices:
        # do stuff here
        pass



#################### STEP 2 ####################
## After you complete the function above and verify that it works, try
## uncommenting these functions and filling them in.


# def assign(grid, cell, digit):
#     """Assign a cell to take a given value.

#     Works by using `eliminate()` to remove all other values and propagate the
#     constraint to peer cells.
#     """

#     cur_digits = grid.cells[cell]

#     other_values = cur_digits - {digit}

#     ## INSERT CODE HERE ##
#     ## eliminate all other values from this cell

#     return grid

# def eliminate(grid, cell, digit):
#     """Eliminate `digit` from the possible values of `cell`."""

#     if grid == False:
#         ## current grid is impossible
#         return False

#     possible_digits = grid.cells[cell]

#     if digit not in possible_digits:
#         ## This value was already eliminated.
#         return grid

#     new_digits = possible_digits - {digit}
#     grid.cells[cell] = new_digits

#     if len(new_digits) == 0:
#         ## We've eliminated the only possible value for this cell. Abort.
#         return False
#     elif len(new_digits) == 1:
#         ## INSERT CODE HERE ##
#         ## propagate constraints to peer cells



#     return grid


##################### STOP EDITING HERE #####################
## Functions below are for your use or reference, but you
## do not need to edit them.

def read_grid(filename):
    """Read a grid from a file and return the Sudoku object."""
    f = open(filename, "r")

    grid = list(map(lambda line: [int(c) if c != "0" else None
                                  for c in line[:-1]],
                    f))

    return parse_grid(grid)

def count_calls(fn):
    """Takes a function and return a new function that counts calls to itself.

    The number of calls is tracked in a `.calls` property of the function.
    The new function must have the same name as the old, so the old recurses
    into it correctly.
    For example:

    solve_sudoku = count_calls(solve_sudoku)
    solve_sudoku(grid, most_constrained, smallest_first)
    solve_sudoku.calls #=> number of calls

    solve_sudoku.calls = 0 # resets count
    """

    def counter(*args, **kwargs):
        counter.calls += 1
        return fn(*args, **kwargs)

    counter.calls = 0

    return counter

def solved(grid):
    """Test if all values have been filled in."""

    return all(len(vals) == 1 for vals in grid.cells.values())

def parse_grid(grid_rows):
    """Take a read-in grid and turn it into a Sudoku object.

    Takes the list of lines from `read_grid` and an empty Sudoku object,
    then assigns each cell the correct values.
    """

    n = int(math.sqrt(len(grid_rows)))

    assert n**2 == len(grid_rows), "Side length must be square of block size"

    new_grid = empty_grid(n)

    for row, cols in enumerate(grid_rows, 1):
        for col, val in enumerate(cols, 1):
            if val is not None:
                new_grid = assign(new_grid, (row, col), val)

    if new_grid == False:
        return False

    return new_grid
