## RPostgreSQL is the R package to connect to PostgreSQL. Its documentation:
## https://cran.r-project.org/package=RPostgreSQL
library(RPostgreSQL)

con <- dbConnect(PostgreSQL(), user="yourusername", password="yourpassword",
                 dbname="yourusername", host="sculptor.stat.cmu.edu")

result <- dbSendQuery(con, "SELECT persona, score FROM events WHERE ...")

data <- dbFetch(result) # load all data

data <- dbFetch(result, n=10) # load only ten rows

dbClearResult(result)

## NEVER use paste() to put together SQL queries containing data. ALWAYS use
## sqlInterpolate, as shown here. See README.org for details.
username <- "Little Bobby Tables"
password <- "walruses"

query <- sqlInterpolate(con,
                        "SELECT * FROM users WHERE username = ?user AND password = ?pass",
                        user=username, pass=password)

users <- dbGetQuery(con, query)
