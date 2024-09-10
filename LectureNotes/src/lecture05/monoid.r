setClass("Monoid")
setGeneric("munit", function(monoid) { standardGeneric("munit") })
setGeneric("mdot", function(monoid, x, y) { standardGeneric("mdot") })

munit <- function(monoid, ...)             # S3 generic for S3 dispatch
    UseMethod("munit")
setGeneric("munit")                        # S4 generic for S4 dispatch, default is S3 generic
munit.Monoid <- function(monoid, ...) {}   # S3 method for S3 class
setMethod("munit", "Monoid", munit.Monoid) # S4 method for S4 class

SumM <- setClass("SumM", contains="Monoid")
Sum <- SumM()
setMethod("munit", signature("SumM"), function(monoid) 0)
setMethod("mdot", signature("SumM", "numeric", "numeric"), function(monoid, x, y) x + y)
