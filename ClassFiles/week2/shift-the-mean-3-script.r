# Script to run mean shift on a random data set

source("shift-the-mean-3.r") # ATTN: library() when mean-shift is a package


# Generate random data set and compute trajectories for spherical normal kernel
# ATTN Q: Are these names well chosen?

n  <- 200
S  <- matrix(c(rnorm(n, 2,  1),  rnorm(n,  -1,  1)),  n,  2)
T  <- cbind(runif(50, 0, 4), runif(50, -3, 1))
h  <- 1.06 * sd(as.vector(S)) * n^-0.2       # normal reference rule for bandwidth
K  <- function(x) dnorm(x[1], 0, h) * dnorm(x[2], 0, h)

trajectories <- mean_shift_trajectories(data=S, start_at=T, kernel=K, steps=15)

plot_trajectories(trajectories, colors=1:7)

# ATTN: make objects and functions/methods to represent and act upon
#       the trajectories, for instance using generic plot


