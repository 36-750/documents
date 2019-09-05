#' Simple implementation of the mean-shift algorithm
#'
#' The mean-shift algorithm is nonparametric method for
#' locating the maximum of an estimated density function.
#' In a single step of the algorithm, a point \eqn{x}
#' is replaced by \eqn{m(x)}, where
#' \deqn{m(x) = \frac{\sum_{y\in S} K(x - y) y}{\sum_{y\in S} K(x - y)}.}
#' The coorresponding trajectory is obtained, starting at \eqn{x},
#' as \eqn{x, m(x), m(m(x)), m(m(m(x))), \ldots}.
#'
#' @references See the following papers for background and applications:
#'
#'   Cheng, Y. “Mean shift, mode seeking, and clustering,” IEEE Trans. Pattern Anal.
#'   Machine Intell., vol. 17, pp. 790–799, 1995.
#'
#'   Comaniciu, D. and Meer, P. "Mean Shift: A Robust Approach to Feature-Space Analysis".
#'   IEEE Transactions on Pattern Analysis and Machine Intelligence archive
#'   Volume 24 Issue 5, May 2002, pp. 603-619.
#'
#'   Fukunaga, K. and Hostetler, L. D., “The estimation of the gradient of a density function,
#'   with applications in pattern recognition,” IEEE Trans. Information Theory, vol. 21,
#'   pp. 32–40, 1975.
#'

library(assertthat)


#' Kernel density estimate of a given data set evaluated at a specified point
#'
#' The kernel density estimator at a specified point \eqn{x} takes a weighted
#' average of the data, using \eqn{K(x - y)} as the weight at data point \eqn{y}.
#' The function \eqn{K} is called a kernel. It is usually non-negative and
#' integrates to 1 but that is not required. Hence, the kernel-weighted average
#' at point \eqn{x} is \deqn{\frac{\sum_{y} K(x - y) y}{\sum_{y} K(x - y)}}.
#'
#' @param evaluation_point Point at which to evaluate the weighted average,
#'                         a vector or one dimensional matrix
#' @param data             Data set containing points to average over,
#'                         a matrix whose column dimension is the same
#'                         as the length of \code{evaluation_point}.
#' @param kernel           A smoothing kernel function, takes a d-vector
#'                         and returns a real number.
#' @return  The kernel weighted mean, a vector the same dimension as
#'          \code{evaluation_point}.
#'
#' @author Christopher R. Genovese
#'
kernel_weighted_average <- function(evaluation_point, data, kernel) {
    numerator <- rep(0.0, length(evaluation_point))
    denominator <- 0.0

    for ( index in 1:nrow(data) ) {
        kernel_value <- kernel(evaluation_point - data[index, ])
        numerator <- numerator + kernel_value * data[index, ]
        denominator <- denominator + kernel_value
    }

    return(numerator/denominator)
}

#' Mean-shift trajectories of arbitrary points with respect to smoothed data
#'
#' Smooths the given data with a specified kernel and then applies the mean shift
#' to each given starting point for the specified number of steps. Each starting
#' point thus traces out a path (its mean-shift trajectory) toward the mode
#' of the estimated density.
#'
#' @param data      Data points from which to compute the density estimate,
#'                  a numeric matrix (call this n by d).
#' @param start_at  Points for which to compute the mean-shift trajectories,
#'                  a numeric matrix  of the same shape as \code{data}
#' @param kernel    A smoothing kernel function, takes a d-vector
#'                  and returns a real number.
#' @param steps     Number of steps in the computed trajectories, a positive
#'                  integer.
#'
#' @return Array (dimensions n by d by steps+1) giving trajectories for
#'         each point in \code{starts_at}. The vector at position \code{[i,,k]}
#'         is the location on the trajectory of point \code{starts_at[i,]}
#'         after \code{k-1} steps.
#'
#' @author Christopher R. Genovese
#'
mean_shift_trajectories <- function(data, start_at, kernel, steps) {
    n_points  <- nrow(start_at)
    space_dim <- ncol(start_at)
    trajectories <- array(0, dim=c(n_points, space_dim, steps+1))
    trajectories[,,1] <- start_at  # array dims: start_point, x-y, steps

    for( step in 1:steps ) {
        for( eval_pt_index in 1:n_points ) {
            eval_pt = trajectories[eval_pt_index,,step]
            trajectories[eval_pt_index, , step+1] <-
                kernel_weighted_average(eval_pt, data, kernel)
        }
    }
    return( trajectories )
}

#' Trajectory for a single starting point as a matrix of points
#'
#' Extracts from the trajectories array a steps by d matrix of
#' d-dimensional points in order along the trajectory.
#'
#' @param trajectories An array of trajectories as returned by
#'                     \code{mean_shift_trajectories}
#' @param index        Index of the starting point
#'
#' @return Numeric matrix whose rows are point on the index'th
#'         trajectory, in order.
#'
get_trajectory <- function(trajectories, index) {
    return( t(trajectories[index,,]) )  # dimension steps x 2
}

#' Add a two-dimensional trajectory curve to an existing plot
#'
#' Adds the starting point and a curve showing the trajectory to the
#' existing plot. Assumes the points are two dimensional.
#'
#' @param trajectory A numeric matrix with two columns, each row is a step
#'                   in the trajectory.
#' @param color      Optional color index for the trajectory curve
#' @param char       Optional plot character for the starting point
#' @return None
#'
#' @author Christopher R. Genovese
plot_trajectory_curve2d <- function(trajectory, color=1, char=20) {
    points(trajectory[1, 1], trajectory[1, 2], pch=char)
    matlines(trajectory[, 1], trajectory[, 2], col=color)
}


#' Plot a collection of two-dimensional trajectories simultaneously
#'
#' Plots given trajectories as curves over a region that contains
#' all of the curves. Currently does not allow configuration of the
#' graphical elements.
#'
#' @param trajectories Array object returned by \code{mean_shift_trajectories}; each row is a step
#' @param colors     Optional vector of color indices for trajectory curves,
#'                   used cyclically
#' @param char       Optional plot character for the starting point
#' @return None
#'
#' @author Christopher R. Genovese
plot_trajectories <- function(trajectories, colors=1, char=20) {
    n_colors <- length(colors)

    plot(range(trajectories[,1,1]), range(trajectories[,2,1]),
         type='n', xlab="x", ylab="y")

    color_index <- 1
    for( step in 1:nrow(trajectories) ) {
        plot_trajectory_curve2d(get_trajectory(trajectories, step),
                                color=colors[color_index])
        color_index <- 1 + (color_index %% n_colors)
    }
}
