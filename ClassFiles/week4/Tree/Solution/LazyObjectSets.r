# Lazy Object Sets

init <- function(n) {
    return(1:n)
}

root <- function(parent, id) {
    while ( parent[id] != id ) {
        id = parent[id]
    }
    return(id)
}

find <- function(parent, id1, id2) {
    return(root(parent, id1) == root(parent, id2))
}

union <- function(parent, id1, id2) {
    parent[root(parent, id1)] = root(parent, id2)
    return(parent)
}


