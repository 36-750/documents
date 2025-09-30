# Graph CC in R

library(S7)

Graph <- new_class("Graph",
                   properties =  list(
                       nodes =  class_numeric,
                       edges =  class_numeric
                   )
         )

