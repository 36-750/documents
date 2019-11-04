## A source file that makes the mean shift code crash in various ways.

source("shift-the-mean.r")

## Set up the data.
n <- 200
data <- matrix(c(rnorm(n, 2, 1),  rnorm(n, -1, 1)), n, 2)
start_pts <- cbind(runif(50, 0, 4), runif(50, -3, 1))

bandwidth <- 1.06 * sd(as.vector(data)) * n^-0.2  # normal reference rule for bandwidth
gaussian_kernel <- function(x) dnorm(x[1], 0, bandwidth) * dnorm(x[2], 0, bandwidth)

## First, let's show you what the code does when it's used correctly. Run this
## and look at the output.

trajectories <- mean_shift_trajectories(data = data, start_at = start_pts,
                                        kernel = gaussian_kernel, steps = 15)
plot_trajectories(trajectories)

## The lines you see are the trajectories, while the dots are the points in the
## start_at matrix. You can see that the trajectories all move toward one point
## in the middle, which is the maximum of the estimated density.

### Now, the bad stuff:

## There are several cases. Each case crashes for some reason. Determine the
## cause of the crash and add appropriate checks to shift-the-mean.r --
## assertions, error messages, whatever is needed -- so the case leads to an
## understandable error message that would be useful to a user.
##
## Once you've fixed one case, comment out the case and move to the next one.

## Case #1.
trajectories <- mean_shift_trajectories(data = data[1, ], start_at = start_pts,
                                        kernel = gaussian_kernel, steps = 15)

## Case #2.
boxcar_kernel <- function(x) { if (sum(abs(x)) < 0.00001) { 1 } else { 0 } }

trajectories <- mean_shift_trajectories(data = data, start_at = start_pts,
                                        kernel = boxcar_kernel, steps = 15)

## Case #3. It works, but... does it?
trajectories <- mean_shift_trajectories(data = data[, 1, drop=FALSE],
                                        start_at = start_pts,
                                        kernel = gaussian_kernel, steps = 15)

## Case #4.
trajectories <- mean_shift_trajectories(data = data, start_at = start_pts,
                                        kernel = gaussian_kernel, steps = 0)

## Case #5.
trajectories <- mean_shift_trajectories(data = cbind(data, data), start_at = start_pts,
                                        kernel = gaussian_kernel, steps = 15)
