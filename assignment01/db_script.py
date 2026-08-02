import sqlite3

con = sqlite3.connect("assignment01/tasks.db")
cur = con.cursor()

# create "tasks" table

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY,
    title TEXT,
    done BOOLEAN
)
""")

# seed 3 example tasks

cur.execute("SELECT COUNT(*) FROM tasks")

count = cur.fetchone()[0]

if count == 0:
    data = [
        ("First task", False),
        ("Second task", False),
        ("Third task", False)
    ]
    cur.executemany("INSERT INTO tasks(title, done) VALUES (?, ?)", data)

con.commit()
con.close()