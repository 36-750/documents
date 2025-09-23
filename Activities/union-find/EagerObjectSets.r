# Eager Object Sets

EagerObjectSets <- function(n) {
    return(1:n)
}

representative<- function(roots, id1) {
    return(roots[id1])
}

connected <- function(roots, id1, id2) {
    return(roots[id1] == roots[id2])
}

union <- function(roots, id1, id2) {
    root1 <- roots[id1]
    root2 <- roots[id2]
    for ( id in 1:length(roots) ) {
        if ( roots[id] == root1 ) {
            roots[id] <- root2
        }
    }
    return(roots)
}


