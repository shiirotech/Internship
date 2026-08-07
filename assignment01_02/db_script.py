import psycopg
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

with psycopg.connect(DATABASE_URL) as con:
    with con.cursor() as cur:

        # create "tasks" table

        cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id SERIAL PRIMARY KEY,
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
                VALUES (%s, %s, %s, %s)""", data
            )