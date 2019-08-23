# 
# ATTN: Edit documentation
# Shift that mean (ATTN: non-glib purpose)
# See Cheng 1995 for details  (ATTN: authoritative citation)

#-----------------------
# Entities: Data points, evaluation points, input parameters,
#           evolution of the evaluation points under the operation

# For each iteration
#     For each evaluation point
#        Compute weighed average with respect to the data
#        Record each weighted average by its iteration
#-----------------------

kernel_weighted_average <- function(evaluation_point, data, kernel, weights) {
    numerator <- rep(0.0, length(evaluation_point))
    denominator <- 0.0

    for ( index in 1:nrow(data) ) {
        kernel_value <- kernel(evaluation_point - data[index, ])
        numerator <- numerator + kernel_value * weight[index] * data[index, ]
        denominator <- denominator + kernel_value * weight[index]
    }

    return(numerator/denominator)
}    

mean_shift <- function(data, evaluation_points, kernel, weights, iterations) {
    trajectories <- array(0, dim=c(nrow(evaluation_points), ncol(evaluation_points),
                                   iterations+1))
    trajectories[,,1] <- evaluation_points
                 
    for( iteration in 1:iterations ) {
        for( eval_pt_index in 1:nrow(T) ) {
            eval_pt = trajectories[eval_pt_index,,iteration]
            trajectories[eval_pt_index, , iteration+1] <-
                kernel_weighted_average(eval_pt, data, kernel, weights)
        }
    }

    return( trajectories )
}    


# Script to run mean shift on a random data set

S <- matrix(c(rnorm(200, 2,  1),  rnorm(200,  -1,  1)),  200,  2)
T <- cbind(runif(50, 0, 4), runif(50, -3, 1))
h0 <- 1.06 * sd(as.vector(S)) * 200^-0.2
K <- function(x) dnorm(x[1], 0, h0) * dnorm(x[2], 0, h0)
w = rep(1, 200)

mean_shift(data=S, evaluation_pionts=T, kernel=K, weights=w, iterations=its)


# ATTN: make functions (or objects) to handle the trajectories
plot(range(T[, 1]), range(T[, 2]), type='n', xlab="x", ylab="y")
points(T[, 1], T[, 2], pch=20)
co <- 1
for( i in 1:nrow(results ) )
    {
        matlines(results[i, 1, ], results[i, 2, ],  col=co)
        co <- 1 + (co %% 7)
    }


