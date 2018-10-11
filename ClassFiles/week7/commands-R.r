library(RPostgreSQL)

con <- dbConnect(PostgreSQL(), user="yourusername", password="yourpassword",
                 dbname="yourusername", host="pg.stat.cmu.edu")

result <- dbSendQuery(con, "SELECT persona, score FROM events WHERE ...")

data <- dbFetch(result) # load all data

data <- dbFetch(result, n=10) # load only ten rows

dbClearResult(result)

