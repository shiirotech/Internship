import sqlite3
from datetime import datetime

con = sqlite3.connect("assignment01/tasks.db")
cur = con.cursor()

# create "tasks" table

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY,
    title TEXT,
    done BOOLEAN,
    created_at TEXT,
    updated_at TEXT
)
""")

# seed 3 example tasks

cur.execute("SELECT COUNT(*) FROM tasks")

count = cur.fetchone()[0]

if count == 0:
    now = datetime.now().replace(microsecond=0).isoformat()

    data = [
        ("First task", False, now, now),
        ("Second task", False, now, now),
        ("Third task", False, now, now)
    ]

    cur.executemany(
        """INSERT INTO tasks(title, done, created_at, updated_at)
        VALUES (?, ?, ?, ?)""", data
    )

con.commit()
con.close()