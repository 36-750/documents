
#######################
## Profiling example
##
## TASK: Review the code below. Try to figure out how Quicksort works, and come
## up with some suggestions to speed it up. Don't run it yet!
##
## Later we will profile this code to see what takes the most time.
#######################

## Quicksort is a divide-and-conquer algorithm for sorting vectors.
## https://en.wikipedia.org/wiki/Quicksort#Algorithm
##
## vec: a vector to be sorted
## indices: the indices of entries in the vector, e.g. 1:length(vec)
## Returns a new vector containing the entries in sorted order.
quicksort <- function(vec, indices) {
    low <- indices[1]
    high <- indices[length(indices)]

    if (low < high) {
        res <- partition(vec[1:length(vec)], indices)
        pivot <- res[[1]]
        vec <- res[[2]]

        vec <- quicksort(vec[1:length(vec)], low:(pivot - 1))
        vec <- quicksort(vec[1:length(vec)], (pivot + 1):high)
    }

    return(vec)
}

## partition finds a "pivot" value -- just the last entry in the sequence -- and
## partitions the vector, meaning that all elements smaller than the pivot
## appear first, followed by the pivot, followed by all elements larger than the
## pivot. The result isn't actually sorted yet, but we can partition the first
## half again, and so on, until the entire vector is sorted.
partition <- function(vec, indices) {
    low <- indices[1]
    high <- indices[length(indices)]
    pivot <- vec[high]

    ii <- low

    for (jj in low:(high - 1)) {
        if (vec[jj] < pivot) {
            if (ii !=  jj) {
                ## Swap the value in vec[ii] with the one in vec[jj]
                tmp <- vec[ii]
                vec[ii] <- vec[jj]
                vec[jj] <- tmp
            }
            ii <- ii + 1
        }
    }

    ## Swap the value in vec[high] (the pivot value) with the value in vec[ii],
    ## hence putting the pivot in the middle
    tmp <- vec[ii]
    vec[ii] <- vec[high]
    vec[high] <- tmp

    return(list(ii, vec))
}


#######################
## Example code. Don't run this yet!
#######################

data <- sample(1:100000, size=30000, replace=TRUE)

Rprof("profiling.out")

## This may take a minute or two -- reduce the size argument above if it takes
## too long. But you want it to take at least several seconds, so we can collect
## enough profiling data.
sorted <- quicksort(data, seq_along(data))

Rprof(NULL)

summaryRprof("profiling.out")

library(prof.tree)  # you may need to run install.packages("prof.tree") first
prof.tree("profiling.out") # handy, but not so good with recursive functions
