#' Represent a Sudoku grid, read one from a file, and solve with backtracking.
#'
#' @author Alex Reinhart

######################## BEGIN EDITING HERE ########################
### Your task is to fill in the functions below, and provide
### implementations of next_cell and order_choices.

#' Solve a Sudoku grid via backtracking.
#'
#' If the grid cannot be solved, return False.
#'
#' @param grid Grid matrix returned from \code{parse_grid}
#' @param next_cell A function which takes the current grid and returns the
#'     coordinates of the cell we should fill in next.
#' @param order_choices A function which takes the current grid and the
#'     coordinates of the cell chosen to fill in next, and returns an ordered
#'     vector of the values which should be tried in that cell
#' @return Matrix representing the solved grid
solve_sudoku <- function(grid, next_cell, order_choices) {
    if (identical(grid, FALSE)) {
        ## Must have died earlier
        return(FALSE)
    }

    if (solved(grid)) {
        ## We have solved the grid.
        return(grid)
    }

    next.idx <- next_cell(grid)

    choices <- order_choices(grid, next.idx)

    ## INSERT CODE HERE ##
    ## Pick a cell and try to assign values to it.
    ##
    ## See assign() and eliminate() definitions below to see how to use them.
    ## You also have a most_constrained(grid) function, which takes a grid as an
    ## argument and returns the coordinates of the most constrained cell, and a
    ## smallest_first(grid, cell) function which returns the possible values for
    ## that grid cell, ordered from smallest to largest. These can be used as
    ## `next_cell` and `order_choices` arguments.


}

## #' Assign a cell to take a given value, eliminating all other possibilities.
## #'
## #' Propagates the constraints to neighboring cells through \code{eliminate}.
## #'
## #' @param grid the current grid with all possible values
## #' @param cell the c(row, column) coordinates of the cell to update
## #' @param digit the value to assign to this cell
## #' @return the updated grid, or FALSE if a contradiction occurs
## assign <- function(grid, cell, digit) {
##     cur_digits <- grid[[cell[1], cell[2]]]

##     other_values <- cur_digits[which(cur_digits != digit)]

##     ## INSERT CODE HERE ##
##     ## eliminate all other values from this cell


##     return(grid)
## }

## #' Remove digit from the possible values in the given cell.
## #'
## #' @param grid the current grid with all possible values
## #' @param cell the c(row, column) coordinates of the cell to update
## #' @param digit the digit to remove
## #' @return The updated grid, or FALSE if a contradiction occurs
## eliminate <- function(grid, cell, digit) {
##     possible_digits <- grid[[cell[1], cell[2]]]

##     if (!digit %in% possible_digits) {
##         ## This digit was already eliminated from this cell.
##         return(grid)
##     }

##     new_digits <- possible_digits[which(possible_digits != digit)]
##     grid[[cell[1], cell[2]]] <- new_digits

##     if (length(new_digits) == 0) {
##         ## We've eliminated the only possible value for this cell.
##         ## It's not possible to solve this grid.
##         return(FALSE)
##     } else if (length(new_digits) == 1) {
##         ## INSERT CODE HERE ##
##         ## propagate constraints to peer cells



##     }

##     return(grid)
## }

############################ STOP EDITING HERE ############################
### Functions below this point are for your use, but you should not need to
### change them in any way.
###
### sudoku-grid-util.R contains functions used by these; you shouldn't need
### any of those functions directly.

source("sudoku-grid-util.R")

#' Find the peers of a cell.
#'
#' Peers are the cells which may not share a value with this cell: those in its
#' row, column, and block. Doesn't include the cell itself. In a standard 9 x 9
#' grid, each cell has 20 peers.
#'
#' @param grid Grid on which this cell lives
#' @param cell Coordinates of cell to find peers of
#' @return list of peer coordinates
peers <- function(grid, cell) {
    return(attr(grid, "peers")[[cell[1], cell[2]]])
}

#' Read a Sudoku grid from a file.
#'
#' @param filename name of the file to read from
#' @return the parsed grid, as returned by \code{parse_grid}
read_grid <- function(filename) {
    lines <- readLines(filename)

    lines <- sapply(lines, function(line) {
        line <- as.numeric(strsplit(line, "")[[1]])
        line[line == 0] <- NA
        return(line)
    })

    return(parse_grid(t(lines)))
}

#' Apply a function to every cell in a matrix, returning a matrix of values.
#'
#' @param mat matrix to apply to
#' @param fn univariate function, taking matrix cells and returning new values
#' @return matrix of values of fn
matrix_map <- function(mat, fn) {
    new_mat <- sapply(mat, fn)
    dim(new_mat) <- dim(mat)

    return(new_mat)
}

#' Test if a grid is already solved.
#'
#' Checks if there are any cells left to fill. Does not do any checks that the
#' solution is correct, just that every cell is filled.
#'
#' @param grid Sudoku grid to check
#' @return boolean
solved <- function(grid) {
    vals_left <- matrix_map(grid, length)

    return(all(vals_left == 1))
}

#' Count the number of calls to a function in a given block of code.
#'
#' @param fn function name to trace, as a string
#' @param code code to run
#' @return number of calls to \code{fn}
#' @examples
#' count_calls("solve_sudoku",
#'             solve_sudoku(grid, most_constrained, ascending_order))
count_calls <- function(fn, code) {
    count <- 0
    code_call <- substitute(code)

    trace(fn, tracer <- function() { count <<- count + 1 },
          print=FALSE)

    eval(code_call)

    untrace(fn)

    return(count)
}
