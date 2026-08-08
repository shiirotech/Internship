import psycopg
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

with psycopg.connect(DATABASE_URL) as con:
    with con.cursor() as cur:

        # create "tasks" table

        cur.execute("DROP TABLE IF EXISTS tasks")

        cur.execute("""
        CREATE TABLE tasks(
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        """)

        # seed 3 example tasks

        now = datetime.now().replace(microsecond=0).isoformat()

        data = [
            ("First task", False, now, now),
            ("Second task", False, now, now),
            ("Third task", False, now, now)
        ]

        cur.executemany(
            """
            INSERT INTO tasks(title, done, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            """,
            data
        )