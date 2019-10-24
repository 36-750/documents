## Gradient descent for a Poisson log-likelihood with barrier method for
## constraints.
## Alex Reinhart

library(lpSolve)
library(Matrix)

newton <- function(objective, grad, hess, x0, alpha, beta,
                   eps, max.iter=100) {
    obj.prev <- objective(x0)
    x.prev <- x0

    for (ii in seq_len(max.iter)) {
        step.size <- 1

        v <- -1 * solve(hess(x.prev)) %*% grad(x.prev)
        grad.prev <- t(grad(x.prev))

        while (objective(x.prev + step.size * v) >
               obj.prev + alpha * step.size * grad.prev %*% v) {
            step.size <- beta * step.size
        }
        x.prev <- x.prev + step.size * v

        if (abs(objective(x.prev) - obj.prev)/abs(obj.prev) <= eps) {
            break
        }
        obj.prev <- objective(x.prev)
    }
    return(x.prev)
}

barrier.method <- function(objective, grad, hess, m, x0, t.0, alpha,
                           beta, mu, eps.inner, eps.outer) {
    cur.sol <- newton(objective(t.0), grad(t.0), hess(t.0), x0,
                      alpha, beta, eps.inner)

    while (m / t.0 > eps.outer) {
        t.0 <- mu * t.0
        cur.sol <- newton(objective(t.0), grad(t.0), hess(t.0), cur.sol,
                          alpha, beta, eps.inner)
    }
    return(cur.sol)
}

# From problem 2(a)
pois.obj <- function(y, X) {
    function(beta) {
        sum(exp(X %*% beta) - y * X %*% beta)
    }
}

# To simplify, I'll do the ordinary objective function's gradient and
# Hessian, then add in the contributions from the barrier term.
pois.grad <- function(y, X) {
    function(beta) {
        t(X) %*% (exp(X %*% beta) - y)
    }
}

pois.hess <- function(y, X) {
    function(beta) {
        W <- diag(drop(exp(X %*% beta)))
        t(X) %*% W %*% X
    }
}

# These functions are curried so that we can fix the boundary
# parameters, then fix t.0 to pass to Newton's method.
pois.barrier.obj <- function(y, X, lower, upper) {
    obj <- pois.obj(y, X)
    function(t.0) {
        function(beta) {
            xb <- X %*% beta

            # If beta is not feasible, return Inf, so that Newton's
            # method is forced to backtrack to a feasible point.
            if (any(xb - lower <= 0) || any(upper - xb <= 0)) {
                return(Inf)
            }
            t.0 * obj(beta) - sum(log(xb - lower)) -
                sum(log(upper - xb))
        }
    }
}

pois.barrier.grad <- function(y, X, lower, upper) {
    grad <- pois.grad(y, X)
    cX <- colSums(X)
    function(t.0) {
        function(beta) {
            g <- t.0 * grad(beta)
            for (ii in seq_len(nrow(X))) {
                g <- g + X[ii,] / drop(lower[ii] - t(X[ii,]) %*% beta)
                g <- g - X[ii,] / drop(t(X[ii,]) %*% beta - upper[ii])
            }
            return(g)
        }
    }
}

pois.barrier.hess <- function(y, X, lower, upper) {
    hess <- pois.hess(y, X)
    function(t.0) {
        function(beta) {
            h <- t.0 * hess(beta)
            for (ii in seq_len(nrow(X))) {
                h <- h + (X[ii,] %*% t(X[ii,])) /
                    drop(lower[ii] - t(X[ii,]) %*% beta)**2
                h <- h + (X[ii,] %*% t(X[ii,])) /
                    drop(t(X[ii,]) %*% beta - upper[ii])**2
            }
            return(h)
        }
    }
}

# adapted from homework 3
find.x0 <- function(X, lower, upper) {
    rows <- nrow(X)
    cols <- ncol(X)
    f.con <- rBind(X, X)
    f.obj <- rep(0, ncol(f.con))
    f.dir <- c(rep(">=", rows), rep("<=", rows))
    f.rhs <- c(lower + 0.01, upper - 0.01)

    # black magic
    d.con <- as.matrix(summary(as(f.con, "dgTMatrix")))

    lp("min", f.obj, , f.dir, f.rhs, dense.const=d.con)$solution
}
