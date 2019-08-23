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
    # ATTN IMPLEMENT THIS (hint: one liner)
}

union <- function(parent, id1, id2) {
    # ATTN IMPLEMENT THIS
    return(parent)
}


