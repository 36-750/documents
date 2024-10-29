

Stack <- setClass("Stack", slots=c(items="list"))
setGeneric("push", function(stack, item) { standardGeneric("push") })

setMethod("push", "Stack", function(stack,  item) {
              n <- length(stack@items)
              # ...
              stack@items[[n+1]] <- item
              return(stack)
          })

