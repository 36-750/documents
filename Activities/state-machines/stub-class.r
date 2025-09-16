library(S7)  # See https://rconsortium.github.io/S7/articles/generics-methods.html and related links

build <- new_generic("build")
# ...


private_StateMachine <- new_class("StateMachine",
    properties = list(
        #... names map to class or a new_property call with class and e.g., defaults
    ),
    validator = function(self) {
        #...
    }
)


StateMachineBuilder <- new_class("StateMachineBuilder",
    properties = list(
        #...
    ),
    validator = function(self) {
        #...
    }
)

method(build, StateMachineBuilder) <- function() {
    # ...
}


# ...

