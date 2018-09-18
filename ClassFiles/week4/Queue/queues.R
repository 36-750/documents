#!/usr/bin/env Rscript

empty_queue_error <- function(msg, call=sys.call(-1), ...) {
    structure(
        class=c("empty_queue", "error", "condition"),
        list(message=msg, call=call),
        ...
    )
}

## Some examples:
## foo <- Queue()
## foo$enqueue(4)
## foo$dequeue()  #=> 4
## foo$is_empty() #=> TRUE

Queue <- setRefClass(
    "Queue",
    fields=c("queue"),
    methods=list(
        initialize=function() {
            queue <<- list()
        },

        dequeue=function() {
            if (is_empty()) {
                stop(empty_queue_error("Attempt to dequeue an empty queue"))
            }

            val <- queue[[1]]
            queue <<- queue[-1]
            return(val)
        },

        enqueue=function(obj) {
            queue <<- c(queue, obj)
        },

        peek=function() {
            return(queue[[1]])
        },

        is_empty=function() {
            return(length(queue) == 0)
        }
    )
)

## Examples:
## foo <- PoissonProcss(lam=4)
## foo$latest()
## foo$next_event()
PoissonProcess <- setRefClass(
    "PoissonProcess",
    fields=list(lam="numeric", xlatest="numeric"),
    methods=list(
        initialize=function(lam) {
            lam <<- lam
            xlatest <<- interarrival()
        },

        latest=function() {
            return(xlatest)
        },

        interarrival=function() {
            return(rexp(1, rate=lam))
        },

        next_event=function() {
            xlatest <<- xlatest + interarrival()
        }
    )
)

find_next_event <- function(events) {
    minimum <- Inf
    which <- 0
    index <- 0

    for (ind in seq_along(events)) {
        if (events[[ind]]$latest() < minimum) {
            minimum <- events[[ind]]$latest()
            which <-  events[[ind]]
            index <- ind
        }
    }
    return(list(next_service=which, next_index=ind))
}

MMkGroceryQueue <- setRefClass(
    "MMkGroceryQueue",
    fields=c("num_servers", "lambda_arrival", "lambda_serve",
             "servers", "arrival", "station", "queues", "time", "served",
             "total_waiting_time"),

    methods=list(
        initialize=function(nqueues, lambda_arrival, lambda_serve) {
            num_servers <<- nqueues
            lambda_arrival <<- lambda_arrival
            lambda_serve <<- lambda_serve

            servers <<- lapply(seq_len(nqueues),
                               function(arg) {
                                   return(PoissonProcess(lambda_serve))
                               })
            arrival <<- lapply(seq_len(nqueues),
                               function(arg) {
                                   return(PoissonProcess(lambda_arrival))
                               })
            station <<- numeric(nqueues)  # entry time into the service station
            queues <<- lapply(seq_len(nqueues),
                              function(arg) { return(Queue())})

            time <<- 0.0
            served <<- 0
            total_waiting_time <<- 0.0
        },

        step=function() {
            ########
            ## ATTN TO BE IMPLEMENTED
            ########

            return(time)
        },

        run_until=function(time_limit) {
            step()
            while (time < time_limit) {
                step()
            }
        },

        average_waiting_time=function() {
            if (served > 0) {
                return(total_waiting_time / served)
            }
            return(NA)
        }
    )
)

MMkBankQueue <- setRefClass(
    "MMkBankQueue",
    fields=c("num_servers", "lambda_arrivals", "lambda_serve",
             "servers", "arrivals", "station", "queue", "time", "served",
             "total_waiting_time"),

    methods=list(
        initialize=function(nservers, lambda_arrivals, lambda_serve) {
            num_servers <<- nservers
            lambda_arrivals <<- lambda_arrivals
            lambda_serve <<- lambda_serve

            servers <<- lapply(seq_len(nservers),
                               function(arg) {
                                   return(PoissonProcess(lambda_serve))
                               })
            arrivals <<- PoissonProcess(lambda_arrivals)
            station <<- rep(NA, num_servers)  # entry time into the service station
            queue <<- Queue()

            time <<- 0.0
            served <<- 0
            total_waiting_time <<- 0.0
        },

        step=function(debug=FALSE) {
            n <- find_next_event(servers)

            ## Forward event times for empty servers triggering before next
            ## arrival
            while(n$next_service$latest() < arrivals$latest() && is.na(station[n$next_index])) {
                n$next_service$next_event()
                n <- find_next_event(servers)
            }

            if (arrivals$latest() < n$next_service$latest()) {
                time <<- arrivals$latest()

                arrivals$next_event()

                if (all(!is.na(station))) {
                    queue$enqueue(time)
                } else {
                    for (ii in seq_len(num_servers)) {
                        if (is.na(station[ii])) {
                            station[ii] <<- time
                            break
                        }
                    }
                }
            } else {
                time <<- n$next_service$latest()

                entry_time <- station[n$next_index]
                waiting_time <- time - entry_time

                served <<- served + 1
                total_waiting_time <<- total_waiting_time + waiting_time

                if (queue$is_empty()) {
                    station[n$next_index] <<- NA
                } else {
                    station[n$next_index] <<- queue$dequeue()
                }
            }

            if (debug) {
                print(time)
            }

            return(time)
        },

        run_until=function(time_limit) {
            step()
            while (time < time_limit) {
                step()
            }
        },

        average_waiting_time=function() {
            if (served > 0) {
                return(total_waiting_time / served)
            }
            return(NA)
        },

        report=function() {
            cat("Served ", served, ", avg wait ", average_waiting_time(),
                ", time ", time, "\n", sep="")
        }
    )
)

bank <-  MMkBankQueue(10, 1.0, 0.001)
bank$run_until(600.0)
bank$report()
