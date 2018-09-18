# Fast Object Sets

init <- function(n) {
    return(list(parent=1:n, size=rep(1, n)))
}

root <- function(fos,  id) {
    while ( fos$parent[id] != id ) {
        fos$parent[id] = fos$parent[fos$parent[id]]
        id = fos$parent[id]
    }
    return(list(root=id, fos=fos))
}

tworoots <- function(fos, id1, id2) {
    update <- root(fos,  id1)
    root1 <- update$root
    update <- root(update$fos, id2)
    root2 <- update$root
    fos <- update$fos
    return(list(fos=fos, root1=root1, id1=id1, root2=root2, id2=id2))
}

find <- function(fos, id1, id2) {
    u <- tworoots(fos, id1, id2)
    return(list(fos=u$fos, edge=c(id1, id2), found=(u$root1 == u$root2)))
}

union <- function(fos, id1, id2) {
    u <- tworoots(fos, id1, id2)
    fos <- u$fos
    if ( fos$size[u$root1] < fos$size[u$root2] ) {
        fos$parent[u$root1] <- u$root2
        fos$size[u$root2] <- fos$size[u$root2] + fos$size[u$root1]
    } else {
        fos$parent[u$root2] <- u$root1
        fos$size[u$root1] <- fos$size[u$root1] + fos$size[u$root2]
    }
    return(fos)
}


