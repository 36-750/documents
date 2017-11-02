import psycopg2

conn = psycopg2.connect(host="sculptor.stat.cmu.edu", database="yourusername",
                        user="yourusername", password="yourpassword")

cur = conn.cursor()

cur.execute("INSERT INTO foo (bar, baz, spam) "
            "VALUES (17, 'walrus', 'penguin')")

cur.execute("SELECT * FROM events")

# iterating:
for row in cur:
    print(row)

# instead, one at a time:
row = cur.fetchone()

