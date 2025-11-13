fib <- function(n) {
    r <- rep(0,  n)

    r[1] <- 0
    r[2] <- 1

    for( i in 3:n ) {
        r[i] <- r[i - 1] + r[i - 2]
    }
    return( r[n] )
}
