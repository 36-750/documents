#' Utility functions for working with Sudoku grids.
#'
#' You shouldn't need to use any of the functions in this file -- they're merely
#' utilities to help the public functions in sudoku-grid.R, which you should
#' work with instead.
#'
#' @author Alex Reinhart

library(assertthat)
library(purrr)

#' Generate an empty Sudoku grid.
#'
#' Produces a grid in which every cell can take any value, represented as a n^2
#' x n^2 matrix, where each cell is a list of the possible values in that cell.
#' The grid is composed of n separate n x n blocks per side, for a total of n^2
#' such blocks.
#'
#' @param n the side length of each block (e.g. 3 for a standard Sudoku grid)
#' @return a matrix representing the grid
empty_grid <- function(n) {
    peermat <- matrix(list(1), nrow=n^2, ncol=n^2)
    for (row in 1:nrow(peermat)) {
        for (col in 1:ncol(peermat)) {
            peermat[[row, col]] <- make_peers(c(row, col), n)
        }
    }

    structure(matrix(list(1:n^2), nrow=n^2, ncol=n^2),
              class=c("sudoku", "matrix"),
              peers=peermat)
}

#' Find the list of peers of a cell.
#'
#' Peers are the cells which may not share a value with this cell: those in its
#' row, column, and block. Doesn't include the cell itself.
#'
#' @param cell the cell to find peers of
#' @param n block size of this grid
#' @return a list of coordinates of all peers
make_peers <- function(cell, n) {
    p <- list()

    row <- cell[1]
    col <- cell[2]

    p <- append(p, lapply(1:n^2, function(x) { as.integer(c(row, x)) }))
    p <- append(p, lapply(1:n^2, function(x) { as.integer(c(x, col)) }))
    p <- append(p, get_block_indices(cell, n))

    ## We can't allow a cell to be its own peer; if it is, we will try to
    ## eliminate its assigned value from itself. Also, remove duplicates.
    return(unique(remove_from_list(p, as.integer(cell))))
}

#' Display a Sudoku grid in pretty form.
#'
#' Prints a grid in which cells with one possibility have that possibility
#' shown, and undecided cells are printed as '.'.
#'
#' @param grid the grid to print
print.sudoku <- function(grid) {
    rows <- dim(grid)[1]
    cols <- dim(grid)[2]

    assert_that(rows == cols)

    n <- sqrt(rows)

    for (row in seq_len(rows)) {
        for (col in seq_len(cols)) {
            val <- grid[[row, col]]

            if (length(val) == 1) {
                cat(val)
                cat(" ")
            } else {
                cat(". ")
            }

            if (col %% n == 0 && col != cols) {
                cat("| ")
            }
        }
        cat("\n")

        if (row %% n == 0 && row != rows) {
            ## Each column and divider takes two spaces, except the last
            ## column only takes one.
            cat(strrep("-", 2 * cols + 2 * (n - 1) - 1))
            cat("\n")
        }
    }
}

#' Given a single coordinate (row or column), find the coordinates of the block.
#'
#' For example, in a n = 3 grid, row 4 is in the second block, which spans rows
#' 4 to 6.
#'
#' @param n block size of this grid
#' @param idx row or column index
#' @return vector of row or column indices of the containing block
#' @examples
#' get_side_indices(3, 4)  #=> c(4, 5, 6)
get_side_indices <- function(n, idx) {
    which_block <- (idx - 1) %/% n

    1:n + (n * which_block)
}

#' Return the indices of all cells in a given cell's block.
#'
#' @param cell the coordinates of the cell
#' @param n block size for this grid
#' @return a list of coordinate vectors for all cells in the block
get_block_indices <- function(cell, n) {
    row <- cell[1]
    col <- cell[2]

    row_idx <- get_side_indices(n, row)
    col_idx <- get_side_indices(n, col)

    return(map(cross2(row_idx, col_idx), as.integer))
}

#' Remove the value from the list, returning the new list.
#'
#' @param l list from which to remove
#' @param value value to remove
remove_from_list <- function(l, value) {
    l[lapply(l, function(val) { !identical(val, value) }) == TRUE]
}

#' Read a grid problem from a matrix, producing a grid of possibilities.
#'
#' The input grid is the grid we want to solve: a matrix of either numbers or
#' NAs, indicating empty cells which must be filled. We convert this to a grid
#' like those returned by \code{empty_grid} by transforming it to a grid where
#' each cell is a list of possible digits which may fill it. Pre-filled cells
#' have only one possible value.
#'
#' The grid must be square, and its side lengths must be a perfect square, since
#' each side is composed of n separate n x n blocks.
#'
#' @param grid the grid matrix to use
#' @return the parsed grid, or FALSE if it is invalid
parse_grid <- function(grid) {
    n <- sqrt(dim(grid)[1])

    assert_that(dim(grid)[1] == dim(grid)[2])
    assert_that(is.count(n))

    new_grid <- empty_grid(n)

    for (row in 1:n^2) {
        for (col in 1:n^2) {
            if (!is.na(grid[[row, col]])) {
                new_grid <- assign(new_grid, c(row, col), grid[[row, col]])
            }

            if (identical(new_grid, FALSE)) {
                ## A contradiction occurred; this must not be a valid grid.
                return(FALSE)
            }
        }
    }

    return(new_grid)
}


################################################################################
## DO NOT READ BELOW THIS LINE
##
## Later parts of the exercise have you write these functions yourself.
################################################################################

#' Remove digit from the possible values in the given cell.
#'
#' @param grid the current grid with all possible values
#' @param cell the c(row, column) coordinates of the cell to update
#' @param digit the digit to remove
#' @return The updated grid, or FALSE if a contradiction occurs
eliminate <- function(grid, cell, digit) {
    possible_digits <- grid[[cell[1], cell[2]]]

    if (!digit %in% possible_digits) {
        ## This value was already eliminated.
        return(grid)
    }

    new_digits <- possible_digits[which(possible_digits != digit)]
    grid[[cell[1], cell[2]]] <- new_digits

    if (length(new_digits) == 0) {
        ## We've eliminated the only possible value for this cell. Abort.
        return(FALSE)
    } else if (length(new_digits) == 1) {
        ## There's only one possible value here; may as well eliminate it
        ## from the peers of this cell, since they can't take this value.
        for (peer in peers(grid, cell)) {
            grid <- eliminate(grid, peer, new_digits)

            if (identical(grid, FALSE)) {
                return(FALSE)
            }
        }
    }

    return(grid)
}

#' Assign a cell to take a given value, eliminating all other possibilities.
#'
#' Propagates the constraints to neighboring cells through \code{eliminate}.
#'
#' @param grid the current grid with all possible values
#' @param cell the c(row, column) coordinates of the cell to update
#' @param digit the value to assign to this cell
#' @return the updated grid, or FALSE if a contradiction occurs
assign <- function(grid, cell, digit) {
    cur_digits <- grid[[cell[1], cell[2]]]

    other_values <- cur_digits[which(cur_digits != digit)]

    for (val in other_values) {
        grid <- eliminate(grid, cell, val)

        if (identical(grid, FALSE)) {
            return(FALSE)
        }
    }

    return(grid)
}

smallest_first <- function(grid, cell) {
    choices <- grid[[cell[1], cell[2]]]

    return(sort(choices))
}

largest_first <- function(grid, cell) {
    choices <- grid[[cell[1], cell[2]]]

    return(sort(choices, decreasing=TRUE))
}

random_order <- function(grid, cell) {
    choices <- grid[[cell[1], cell[2]]]

    return(sample(choices, size=length(choices)))
}

most_constrained <- function(grid) {
    ## Choose the unfilled square with the fewest possible choices.
    ## (Excluding those that are already finished.)
    num_choices <- matrix_map(grid, length)

    fewest <- min(num_choices[num_choices > 1])

    return(which(num_choices == fewest, arr.ind=TRUE)[1,])
}

least_constrained <- function(grid) {
    ## Choose the unfilled square with the most possible choices.
    ## (Excluding those that are already finished.)
    num_choices <- matrix_map(grid, length)

    fewest <- max(num_choices[num_choices > 1])

    return(which(num_choices == fewest, arr.ind=TRUE)[1,])
}
