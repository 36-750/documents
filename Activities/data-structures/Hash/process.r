library("stringr")
library("magrittr")

## Simple Hash Table Implementation mapping strings to R objects

#' Creates an empty hash table
#' 
#' Operations:
#'  - Read values with lookup() or [[ ]].
#'  - Insertion by assigning to hashmap[[key]].
#'  - keys() gives all keys
#'  - inspect() at the repl shows all keys and values
#'  - contains() checks if a key exists
#'  - delete() removes keys
#'  
#' 
stringHashMap <- function(size=7919L) {
    return( new.env(hash=TRUE, size=size) )
}

keys <- function(hashmap) {
    return( ls(hashmap, all.names=TRUE) )
}

inspect <- function(hashmap) {
    return( ls.str(hashmap, all.names=TRUE) )
}

contains <- function(hashmap, key) {
    return( exists(key, envir=hashmap, inherits=FALSE) )
}    

lookup <- function(hashmap, key, default=NULL) {
    if ( contains(hashmap, key) ) return( hashmap[[key]] )
    return( default )
}

delete <- function(hashmap, key) {
    rm(key, envir=hashmap)
}


## Processing text from inputs sources

tokenize <- function(line) {
    line %>%
        str_extract_all("([A-Za-z][-A-Za-z]+)") %>%
        unlist %>%
        sapply(tolower) %>%
        as.character
}

#' Read next line from connection and apply processing function
#' @param con       -- open connection
#' @param processor -- function taking a character vector, should
#'                     accept the empty string
#'
#' @return result of processing function on the given line
processByLine <- function(con, processor) {
    line <- readLines(con, n=1)
    if ( length(line) == 0 ) return( NULL )
    return( processor(line) )
}

#' Perform action while safely opening and closing a connection
#'
#' Examples:
#'   - withReadConnection(file("foo"), function(con) {readLines(con, n=4)})
#'   - withReadConnection(file("foo"), nGramFrequency, n=2)
#' 
withReadConnection <- function(connection, action, ...) {
    open(connection, "r")
    on.exit(close(connection))
    return( action(connection, ...) )
}    

#' Generates a unique string from a given ngram
#'
#' @param ngram -- a vector of strings
#'
#' @return string that uniquely combines all the strings in ngram
nGramKey <- function(ngram) {
    paste(ngram, sep="", collapse="+")
}

#' Returns generator function for reading next ngram from connection
#'
#' @param con -- an open connection
#' @param n   -- order of the ngrams being computed
#'
#' @return function that produces successive ngrams from \code{con}.
#' 
#' In the retunred function Text on the connection is tokenized and n
#' successive words combined to an ngram key, with the window shifting
#' each time by 1 word.
nGramGenerator <- function(con, n=1) {
    line <- processByLine(con, tokenize)
    token_number <- 1

    if ( is.null(line) ) { # input is empty, no ngrams
        return( function() { return( NULL ) } )
    }
    
    return( function() {
                # Note: length(NULL) == 0
                while ( length(line) < token_number + n - 1 ) {
                    rest <- processByLine(con, tokenize) # add more tokens
                    if ( is.null(rest) ) return( NULL )  # < n tokens remain
                    line <<- c(line, rest)
                }
                # Create the ngram key then shift the window forward by one
                # token. Ex: when n = 2, A B C... -> key(A,B), key(B,C), ....
                index <- token_number
                token_number <<- token_number + 1
                return( nGramKey(line[index:(index + n - 1)]) )
            } )
}


## Main User Entry Points

#' Generates frequency distribution of ngrams from a given text source
#'
#' @param con -- an open connection (e.g., to a file, url)
#' @param n   -- the order of the word ngrams collected from the file
#'
#' For example, a string "all good folks know" has ngrams for n=2
#' "all+good", "good+folks", and "folks+know"; for n=1, each word
#' is an n-gram. This function reads text from the connection, tokenizes
#' it, and computes ngram frequencies.
#'
#' @return a hashtable (see \code{stringHashMap()} and related
#'     functions) mapping ngrams in the text to the number of times the
#'     ngram appears. This object has attributes "order" which is equal
#'     to n and "total" which equals the total number of non-unique
#'     n-grams to appear in the text.
#'
nGramFrequency <- function(con, n=1) {
    ngramCounts <- stringHashMap()
    total       <- 0
    nextNGram   <- ATTN:FILLIN

    ATTN:FILLIN

    attr(ngramCounts, "order") <- n
    attr(ngramCounts, "total") <- total
    return( ngramCounts )
}

#' Finds the n-grams common to two text sources
#'
#' @param ngramCounts1 -- Frequency tables from two text sources as
#' @param ngramCounts2    produced by \code{nGramFrequency()}.
#' 
#' @return list of ngram keys for ngrams common to the two sources
#' Includes attributes giving the total and unique n-gram counts
#' for the two sources and the number of overlapping (non-unique) ngrams.
#' 
nGramIntersection <- function(ngramCounts1, ngramCounts2) {
    ngrams12 <- stringHashMap()
    if ( attr(ngramCounts1,"order") != attr(ngramCounts2,"order") ) {
        return( keys(ngrams12) )
    }

    overlap <- 0
    for ( ngram in keys(ngramCounts1) ) {
        if ( contains(ngramCounts2, ngram) ) {
            mincount <- min(ngramCounts1[[ngram]], ngramCounts2[[ngram]])
            ngrams12[[ngram]] <- mincount
            overlap <- overlap + mincount
        }
    }

    intersect <- keys(ngrams12)
    attr(intersect, "counts") <- list(total1=attr(ngramCounts1,"total"),
                                      total2=attr(ngramCounts2,"total"),
                                      overlap=overlap,
                                      unique1=length(keys(ngramCounts1)),
                                      unique2=length(keys(ngramCounts2)))
    return( intersect )
}

