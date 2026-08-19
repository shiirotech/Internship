from dotenv import load_dotenv
import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_timestamp() -> str:
    return datetime.now().replace(microsecond=0)


class PostgresTaskRepository:

    def db_status(self) -> str:
        try:
            with psycopg.connect(DATABASE_URL) as con:
                with con.cursor() as cur:
                    cur.execute("SELECT 1")
                    return "ok"
        except psycopg.OperationalError:
            return "bad"

    def read_tasks(
        self,
        done: bool | None = None,
        search: str | None = None,
        sort: str | None = None
    ) -> list[dict]:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:
        
                query = "SELECT * FROM tasks"
                conditions = []
                params = []
        
                if done is not None:
                    conditions.append("done = %s")
                    params.append(done)
        
                if search and search.strip():
                    search = search.strip()
                    conditions.append("title ILIKE %s")
                    params.append(f"%{search}%")
        
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
        
                if sort and sort.strip():
                    sort = sort.strip().lower()
                    if sort == "title":
                        query += " ORDER BY title"
                    elif sort == "-title":
                        query += " ORDER BY title DESC"
                    elif sort == "id":
                        query += " ORDER BY id"
                    elif sort == "-id":
                        query += " ORDER BY id DESC"
                    else:
                        raise ValueError(
                            "Unable to sort using current parameter"
                        )
        
                rows = cur.execute(query, params).fetchall()
        
        return rows


    def read_task(self, task_id: int) -> dict | None:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:
        
                row = cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,)).fetchone()
        
        return row


    def read_stats(self) -> dict:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:

                total = cur.execute(
                    "SELECT COUNT(*) FROM tasks"
                ).fetchone()["count"]

                count_done = cur.execute(
                    "SELECT COUNT(*) FROM tasks WHERE done = %s",
                    (True,)
                ).fetchone()["count"]

                count_open = total - count_done

        return {
            "total": total,
            "done": count_done,
            "open": count_open
        }


    def create_task(self, title: str) -> dict:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:

                now = get_timestamp()

                cur.execute(
                    """
                    INSERT INTO tasks(title, done, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                    """,
                    (title, False, now, now)
                )

                row = cur.fetchone()

        return row


    def reset_tasks(self) -> list[dict]:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:

                cur.execute("TRUNCATE TABLE tasks RESTART IDENTITY")

                now = get_timestamp()
                
                cur.execute(
                    """
                    INSERT INTO tasks(title, done, created_at, updated_at)
                    VALUES
                        (%s, %s, %s, %s),
                        (%s, %s, %s, %s),
                        (%s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        "First task", False, now, now,
                        "Second task", False, now, now,
                        "Third task", False, now, now
                    )
                )

                rows = cur.fetchall()

        return rows


    def update_task(self, task_id: int, data: dict) -> dict | None:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:

                updates = []
                params = []

                if "title" in data:
                    updates.append("title = %s")
                    params.append(data["title"])

                if "done" in data:
                    updates.append("done = %s")
                    params.append(data["done"])

                now = get_timestamp()

                updates.append("updated_at = %s")
                params.append(now)

                params.append(task_id)

                query = (
                    "UPDATE tasks SET " +
                    ", ".join(updates) +
                    " WHERE id = %s"
                    " RETURNING *"
                )
                
                cur.execute(query, params)
        
                row = cur.fetchone()
        
        return row


    def delete_task(self, task_id: int) -> None:
        with psycopg.connect(DATABASE_URL) as con:
            with con.cursor() as cur:

                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))

                if cur.rowcount == 0:
                    raise ValueError(
                        f"Task {task_id} not found"
                    )