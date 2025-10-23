lazy_seq <- function(f) {
    return list(realized=list(), fn=f)
}

iterate <- function(f, x) {
    lazy <- lazy_seq(f)
    lazy$realized <- list(x)
}

