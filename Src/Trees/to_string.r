# to_string : Showable a => Tree a -> String

to_string <- function(tree, down = "(", sep = ", ", up = ")") {
    n <- length(tree)

    # for every element of the list
    #   if it's showable,  collect its string form
    #   otherwise collect to_string(element)

    emitted <- c()
    sep_char <- ""
    for ( i in 1:n ) {
        emitted <- c(emitted, sep_char)
        if ( is.list(tree[[i]]) ) {
            str_of_subtree <- to_string(tree[[i]])
            emitted <- c(emitted, down,  str_of_subtree,  up)
        } else {
            emitted <- c(emitted, as.character(tree[[i]]))
        }
        sep_char <- sep
    }
    return( str_c(emitted, collapse = "") )
}
