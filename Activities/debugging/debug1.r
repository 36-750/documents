#
# binary search
# O(log n) time algorithm for finding a target in a sorted array.
#
# Returns an index in 1..n if found,  n+1 if not
#

binarySearch <- function(a, target) {
    n <- length(a)
    lo <- 1
    up <- n

    while(TRUE) {
        index <- (lo + up)/2
        if( target < a[index] ) {
            up <- index - 1
        } else {
            lo <- index + 1
        }
        if ( lo > up || target == a[index] ) {
            break
        }
    }

    return( lo <= up && index )
}


# bisect
# Find the largest t such that f(t) < 0
#
bisect <- function(f) {
    hi <- Inf
    lo <- 0
    while( hi != lo ) {
        mid <- (lo + hi)/2
        if( f(mid) > 0 ) {
            hi <- mid
        } else {
            lo <- mid
        }
    }
    return( hi )
}
