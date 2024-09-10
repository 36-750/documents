setClass("hyperreal", slots = c(x = "numeric", dx = "numeric"))

hyper <- function(x, dx) {
  new("hyperreal", x = x, dx = dx)
}

setMethod("+", signature(e1 = "hyperreal", e2 = "hyperreal"),
          function(e1, e2) {
              hyper(e1@x + e2@x, e1@dx + e2@dx)
          })

setMethod("+", signature(e1 = "hyperreal", e2 = "numeric"),
          function(e1, e2) {
              hyper(e1@x + e2, e1@dx)
          })

# ... 


# Example

foo <- function(x) {
    sin(x)^2 + 3*x^2 + log(x) - 4
}

# > foo(4)
# [1] 45.95904
#
# > foo(hyper(4, 1))
# An object of class "hyperreal"
# Slot "x":
# [1] 45.95904
#
# Slot "dx":
# [1] 25.23936
