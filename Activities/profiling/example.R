source("hw4-poisson.R")
load("poisLogBarrier.RData")

Rprof("profiling.out")
p <- barrier.method(pois.barrier.obj(count, X, belief.lower, belief.upper),
                    pois.barrier.grad(count, X, belief.lower, belief.upper),
                    pois.barrier.hess(count, X, belief.lower, belief.upper),
                    1000, find.x0(X, belief.lower, belief.upper),
                    5, 0.5, 0.9, 2, 1e-16, 1e-6)
Rprof(NULL)



summaryRprof("profiling.out")

## Call graph with the prof.tree package

# library(prof.tree)
#  
# prof.tree("profiling.out")

## Interactive with profvis

library(profvis)

profvis({
    p <- barrier.method(pois.barrier.obj(count, X, belief.lower, belief.upper),
                        pois.barrier.grad(count, X, belief.lower, belief.upper),
                        pois.barrier.hess(count, X, belief.lower, belief.upper),
                        1000, find.x0(X, belief.lower, belief.upper),
                        5, 0.5, 0.9, 2, 1e-16, 1e-6)
})
