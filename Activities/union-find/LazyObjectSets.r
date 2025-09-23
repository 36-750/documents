# Lazy Object Sets

LazyObjectSet <- function(n) {
    return(1:n)
}

representative <- function(parent, id) {
    while ( parent[id] != id ) {
        id = parent[id]
    }
    return(id)
}

connected <- function(parent, id1, id2) {
    # ATTN IMPLEMENT THIS (hint: one liner)
}

union <- function(parent, id1, id2) {
    # ATTN IMPLEMENT THIS
    return(parent)
}

