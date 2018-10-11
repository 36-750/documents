## Psycopg2 is the best Python package for accessing PostgreSQL databases. Its
## documentation is available here: http://initd.org/psycopg/docs/

import psycopg2

conn = psycopg2.connect(host="sculptor.stat.cmu.edu", database="yourusername",
                        user="yourusername", password="yourpassword")

cur = conn.cursor()

## See README.org for info on "Safe SQL". NEVER insert data into SQL queries by
## concatenating strings together. ALWAYS use parametrized queries, like the one
## below.
new_baz = "walrus"
new_spam = "penguin"

cur.execute("INSERT INTO foo (bar, baz, spam) "
            "VALUES (17, %(baz)s, %(spam)s)",
            {"baz": new_baz, "spam": new_spam})

cur.execute("SELECT * FROM events")

# iterating:
for row in cur:
    print(row)

# instead, one at a time:
row = cur.fetchone()
