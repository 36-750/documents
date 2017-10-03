library(stringr)

#' Computes the edit distance between two strings
#'
#' @param s1 -- a string
#' @param s2 -- a string
#'
#' @return the edit distance between the strings, 
#'         a non-negative integer
#' 
edit_distance <- function(s1, s2) {
    str1 <- unlist(strsplit(s1, ""))
    len1 <- length(str1)

    str2 <- unlist(strsplit(s2, ""))
    len2 <- length(str2)

    # The edit matrix naturally indexed from 0:len1, 0:len2,
    # so in R, we add 1 to the actual index to match.
    # Initialize to NA to make errors clearer.
    edit <- matrix(NA, len1+1, len2+1)

    # Q: What do these initializations mean?
    edit[,1] <- 0:len1
    edit[1,] <- 0:len2

    for( index1 in 2:(len1+1) ) {
        for( index2 in 2:(len2+1) ) {
            #ATTN:FIX
            edit[index1, index2] <- NA #ATTN:FIX
        }
    }

    return( edit[len1+1, len2+1])
}                     


gaps <- function(gap_length) {
    return( paste(rep("_", gap_length), collapse="") )
}

#' Computes the alignment and edit distance between two strings
#'
#' @param s1 -- a string
#' @param s2 -- a string
#'
#' @return a list with two attributes:
#'           - distance  :: the edit distance between the strings,
#'           - alignment :: a pair of strings with '_' characters placed between them
#' 
edit_alignment <- function(s1, s2) {
    str1 <- unlist(strsplit(s1, ""))
    len1 <- length(str1)

    str2 <- unlist(strsplit(s2, ""))
    len2 <- length(str2)

    # The edit matrix naturally indexed from 0:len1, 0:len2,
    # so in R, we add 1 to the actual index to match.
    # Initialize to NA to make errors clearer.
    edit <- matrix(NA, len1+1, len2+1)
    align <- array("", c(len1+1, len2+1, 2))

    # Q: What do these initializations mean?
    edit[,1] <- 0:len1
    edit[1,] <- 0:len2

    align[1,1,] <- ""
    for ( i in 2:(len1+1) ) {
        align[i, 1, 1] <- "NA" #ATTN:FIX  (hint: you can use str_sub or substring)
        align[i, 1, 2] <- gaps(i-1)
    }
    for ( j in 2:(len2+1) ) {
        align[1, j, 1] <- "NA" #ATTN:FIX
        align[1, j, 2] <- "NA" #ATTN:FIX
    }

    for( index1 in 2:(len1+1) ) {
        for( index2 in 2:(len2+1) ) {
            #ATTN:FIX

            edit[index1, index2] <- NA #ATTN:FIX

            if ( TRUE ) { #ATTN:FIX
                align[index1, index2, 1] <- str_c("NA", "NA") #ATTN:FIX
                align[index1, index2, 2] <- str_c("NA", "NA") #ATTN:FIX
            } else if ( TRUE ) { #ATTN:FIX
                align[index1, index2, 1] <- str_c("NA", "NA") #ATTN:FIX
                align[index1, index2, 2] <- str_c("NA", "NA") #ATTN:FIX
            } else {
                align[index1, index2, 1] <- str_c("NA", "NA") #ATTN:FIX
                align[index1, index2, 2] <- str_c("NA", "NA") #ATTN:FIX
            }
        }
    }

    return( list(distance=edit[len1+1, len2+1], alignment=align[len1+1,len2+1,]) )
}                     
